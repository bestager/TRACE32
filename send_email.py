#!/usr/bin/env python3
"""
EPUB 이메일 발송 스크립트
========================
생성된 EPUB 파일을 이메일로 발송합니다.

사용법:
    # Gmail 앱 비밀번호 사용 (권장)
    python send_email.py --sender your@gmail.com --password "앱비밀번호"

    # 환경변수로 설정
    export SMTP_SENDER=your@gmail.com
    export SMTP_PASSWORD=your_app_password
    python send_email.py

    # 다른 SMTP 서버
    python send_email.py --smtp-host smtp.naver.com --smtp-port 587 \\
        --sender your@naver.com --password "비밀번호"

Gmail 앱 비밀번호 생성:
    1. Google 계정 → 보안 → 2단계 인증 활성화
    2. Google 계정 → 보안 → 앱 비밀번호 → 생성
    3. 생성된 16자리 비밀번호를 --password에 입력
"""

import argparse
import logging
import os
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 기본 설정
DEFAULT_RECIPIENT = "bestager@gmail.com"
DEFAULT_EPUB = "output/tech_news_2026-03-05.epub"
DEFAULT_SMTP_HOST = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587


def send_epub_email(
    sender: str,
    password: str,
    recipient: str = DEFAULT_RECIPIENT,
    epub_path: str = DEFAULT_EPUB,
    smtp_host: str = DEFAULT_SMTP_HOST,
    smtp_port: int = DEFAULT_SMTP_PORT,
):
    """EPUB 파일을 이메일 첨부로 발송"""

    if not os.path.exists(epub_path):
        logger.error(f"EPUB 파일을 찾을 수 없습니다: {epub_path}")
        sys.exit(1)

    epub_name = Path(epub_path).name
    epub_size = os.path.getsize(epub_path)

    # 이메일 작성
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = "AI & Tech News Digest (2026-03-03 ~ 03-05) - 15 Articles"

    body = """안녕하세요,

AI & Tech 뉴스 다이제스트를 보내드립니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  기간: 2026년 3월 3일 ~ 3월 5일
  기사 수: 15개 (한글 10 / 영문 5)
  총 읽기 시간: 약 16분
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

주요 기사 (HIGH 중요도):
  • 엔비디아 GTC 2026 D-11: AI 추론 전용 칩 공개 임박
  • 삼성전자 반도체, 엔비디아 제치고 세계 1위 복귀 초읽기
  • Apple, M5 Pro·M5 Max MacBook Pro 발표
  • Block, 직원 절반 해고 — AI 자동화가 원인
  • Users Ditching ChatGPT for Claude
  • OpenAI Raises $110B
  • AI Industry Shifts from Hype to Pragmatism

첨부된 EPUB 파일을 e-리더, Apple Books, Google Play Books
등에서 열어보실 수 있습니다.

---
News Scraper EPUB Agent v2
Engines: trafilatura + readability-lxml + BeautifulSoup
"""

    msg.attach(MIMEText(body, "plain", "utf-8"))

    # EPUB 첨부
    with open(epub_path, "rb") as f:
        attachment = MIMEBase("application", "epub+zip")
        attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            f"attachment; filename={epub_name}",
        )
        msg.attach(attachment)

    # 발송
    logger.info(f"SMTP 서버 연결 중: {smtp_host}:{smtp_port}")
    logger.info(f"발신: {sender} → 수신: {recipient}")
    logger.info(f"첨부: {epub_name} ({epub_size:,} bytes)")

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.send_message(msg)

        logger.info("이메일 발송 성공!")
        print(f"\n  이메일 발송 완료: {recipient}")
        print(f"  첨부 파일: {epub_name}\n")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP 인증 실패. Gmail의 경우 '앱 비밀번호'를 사용하세요.\n"
            "  → Google 계정 → 보안 → 2단계 인증 → 앱 비밀번호"
        )
        return False
    except Exception as e:
        logger.error(f"이메일 발송 실패: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="EPUB 이메일 발송 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--sender", type=str,
        default=os.environ.get("SMTP_SENDER", ""),
        help="발신 이메일 (또는 SMTP_SENDER 환경변수)",
    )
    parser.add_argument(
        "--password", type=str,
        default=os.environ.get("SMTP_PASSWORD", ""),
        help="SMTP 비밀번호 (또는 SMTP_PASSWORD 환경변수)",
    )
    parser.add_argument(
        "--recipient", type=str,
        default=DEFAULT_RECIPIENT,
        help=f"수신 이메일 (기본값: {DEFAULT_RECIPIENT})",
    )
    parser.add_argument(
        "--epub", type=str,
        default=DEFAULT_EPUB,
        help=f"EPUB 파일 경로 (기본값: {DEFAULT_EPUB})",
    )
    parser.add_argument(
        "--smtp-host", type=str,
        default=DEFAULT_SMTP_HOST,
        help=f"SMTP 서버 (기본값: {DEFAULT_SMTP_HOST})",
    )
    parser.add_argument(
        "--smtp-port", type=int,
        default=DEFAULT_SMTP_PORT,
        help=f"SMTP 포트 (기본값: {DEFAULT_SMTP_PORT})",
    )

    args = parser.parse_args()

    if not args.sender or not args.password:
        print("\n사용법:")
        print("  python send_email.py --sender your@gmail.com --password '앱비밀번호'")
        print("\n또는 환경변수로:")
        print("  export SMTP_SENDER=your@gmail.com")
        print("  export SMTP_PASSWORD=your_app_password")
        print("  python send_email.py\n")
        sys.exit(1)

    send_epub_email(
        sender=args.sender,
        password=args.password,
        recipient=args.recipient,
        epub_path=args.epub,
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
    )


if __name__ == "__main__":
    main()
