"""
WebSearch 기반 뉴스 수집 모듈
- 외부 HTTP 접근이 제한된 환경에서 사용
- 사전 수집된 JSON 데이터로 EPUB 생성 지원
"""

import json
import logging
import os
from datetime import datetime

from .article_scraper import Article

logger = logging.getLogger(__name__)


def load_articles_from_json(json_path: str) -> list[Article]:
    """JSON 파일에서 기사 목록을 로드"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = []
    for item in data:
        articles.append(Article(
            title=item["title"],
            url=item.get("url", ""),
            source=item.get("source", ""),
            content=item.get("content", ""),
            html_content=item.get("html_content", ""),
            author=item.get("author", ""),
            published=item.get("published", ""),
            language=item.get("language", "unknown"),
        ))

    logger.info(f"JSON에서 {len(articles)}개 기사 로드 완료")
    return articles


def save_articles_to_json(articles: list[Article], json_path: str) -> str:
    """기사 목록을 JSON으로 저장"""
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
        })

    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"기사 {len(data)}개를 {json_path}에 저장")
    return json_path
