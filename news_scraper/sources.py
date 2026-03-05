"""
뉴스 소스 설정 - AI/Tech 관련 RSS 피드 및 웹사이트 목록
한글 + 영문 소스를 포함
"""

# RSS 피드 소스 목록
RSS_FEEDS = {
    # 한글 소스
    "AI타임스": "https://www.aitimes.com/rss/allArticle.xml",
    "ZDNet Korea": "https://zdnet.co.kr/rss/newsall.xml",
    "전자신문": "https://rss.etnews.com/Section901.xml",
    "블로터": "https://www.bloter.net/feed",

    # 영문 소스
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "VentureBeat": "https://venturebeat.com/category/ai/feed/",
    "Wired": "https://www.wired.com/feed/category/business/latest/rss",
}

# AI/Tech 관련 키워드 필터
KEYWORDS_KO = ["AI", "인공지능", "LLM", "GPT", "클로드", "딥러닝", "머신러닝",
               "로봇", "반도체", "칩", "자율주행", "메타", "구글", "오픈AI",
               "애플", "삼성", "테크", "스타트업", "데이터"]

KEYWORDS_EN = ["AI", "artificial intelligence", "LLM", "GPT", "Claude",
               "deep learning", "machine learning", "robot", "chip",
               "semiconductor", "autonomous", "OpenAI", "Google", "Apple",
               "Meta", "startup", "neural", "transformer", "agent"]

# 기사 수집 설정
MAX_ARTICLES_PER_FEED = 5
TARGET_TOTAL_ARTICLES = 10
