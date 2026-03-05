#!/usr/bin/env python3
"""
AI & Tech 뉴스 스크래퍼 EPUB 에이전트 v2
=============================================
한글/영문 AI·테크 뉴스 기사를 RSS + 네이버 + 구글뉴스에서 수집하여
기사 원문 그대로 EPUB 전자책으로 생성합니다.

추출 엔진: trafilatura → readability-lxml → BeautifulSoup (3단계 폴백)

사용법:
    python main.py                              # RSS에서 실시간 수집 (10개)
    python main.py --count 15                   # 15개 기사 수집
    python main.py --from-json data/articles.json  # JSON에서 로드
    python main.py --output ./books             # 출력 디렉토리 지정
    python main.py --save-json                  # 수집 결과를 JSON으로도 저장
    python main.py --list-sources               # 등록된 소스 목록 확인
"""

import argparse
import logging
import sys
import time

from news_scraper.article_scraper import collect_articles
from news_scraper.epub_builder import build_epub
from news_scraper.fetch_with_search import load_articles_from_json, save_articles_to_json
from news_scraper.sources import GOOGLE_NEWS_RSS, RSS_FEEDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def list_sources():
    """등록된 뉴스 소스 목록 출력"""
    print("\n=== 등록된 뉴스 소스 ===\n")

    print("[RSS 피드]")
    for name, url in RSS_FEEDS.items():
        print(f"  - {name}: {url}")

    print(f"\n[구글 뉴스 RSS]")
    for name, url in GOOGLE_NEWS_RSS.items():
        print(f"  - {name}: {url}")

    print(f"\n[네이버 뉴스 검색] - AI/Tech 키워드 자동 검색")

    total = len(RSS_FEEDS) + len(GOOGLE_NEWS_RSS) + 1
    print(f"\n총 {total}개 소스 등록됨\n")

    print("추출 엔진:")
    print("  1. trafilatura  (1순위 - 가장 정확)")
    print("  2. readability  (2순위 - Mozilla Readability)")
    print("  3. BeautifulSoup (3순위 - 최후 폴백)")
    print()


def run_agent(
    target_count: int = 10,
    output_dir: str = "output",
    json_path: str = None,
    save_json: bool = False,
):
    start_time = time.time()

    print("\n" + "=" * 62)
    print("  AI & Tech 뉴스 스크래퍼 EPUB 에이전트 v2")
    print("  Engines: trafilatura + readability-lxml + BeautifulSoup")
    print("=" * 62)

    if json_path:
        print(f"  Mode: JSON load ({json_path})")
    else:
        total_sources = len(RSS_FEEDS) + len(GOOGLE_NEWS_RSS) + 1
        print(f"  Mode: Live crawl ({total_sources} sources)")
        print(f"  Target: {target_count} articles")

    print(f"  Output: {output_dir}")
    print("=" * 62 + "\n")

    # 1단계: 기사 수집
    print("[1/2] Collecting news articles...")

    if json_path:
        articles = load_articles_from_json(json_path)
    else:
        articles = collect_articles(target_count=target_count)

    if not articles:
        logger.error("No articles collected. Check network or try --from-json mode.")
        sys.exit(1)

    print(f"\n  -> {len(articles)} articles collected\n")

    # 기사 목록 출력
    print("  Collected articles:")
    print("  " + "-" * 58)
    for i, article in enumerate(articles, 1):
        lang = "KO" if article.language == "ko" else "EN"
        q_label = "H" if article.quality_score >= 0.5 else ("M" if article.quality_score >= 0.3 else "L")
        method = article.extraction_method[:5] if article.extraction_method else "?"
        print(
            f"  {i:2d}. [{lang}|{q_label}|{method}] {article.title[:42]}"
        )
        print(f"      {article.source} | {article.word_count:,} chars")
    print()

    # JSON 저장 (옵션)
    if save_json:
        json_out = f"{output_dir}/articles_{time.strftime('%Y%m%d_%H%M%S')}.json"
        save_articles_to_json(articles, json_out)
        print(f"  JSON saved: {json_out}\n")

    # 2단계: EPUB 생성
    print("[2/2] Building EPUB...")
    epub_path = build_epub(articles, output_dir=output_dir)

    elapsed = time.time() - start_time

    print("\n" + "=" * 62)
    print("  Done!")
    print(f"  EPUB: {epub_path}")
    if save_json:
        print(f"  JSON: {json_out}")
    print(f"  Time: {elapsed:.1f}s")
    print("=" * 62 + "\n")

    return epub_path


def main():
    parser = argparse.ArgumentParser(
        description="AI & Tech 뉴스 스크래퍼 EPUB 에이전트 v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--count", "-c", type=int, default=10,
        help="수집할 기사 수 (기본값: 10)",
    )
    parser.add_argument(
        "--output", "-o", type=str, default="output",
        help="EPUB 출력 디렉토리 (기본값: output)",
    )
    parser.add_argument(
        "--from-json", "-j", type=str, default=None,
        help="JSON 파일에서 기사 로드 (RSS 대신)",
    )
    parser.add_argument(
        "--save-json", "-s", action="store_true",
        help="수집 결과를 JSON으로도 저장",
    )
    parser.add_argument(
        "--list-sources", "-l", action="store_true",
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
        save_json=args.save_json,
    )


if __name__ == "__main__":
    main()
