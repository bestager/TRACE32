"""
기사 원문 스크래퍼 모듈
- RSS 피드에서 기사 목록 수집
- trafilatura로 기사 원문 전체 추출 (요약 최소화)
- 한글/영문 기사 모두 지원
"""

import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

import requests
import trafilatura
from bs4 import BeautifulSoup

from .sources import (
    KEYWORDS_EN,
    KEYWORDS_KO,
    MAX_ARTICLES_PER_FEED,
    RSS_FEEDS,
    TARGET_TOTAL_ARTICLES,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 30


@dataclass
class Article:
    title: str
    url: str
    source: str
    content: str  # 원문 전체 텍스트
    html_content: str = ""  # HTML 형식 원문
    author: str = ""
    published: str = ""
    language: str = "unknown"
    images: list = field(default_factory=list)


def fetch_rss_entries(feed_url: str, source_name: str) -> list[dict]:
    """RSS/Atom 피드에서 기사 엔트리를 가져옴 (표준 라이브러리 사용)"""
    try:
        response = requests.get(feed_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        entries = []
        # RSS 2.0 네임스페이스 없이
        items = root.findall(".//item")
        # Atom 피드
        if not items:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//atom:entry", ns)

        for item in items[:MAX_ARTICLES_PER_FEED]:
            # RSS 2.0
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
                pub_date = _xml_text(item, "atom:published", ns) or _xml_text(item, "atom:updated", ns)

            if title and link:
                entries.append({
                    "title": title,
                    "url": link,
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


def is_relevant(title: str) -> bool:
    """기사 제목이 AI/Tech 관련인지 키워드 필터링"""
    title_lower = title.lower()
    all_keywords = KEYWORDS_KO + KEYWORDS_EN
    return any(kw.lower() in title_lower for kw in all_keywords)


def extract_full_article(url: str) -> Optional[tuple[str, str]]:
    """
    URL에서 기사 원문을 최대한 전체 추출
    Returns: (plain_text, html_content) 또는 None
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            downloaded = response.text

        # 원문 전체 추출 설정 - 요약 최소화
        text_content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            include_images=True,
            include_links=True,
            no_fallback=False,
            favor_precision=False,  # recall 우선 = 더 많은 텍스트 추출
            favor_recall=True,
        )

        html_content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            include_images=True,
            include_links=True,
            no_fallback=False,
            favor_recall=True,
            output_format="html",
        )

        if text_content and len(text_content) > 100:
            return text_content, html_content or ""

        # fallback: BeautifulSoup으로 직접 추출
        return _fallback_extract(downloaded)

    except Exception as e:
        logger.warning(f"기사 추출 실패 ({url}): {e}")
        return None


def _fallback_extract(html: str) -> Optional[tuple[str, str]]:
    """trafilatura 실패 시 BeautifulSoup 폴백"""
    try:
        soup = BeautifulSoup(html, "lxml")

        # 불필요한 태그 제거
        for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # 본문 영역 탐색
        article = (
            soup.find("article")
            or soup.find("div", class_=lambda c: c and "content" in c)
            or soup.find("div", class_=lambda c: c and "article" in c)
            or soup.find("main")
        )

        if article:
            text = article.get_text(separator="\n", strip=True)
            html_content = str(article)
        else:
            paragraphs = soup.find_all("p")
            text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
            html_content = "\n".join(str(p) for p in paragraphs if len(p.get_text(strip=True)) > 20)

        if text and len(text) > 100:
            return text, html_content
        return None
    except Exception:
        return None


def detect_language(text: str) -> str:
    """간단한 한글/영문 감지"""
    korean_chars = sum(1 for c in text[:500] if "\uac00" <= c <= "\ud7a3")
    return "ko" if korean_chars > 10 else "en"


def collect_articles(target_count: int = TARGET_TOTAL_ARTICLES) -> list[Article]:
    """
    모든 RSS 소스에서 기사를 수집하고 원문을 추출
    한글/영문 균형 맞춤
    """
    all_entries = []

    logger.info(f"=== 뉴스 수집 시작 (목표: {target_count}개) ===")

    # 1단계: 모든 RSS 피드에서 엔트리 수집
    for source_name, feed_url in RSS_FEEDS.items():
        entries = fetch_rss_entries(feed_url, source_name)
        all_entries.extend(entries)
        time.sleep(0.5)  # 예의 바른 크롤링

    logger.info(f"총 {len(all_entries)}개 RSS 엔트리 수집 완료")

    # 2단계: AI/Tech 관련 필터링 (키워드 매칭이 있는 것 우선)
    relevant = [e for e in all_entries if is_relevant(e["title"])]
    others = [e for e in all_entries if not is_relevant(e["title"])]
    sorted_entries = relevant + others

    logger.info(f"키워드 매칭: {len(relevant)}개, 기타: {len(others)}개")

    # 3단계: 기사 원문 추출
    articles = []
    seen_urls = set()

    for entry in sorted_entries:
        if len(articles) >= target_count:
            break

        url = entry["url"]
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        logger.info(f"원문 추출 중: {entry['title'][:50]}...")
        result = extract_full_article(url)

        if result:
            text_content, html_content = result
            lang = detect_language(text_content)
            article = Article(
                title=entry["title"],
                url=url,
                source=entry["source"],
                content=text_content,
                html_content=html_content,
                author=entry.get("author", ""),
                published=entry.get("published", ""),
                language=lang,
            )
            articles.append(article)
            logger.info(
                f"  ✓ 수집 완료 [{lang}] ({len(text_content)}자) - {entry['title'][:40]}"
            )
        else:
            logger.warning(f"  ✗ 추출 실패: {entry['title'][:40]}")

        time.sleep(1)  # 서버 부하 방지

    # 한글/영문 균형 정보
    ko_count = sum(1 for a in articles if a.language == "ko")
    en_count = sum(1 for a in articles if a.language == "en")
    logger.info(f"=== 수집 완료: 총 {len(articles)}개 (한글: {ko_count}, 영문: {en_count}) ===")

    return articles
