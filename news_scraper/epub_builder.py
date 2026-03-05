"""
EPUB 생성 모듈
- 수집된 기사들을 EPUB 전자책으로 변환
- 목차(TOC) 자동 생성
- 한글/영문 기사 구분 챕터
"""

import logging
import os
from datetime import datetime

from ebooklib import epub

from .article_scraper import Article

logger = logging.getLogger(__name__)

# EPUB 스타일시트
STYLESHEET = """
body {
    font-family: "Noto Sans KR", "Malgun Gothic", "맑은 고딕",
                 "Apple SD Gothic Neo", sans-serif;
    line-height: 1.8;
    margin: 1em;
    color: #333;
}
h1 {
    font-size: 1.6em;
    color: #1a1a2e;
    border-bottom: 2px solid #16213e;
    padding-bottom: 0.3em;
    margin-bottom: 0.5em;
}
h2 {
    font-size: 1.3em;
    color: #16213e;
    margin-top: 1.5em;
}
.article-meta {
    color: #666;
    font-size: 0.85em;
    margin-bottom: 1.5em;
    padding: 0.5em;
    background-color: #f8f9fa;
    border-left: 3px solid #0f3460;
}
.article-meta span {
    display: block;
    margin: 0.2em 0;
}
.article-content {
    text-align: justify;
    font-size: 1em;
}
.article-content p {
    margin: 0.8em 0;
    text-indent: 0;
}
.source-link {
    margin-top: 2em;
    padding-top: 1em;
    border-top: 1px solid #ddd;
    font-size: 0.85em;
    color: #0f3460;
}
.toc-section {
    margin: 1em 0;
}
.toc-section h2 {
    color: #e94560;
}
.cover-title {
    text-align: center;
    margin-top: 30%;
}
.cover-title h1 {
    font-size: 2em;
    border: none;
    color: #0f3460;
}
.cover-title p {
    color: #666;
    font-size: 1.1em;
}
"""

COVER_HTML_TEMPLATE = """
<div class="cover-title">
    <h1>{title}</h1>
    <p>{subtitle}</p>
    <p style="margin-top: 2em; font-size: 0.9em; color: #999;">{date}</p>
    <p style="font-size: 0.8em; color: #aaa;">총 {count}개 기사 (한글: {ko}개 / 영문: {en}개)</p>
</div>
"""

ARTICLE_HTML_TEMPLATE = """
<h1>{title}</h1>
<div class="article-meta">
    <span><strong>출처:</strong> {source}</span>
    <span><strong>작성자:</strong> {author}</span>
    <span><strong>발행일:</strong> {published}</span>
    <span><strong>언어:</strong> {language}</span>
</div>
<div class="article-content">
{content}
</div>
<div class="source-link">
    <p>원문 링크: <a href="{url}">{url}</a></p>
</div>
"""


def _format_article_content(article: Article) -> str:
    """기사 내용을 HTML로 포맷팅"""
    if article.html_content:
        return article.html_content

    # plain text를 HTML 단락으로 변환
    paragraphs = article.content.split("\n")
    html_parts = []
    for p in paragraphs:
        p = p.strip()
        if p:
            html_parts.append(f"<p>{p}</p>")
    return "\n".join(html_parts)


def build_epub(
    articles: list[Article],
    output_dir: str = "output",
    title: str = None,
) -> str:
    """
    기사 목록을 EPUB 파일로 생성

    Args:
        articles: Article 객체 리스트
        output_dir: 출력 디렉토리
        title: EPUB 제목 (기본값: 자동 생성)

    Returns:
        생성된 EPUB 파일 경로
    """
    today = datetime.now().strftime("%Y-%m-%d")
    if not title:
        title = f"AI & Tech 뉴스 다이제스트"

    book = epub.EpubBook()

    # 메타데이터 설정
    book.set_identifier(f"news-digest-{today}")
    book.set_title(title)
    book.set_language("ko")
    book.add_author("News Scraper Agent")
    book.add_metadata("DC", "date", today)
    book.add_metadata("DC", "description",
                      f"AI/Tech 뉴스 {len(articles)}개 기사 모음 ({today})")

    # 스타일시트 추가
    style = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content=STYLESHEET.encode("utf-8"),
    )
    book.add_item(style)

    # 커버 페이지 생성
    ko_count = sum(1 for a in articles if a.language == "ko")
    en_count = sum(1 for a in articles if a.language == "en")

    cover_html = COVER_HTML_TEMPLATE.format(
        title=title,
        subtitle="AI / Technology News Digest",
        date=today,
        count=len(articles),
        ko=ko_count,
        en=en_count,
    )

    cover_chapter = epub.EpubHtml(
        title="표지",
        file_name="cover.xhtml",
        lang="ko",
        content=f"<html><body>{cover_html}</body></html>",
    )
    cover_chapter.add_item(style)
    book.add_item(cover_chapter)

    # 기사 챕터 생성
    chapters = []
    ko_chapters = []
    en_chapters = []

    for i, article in enumerate(articles, 1):
        content_html = _format_article_content(article)
        lang_label = "한글" if article.language == "ko" else "English"

        article_html = ARTICLE_HTML_TEMPLATE.format(
            title=article.title,
            source=article.source,
            author=article.author or "미상",
            published=article.published or "미상",
            language=lang_label,
            content=content_html,
            url=article.url,
        )

        chapter = epub.EpubHtml(
            title=f"{article.title}",
            file_name=f"article_{i:02d}.xhtml",
            lang="ko" if article.language == "ko" else "en",
            content=f"<html><body>{article_html}</body></html>",
        )
        chapter.add_item(style)
        book.add_item(chapter)
        chapters.append(chapter)

        if article.language == "ko":
            ko_chapters.append(chapter)
        else:
            en_chapters.append(chapter)

    # 목차 구성 (한글/영문 구분)
    toc = []
    if ko_chapters:
        toc.append((epub.Section("한글 기사"), ko_chapters))
    if en_chapters:
        toc.append((epub.Section("English Articles"), en_chapters))

    book.toc = toc

    # spine (읽기 순서)
    book.spine = ["nav", cover_chapter] + chapters

    # 네비게이션 파일
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 출력
    os.makedirs(output_dir, exist_ok=True)
    filename = f"tech_news_{today}.epub"
    filepath = os.path.join(output_dir, filename)
    epub.write_epub(filepath, book)

    logger.info(f"EPUB 생성 완료: {filepath}")
    logger.info(f"  - 총 {len(articles)}개 기사 (한글: {ko_count}, 영문: {en_count})")

    return filepath
