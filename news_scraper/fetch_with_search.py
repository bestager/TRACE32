"""
뉴스 데이터 JSON 입출력 모듈
- 사전 수집된 JSON 데이터로 EPUB 생성 지원
- 수집 결과를 JSON으로 저장하여 재사용 가능
"""

import json
import logging
import os

from .article_scraper import Article, compute_quality_score

logger = logging.getLogger(__name__)


def load_articles_from_json(json_path: str) -> list[Article]:
    """JSON 파일에서 기사 목록을 로드 (품질 점수 자동 계산)"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = []
    for item in data:
        content = item.get("content", "")
        title = item["title"]
        quality = item.get("quality_score") or compute_quality_score(content, title)

        articles.append(Article(
            title=title,
            url=item.get("url", ""),
            source=item.get("source", ""),
            content=content,
            html_content=item.get("html_content", ""),
            author=item.get("author", ""),
            published=item.get("published", ""),
            language=item.get("language", "unknown"),
            quality_score=quality,
            word_count=len(content),
            extraction_method=item.get("extraction_method", "json"),
        ))

    logger.info(f"JSON에서 {len(articles)}개 기사 로드 완료")
    return articles


def save_articles_to_json(articles: list[Article], json_path: str) -> str:
    """기사 목록을 JSON으로 저장 (재로드 가능한 포맷)"""
    data = []
    for a in articles:
        data.append({
            "title": a.title,
            "url": a.url,
            "source": a.source,
            "content": a.content,
            "html_content": a.html_content,
            "author": a.author,
            "published": a.published,
            "language": a.language,
            "quality_score": a.quality_score,
            "word_count": a.word_count,
            "extraction_method": a.extraction_method,
        })

    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"기사 {len(data)}개를 {json_path}에 저장")
    return json_path
