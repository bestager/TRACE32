"""
기사 원문 스크래퍼 모듈 (v2 - 최적화 통합 버전)
- 멀티 백엔드 추출 체인: trafilatura → readability-lxml → BeautifulSoup
- 동시 수집 (ThreadPoolExecutor)
- 품질 스코어링 및 중복 제거
- 한글/영문 균형 수집
- 네이버 뉴스 / 구글 뉴스 RSS 지원
"""

import hashlib
import logging
import re
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import requests
import trafilatura
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDocument

from .sources import (
    FETCH_DELAY,
    GOOGLE_NEWS_RSS,
    KEYWORDS_EN,
    KEYWORDS_KO,
    MAX_ARTICLES_PER_FEED,
    MAX_CONCURRENT_FETCHES,
    MIN_ARTICLE_LENGTH,
    MIN_PARAGRAPH_COUNT,
    NAVER_NEWS_SEARCH,
    RSS_FEEDS,
    TARGET_TOTAL_ARTICLES,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}
REQUEST_TIMEOUT = 30


@dataclass
class Article:
    title: str
    url: str
    source: str
    content: str           # 원문 전체 텍스트
    html_content: str = ""  # HTML 형식 원문
    author: str = ""
    published: str = ""
    language: str = "unknown"
    images: list = field(default_factory=list)
    quality_score: float = 0.0  # 품질 점수 (0~1)
    word_count: int = 0
    extraction_method: str = ""  # 어떤 엔진으로 추출했는지


# ============================================================
# RSS 피드 파싱
# ============================================================

def fetch_rss_entries(feed_url: str, source_name: str) -> list[dict]:
    """RSS/Atom 피드에서 기사 엔트리를 가져옴 (표준 라이브러리 사용)"""
    try:
        response = requests.get(feed_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        entries = []
        # RSS 2.0
        items = root.findall(".//item")
        # Atom 피드
        if not items:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//atom:entry", ns)

        for item in items[:MAX_ARTICLES_PER_FEED]:
            title = _xml_text(item, "title")
            link = _xml_text(item, "link")
            pub_date = _xml_text(item, "pubDate") or _xml_text(item, "published")
            author = _xml_text(item, "author") or _xml_text(item, "dc:creator")

            # Atom fallback
            if not title:
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                title = _xml_text(item, "atom:title", ns)
            if not link:
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                link_el = item.find("atom:link", ns)
                if link_el is not None:
                    link = link_el.get("href", "")
            if not pub_date:
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                pub_date = (
                    _xml_text(item, "atom:published", ns)
                    or _xml_text(item, "atom:updated", ns)
                )

            if title and link:
                entries.append({
                    "title": title.strip(),
                    "url": link.strip(),
                    "source": source_name,
                    "published": pub_date or "",
                    "author": author or "",
                })

        logger.info(f"[{source_name}] RSS에서 {len(entries)}개 엔트리 수집")
        return entries
    except Exception as e:
        logger.warning(f"[{source_name}] RSS 파싱 실패: {e}")
        return []


def _xml_text(element: ET.Element, tag: str, ns: dict = None) -> str:
    """XML 요소에서 텍스트 안전하게 추출"""
    child = element.find(tag, ns) if ns else element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return ""


# ============================================================
# 네이버 뉴스 크롤링 (한국 뉴스 보강)
# ============================================================

def fetch_naver_news_entries() -> list[dict]:
    """네이버 뉴스 검색에서 AI/Tech 기사 엔트리를 수집"""
    entries = []
    try:
        for query in NAVER_NEWS_SEARCH["queries"]:
            params = {
                "where": "news",
                "query": query,
                "sort": "1",  # 최신순
            }
            resp = requests.get(
                NAVER_NEWS_SEARCH["base_url"],
                params=params,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("div.news_area, div.news_wrap")

            count = 0
            for item in news_items:
                if count >= NAVER_NEWS_SEARCH["max_per_query"]:
                    break

                title_el = item.select_one("a.news_tit")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                url = title_el.get("href", "")

                # 네이버 뉴스 링크만 (원문 기사 접근 가능)
                if not url:
                    continue

                source_el = item.select_one("a.info.press")
                source = source_el.get_text(strip=True) if source_el else "네이버 뉴스"

                entries.append({
                    "title": title,
                    "url": url,
                    "source": f"네이버/{source}",
                    "published": "",
                    "author": "",
                })
                count += 1

            time.sleep(FETCH_DELAY)

        logger.info(f"[네이버 뉴스] {len(entries)}개 엔트리 수집")
    except Exception as e:
        logger.warning(f"[네이버 뉴스] 크롤링 실패: {e}")

    return entries


# ============================================================
# 멀티 백엔드 기사 원문 추출
# ============================================================

def _download_page(url: str) -> Optional[str]:
    """URL에서 HTML 다운로드"""
    html = trafilatura.fetch_url(url)
    if html:
        return html
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except Exception as e:
        logger.debug(f"다운로드 실패 ({url}): {e}")
        return None


def _extract_with_trafilatura(html: str) -> Optional[tuple[str, str]]:
    """[백엔드 1] trafilatura - 가장 정확한 본문 추출"""
    try:
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            include_images=True,
            include_links=True,
            no_fallback=False,
            favor_precision=False,
            favor_recall=True,
        )
        html_out = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            include_images=True,
            include_links=True,
            no_fallback=False,
            favor_recall=True,
            output_format="html",
        )
        if text and len(text) > MIN_ARTICLE_LENGTH:
            return text, html_out or ""
    except Exception:
        pass
    return None


def _extract_with_readability(html: str) -> Optional[tuple[str, str]]:
    """[백엔드 2] readability-lxml - Mozilla Readability 포트"""
    try:
        doc = ReadabilityDocument(html)
        html_content = doc.summary()

        soup = BeautifulSoup(html_content, "lxml")
        text = soup.get_text(separator="\n", strip=True)

        if text and len(text) > MIN_ARTICLE_LENGTH:
            return text, html_content
    except Exception:
        pass
    return None


def _extract_with_beautifulsoup(html: str) -> Optional[tuple[str, str]]:
    """[백엔드 3] BeautifulSoup - 최후의 폴백"""
    try:
        soup = BeautifulSoup(html, "lxml")

        for tag in soup.find_all(["script", "style", "nav", "footer",
                                   "header", "aside", "iframe", "noscript"]):
            tag.decompose()

        article = (
            soup.find("article")
            or soup.find("div", class_=lambda c: c and any(
                k in c for k in ["article-body", "article_body", "content-body",
                                  "story-body", "post-content", "entry-content"]))
            or soup.find("div", class_=lambda c: c and "content" in c)
            or soup.find("main")
        )

        if article:
            text = article.get_text(separator="\n", strip=True)
            html_content = str(article)
        else:
            paragraphs = soup.find_all("p")
            good_paras = [p for p in paragraphs if len(p.get_text(strip=True)) > 30]
            text = "\n\n".join(p.get_text(strip=True) for p in good_paras)
            html_content = "\n".join(str(p) for p in good_paras)

        if text and len(text) > MIN_ARTICLE_LENGTH:
            return text, html_content
    except Exception:
        pass
    return None


def extract_full_article(url: str) -> Optional[tuple[str, str, str]]:
    """
    멀티 백엔드 추출 체인으로 기사 원문을 최대한 전체 추출

    추출 순서: trafilatura → readability-lxml → BeautifulSoup
    가장 긴 결과를 반환 (원문 최대 보존)

    Returns: (plain_text, html_content, extraction_method) 또는 None
    """
    html = _download_page(url)
    if not html:
        return None

    results = []

    # 백엔드 1: trafilatura (가장 정확)
    r = _extract_with_trafilatura(html)
    if r:
        results.append((r[0], r[1], "trafilatura"))

    # 백엔드 2: readability-lxml (Mozilla Readability)
    r = _extract_with_readability(html)
    if r:
        results.append((r[0], r[1], "readability"))

    # 백엔드 3: BeautifulSoup (폴백)
    if not results:
        r = _extract_with_beautifulsoup(html)
        if r:
            results.append((r[0], r[1], "beautifulsoup"))

    if not results:
        return None

    # 가장 긴 결과 선택 (원문 최대 보존 원칙)
    best = max(results, key=lambda x: len(x[0]))
    return best


# ============================================================
# 품질 스코어링 및 필터링
# ============================================================

def compute_quality_score(text: str, title: str) -> float:
    """
    기사 품질 점수 계산 (0.0 ~ 1.0)
    높을수록 좋은 기사
    """
    score = 0.0

    # 길이 점수 (0~0.3) - 긴 기사 선호
    char_count = len(text)
    if char_count > 3000:
        score += 0.3
    elif char_count > 1000:
        score += 0.2
    elif char_count > 500:
        score += 0.1

    # 단락 수 점수 (0~0.2)
    paragraphs = [p for p in text.split("\n") if p.strip() and len(p.strip()) > 20]
    if len(paragraphs) >= 10:
        score += 0.2
    elif len(paragraphs) >= MIN_PARAGRAPH_COUNT:
        score += 0.1

    # 키워드 관련성 점수 (0~0.3)
    title_lower = title.lower()
    text_lower = text[:2000].lower()
    all_keywords = KEYWORDS_KO + KEYWORDS_EN
    keyword_hits = sum(1 for kw in all_keywords if kw.lower() in title_lower or kw.lower() in text_lower)
    if keyword_hits >= 5:
        score += 0.3
    elif keyword_hits >= 3:
        score += 0.2
    elif keyword_hits >= 1:
        score += 0.1

    # 광고/스팸 패턴 감점 (0~-0.2)
    ad_patterns = [
        r"구독.*클릭", r"광고.*문의", r"copyright", r"all rights reserved",
        r"무단.*전재", r"재배포.*금지", r"subscribe.*newsletter",
    ]
    ad_count = sum(1 for p in ad_patterns if re.search(p, text_lower))
    score -= min(ad_count * 0.05, 0.2)

    return max(0.0, min(1.0, score))


def _content_fingerprint(text: str) -> str:
    """기사 내용 기반 지문 (중복 탐지용)"""
    # 앞 500자의 해시로 유사 기사 탐지
    normalized = re.sub(r"\s+", "", text[:500])
    return hashlib.md5(normalized.encode()).hexdigest()


def detect_language(text: str) -> str:
    """간단한 한글/영문 감지"""
    korean_chars = sum(1 for c in text[:500] if "\uac00" <= c <= "\ud7a3")
    return "ko" if korean_chars > 10 else "en"


def is_relevant(title: str) -> bool:
    """기사 제목이 AI/Tech 관련인지 키워드 필터링"""
    title_lower = title.lower()
    all_keywords = KEYWORDS_KO + KEYWORDS_EN
    return any(kw.lower() in title_lower for kw in all_keywords)


# ============================================================
# 기사 수집 파이프라인
# ============================================================

def _fetch_single_article(entry: dict) -> Optional[Article]:
    """단일 기사를 가져와 Article 객체로 변환"""
    url = entry["url"]
    result = extract_full_article(url)
    if not result:
        return None

    text_content, html_content, method = result
    lang = detect_language(text_content)
    quality = compute_quality_score(text_content, entry["title"])

    return Article(
        title=entry["title"],
        url=url,
        source=entry["source"],
        content=text_content,
        html_content=html_content,
        author=entry.get("author", ""),
        published=entry.get("published", ""),
        language=lang,
        quality_score=quality,
        word_count=len(text_content),
        extraction_method=method,
    )


def _collect_all_entries() -> list[dict]:
    """모든 소스에서 RSS 엔트리 수집 (RSS + 구글뉴스 + 네이버)"""
    all_entries = []

    # 1. 기본 RSS 피드
    for source_name, feed_url in RSS_FEEDS.items():
        entries = fetch_rss_entries(feed_url, source_name)
        all_entries.extend(entries)
        time.sleep(FETCH_DELAY)

    # 2. 구글 뉴스 RSS
    for source_name, feed_url in GOOGLE_NEWS_RSS.items():
        entries = fetch_rss_entries(feed_url, source_name)
        all_entries.extend(entries)
        time.sleep(FETCH_DELAY)

    # 3. 네이버 뉴스 검색
    naver_entries = fetch_naver_news_entries()
    all_entries.extend(naver_entries)

    return all_entries


def collect_articles(target_count: int = TARGET_TOTAL_ARTICLES) -> list[Article]:
    """
    모든 소스에서 기사를 수집하고 원문을 추출
    멀티 백엔드 + 동시 수집 + 품질 스코어링 + 한글/영문 균형
    """
    logger.info(f"=== 뉴스 수집 시작 (목표: {target_count}개) ===")

    # 1단계: 모든 피드에서 엔트리 수집
    all_entries = _collect_all_entries()
    logger.info(f"총 {len(all_entries)}개 RSS/검색 엔트리 수집 완료")

    # 2단계: AI/Tech 관련 필터링 (키워드 매칭 우선 정렬)
    relevant = [e for e in all_entries if is_relevant(e["title"])]
    others = [e for e in all_entries if not is_relevant(e["title"])]
    sorted_entries = relevant + others
    logger.info(f"키워드 매칭: {len(relevant)}개, 기타: {len(others)}개")

    # 3단계: URL 중복 제거
    seen_urls = set()
    unique_entries = []
    for entry in sorted_entries:
        url = entry["url"]
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_entries.append(entry)
    logger.info(f"URL 중복 제거 후: {len(unique_entries)}개")

    # 4단계: 동시 수집 (ThreadPoolExecutor)
    articles = []
    content_fingerprints = set()

    # 목표보다 많이 시도 (실패 대비)
    candidates = unique_entries[:target_count * 3]

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_FETCHES) as executor:
        future_to_entry = {
            executor.submit(_fetch_single_article, entry): entry
            for entry in candidates
        }

        for future in as_completed(future_to_entry):
            if len(articles) >= target_count:
                break

            entry = future_to_entry[future]
            try:
                article = future.result()
                if not article:
                    logger.warning(f"  x 추출 실패: {entry['title'][:40]}")
                    continue

                # 내용 중복 체크
                fp = _content_fingerprint(article.content)
                if fp in content_fingerprints:
                    logger.info(f"  ~ 중복 건너뜀: {entry['title'][:40]}")
                    continue
                content_fingerprints.add(fp)

                # 품질 기준 미달 건너뜀
                if article.quality_score < 0.1:
                    logger.info(f"  ~ 품질 미달 건너뜀 (score={article.quality_score:.2f}): {entry['title'][:40]}")
                    continue

                articles.append(article)
                logger.info(
                    f"  v [{article.language.upper()}] ({article.word_count:,}자, "
                    f"Q={article.quality_score:.2f}, {article.extraction_method}) "
                    f"- {entry['title'][:40]}"
                )
            except Exception as e:
                logger.warning(f"  x 처리 오류 ({entry['title'][:40]}): {e}")

    # 5단계: 품질 점수 기준 정렬 + 한글/영문 균형
    articles.sort(key=lambda a: a.quality_score, reverse=True)

    if len(articles) > target_count:
        # 한글/영문 균형 맞추기 (최소 각 30%)
        ko_articles = [a for a in articles if a.language == "ko"]
        en_articles = [a for a in articles if a.language == "en"]

        min_each = max(1, target_count * 3 // 10)  # 최소 30%
        balanced = []

        # 한글 최소 보장
        balanced.extend(ko_articles[:min_each])
        # 영문 최소 보장
        balanced.extend(en_articles[:min_each])

        # 나머지는 품질순으로 채움
        remaining = [a for a in articles if a not in balanced]
        remaining.sort(key=lambda a: a.quality_score, reverse=True)
        balanced.extend(remaining[:target_count - len(balanced)])

        articles = balanced[:target_count]

    ko_count = sum(1 for a in articles if a.language == "ko")
    en_count = sum(1 for a in articles if a.language == "en")
    logger.info(f"=== 수집 완료: 총 {len(articles)}개 (한글: {ko_count}, 영문: {en_count}) ===")

    return articles
