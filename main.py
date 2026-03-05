#!/usr/bin/env python3
"""
AI & Tech 뉴스 스크래퍼 EPUB 에이전트
=============================================
한글/영문 AI·테크 뉴스 기사를 RSS에서 수집하여
원문 그대로 EPUB 전자책으로 생성합니다.

사용법:
    python main.py                          # RSS에서 실시간 수집 (10개)
    python main.py --count 15               # 15개 기사 수집
    python main.py --from-json data/articles.json  # JSON에서 로드
    python main.py --output ./books         # 출력 디렉토리 지정
    python main.py --list-sources           # 등록된 소스 목록 확인
"""

import argparse
import logging
import sys
import time

from news_scraper.article_scraper import collect_articles
from news_scraper.epub_builder import build_epub
from news_scraper.fetch_with_search import load_articles_from_json
from news_scraper.sources import RSS_FEEDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def list_sources():
    """등록된 뉴스 소스 목록 출력"""
    print("\n등록된 뉴스 소스:")
    print("=" * 50)
    for name, url in RSS_FEEDS.items():
        print(f"  - {name}")
        print(f"    {url}")
    print(f"\n총 {len(RSS_FEEDS)}개 소스 등록됨\n")


def run_agent(target_count: int = 10, output_dir: str = "output", json_path: str = None):
    """
    뉴스 수집 → EPUB 생성 파이프라인 실행

    Args:
        target_count: 수집할 기사 수
        output_dir: EPUB 출력 디렉토리
        json_path: JSON 파일 경로 (지정 시 RSS 대신 JSON에서 로드)
    """
    start_time = time.time()

    print("\n" + "=" * 60)
    print("  AI & Tech 뉴스 스크래퍼 EPUB 에이전트")
    print("=" * 60)

    if json_path:
        print(f"  모드: JSON 파일에서 로드")
        print(f"  파일: {json_path}")
    else:
        print(f"  모드: RSS 실시간 수집")
        print(f"  목표 기사 수: {target_count}개")
        print(f"  뉴스 소스: {len(RSS_FEEDS)}개 RSS 피드")

    print(f"  출력 디렉토리: {output_dir}")
    print("=" * 60 + "\n")

    # 1단계: 기사 수집
    print("[1/2] 뉴스 기사 수집 중...")

    if json_path:
        articles = load_articles_from_json(json_path)
    else:
        articles = collect_articles(target_count=target_count)

    if not articles:
        logger.error("수집된 기사가 없습니다.")
        sys.exit(1)

    print(f"\n  -> {len(articles)}개 기사 수집 완료\n")

    # 기사 목록 출력
    print("  수집된 기사 목록:")
    print("  " + "-" * 56)
    for i, article in enumerate(articles, 1):
        lang = "KO" if article.language == "ko" else "EN"
        content_len = len(article.content)
        print(f"  {i:2d}. [{lang}] {article.title[:45]}")
        print(f"      출처: {article.source} | 길이: {content_len:,}자")
    print()

    # 2단계: EPUB 생성
    print("[2/2] EPUB 파일 생성 중...")
    epub_path = build_epub(articles, output_dir=output_dir)

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("  완료!")
    print(f"  EPUB 파일: {epub_path}")
    print(f"  소요 시간: {elapsed:.1f}초")
    print("=" * 60 + "\n")

    return epub_path


def main():
    parser = argparse.ArgumentParser(
        description="AI & Tech 뉴스 스크래퍼 EPUB 에이전트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=10,
        help="수집할 기사 수 (기본값: 10)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="EPUB 출력 디렉토리 (기본값: output)",
    )
    parser.add_argument(
        "--from-json", "-j",
        type=str,
        default=None,
        help="JSON 파일에서 기사 로드 (RSS 대신)",
    )
    parser.add_argument(
        "--list-sources", "-l",
        action="store_true",
        help="등록된 뉴스 소스 목록 표시",
    )

    args = parser.parse_args()

    if args.list_sources:
        list_sources()
        return

    run_agent(
        target_count=args.count,
        output_dir=args.output,
        json_path=args.from_json,
    )


if __name__ == "__main__":
    main()
