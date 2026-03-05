"""
뉴스 소스 설정 - AI/Tech 관련 RSS 피드 및 웹사이트 목록
한글 + 영문 소스를 포함
"""

# RSS 피드 소스 목록
RSS_FEEDS = {
    # === 한글 소스 ===
    "AI타임스": "https://www.aitimes.com/rss/allArticle.xml",
    "ZDNet Korea": "https://zdnet.co.kr/rss/newsall.xml",
    "전자신문": "https://rss.etnews.com/Section901.xml",
    "블로터": "https://www.bloter.net/feed",
    "디지털타임스": "https://www.dt.co.kr/rss/allArticle.xml",
    "IT조선": "http://it.chosun.com/data/rss/rss.xml",

    # === 영문 소스 ===
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "VentureBeat": "https://venturebeat.com/category/ai/feed/",
    "Wired": "https://www.wired.com/feed/category/business/latest/rss",
    "The Register": "https://www.theregister.com/headlines.atom",
    "Hacker News (best)": "https://hnrss.org/best?q=AI+OR+LLM+OR+GPT",
}

# 네이버 뉴스 검색 설정 (한국 뉴스 보강용)
NAVER_NEWS_SEARCH = {
    "base_url": "https://search.naver.com/search.naver",
    "queries": [
        "인공지능 AI 최신",
        "LLM GPT 클로드",
        "반도체 AI 칩",
        "테크 스타트업 AI",
    ],
    "max_per_query": 3,
}

# 구글 뉴스 RSS (추가 소스)
GOOGLE_NEWS_RSS = {
    "AI 뉴스 (한글)": "https://news.google.com/rss/search?q=AI+%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5&hl=ko&gl=KR&ceid=KR:ko",
    "AI News (EN)": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
}

# AI/Tech 관련 키워드 필터
KEYWORDS_KO = [
    "AI", "인공지능", "LLM", "GPT", "클로드", "딥러닝", "머신러닝",
    "로봇", "반도체", "칩", "자율주행", "메타", "구글", "오픈AI",
    "애플", "삼성", "테크", "스타트업", "데이터", "엔비디아",
    "딥시크", "앤트로픽", "에이전트", "뉴럴", "트랜스포머",
    "파운데이션 모델", "생성형", "챗봇", "클라우드",
]

KEYWORDS_EN = [
    "AI", "artificial intelligence", "LLM", "GPT", "Claude",
    "deep learning", "machine learning", "robot", "chip",
    "semiconductor", "autonomous", "OpenAI", "Google", "Apple",
    "Meta", "startup", "neural", "transformer", "agent",
    "Nvidia", "DeepSeek", "Anthropic", "foundation model",
    "generative", "chatbot", "world model", "reasoning",
]

# 기사 수집 설정
MAX_ARTICLES_PER_FEED = 5
TARGET_TOTAL_ARTICLES = 10

# 품질 필터링 기준
MIN_ARTICLE_LENGTH = 200     # 최소 글자 수 (너무 짧은 기사 제외)
MIN_PARAGRAPH_COUNT = 3      # 최소 단락 수
MAX_AD_RATIO = 0.3           # 광고성 텍스트 비율 상한

# 동시 수집 설정
MAX_CONCURRENT_FETCHES = 5   # 동시 HTTP 요청 수
FETCH_DELAY = 0.5            # 같은 도메인 요청 간 지연 (초)
