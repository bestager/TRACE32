import re

COMMAND_PATTERN = re.compile(
    r'#\s*(.+?)\s*영어\s*추천\s*(\d+)\s*개\s*#'
)

CATEGORY_ALIASES = {
    '회의': '회의',
    '미팅': '회의',
    'meeting': '회의',
    '이메일': '비즈니스 이메일',
    '비즈니스이메일': '비즈니스 이메일',
    '비즈니스 이메일': '비즈니스 이메일',
    'email': '비즈니스 이메일',
    '일상': '일상 대화',
    '일상대화': '일상 대화',
    '일상 대화': '일상 대화',
    'daily': '일상 대화',
    '전화': '전화 영어',
    '전화영어': '전화 영어',
    '전화 영어': '전화 영어',
    'phone': '전화 영어',
    '프레젠테이션': '프레젠테이션',
    '발표': '프레젠테이션',
    'presentation': '프레젠테이션',
    '여행': '여행 영어',
    '여행영어': '여행 영어',
    '여행 영어': '여행 영어',
    'travel': '여행 영어',
    '면접': '면접 영어',
    '면접영어': '면접 영어',
    '면접 영어': '면접 영어',
    'interview': '면접 영어',
    '협상': '협상',
    'negotiation': '협상',
}


def parse_command(command_str):
    """
    Parse a command like "# 회의 영어 추천 50개#"
    Returns dict with category_ko, raw_category, count, recognized
    or None if unparsable.
    """
    match = COMMAND_PATTERN.search(command_str)
    if not match:
        return None

    raw_category = match.group(1).strip()
    count = int(match.group(2))
    count = min(count, 200)

    category = CATEGORY_ALIASES.get(raw_category)
    if category is None:
        for alias, canonical in CATEGORY_ALIASES.items():
            if raw_category in alias or alias in raw_category:
                category = canonical
                break

    return {
        "category_ko": category,
        "raw_category": raw_category,
        "count": count,
        "recognized": category is not None
    }
