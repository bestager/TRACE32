#!/usr/bin/env python3
"""
Cursor AI 사용 가이드 DOCX 생성 스크립트
초보자 대상 한글 문서 (10장 미만) - 스크린샷 참조 URL 포함 버전
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

def add_hyperlink(paragraph, url, text):
    """python-docx에 하이퍼링크를 추가하는 헬퍼 함수"""
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    c = OxmlElement('w:color')
    c.set(qn('w:val'), '0563C1')
    rPr.append(c)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), '20')
    rPr.append(sz)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return paragraph

def add_screenshot_ref(doc, label, url, description=None):
    """스크린샷 참조 링크를 문서에 추가"""
    p = doc.add_paragraph()
    run = p.add_run(f'📸 {label}: ')
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    add_hyperlink(p, url, url)
    if description:
        p2 = doc.add_paragraph()
        run2 = p2.add_run(f'   ({description})')
        run2.font.size = Pt(9)
        run2.font.italic = True
        run2.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

doc = Document()

# ─── 스타일 설정 ───
style = doc.styles['Normal']
font = style.font
font.name = 'Malgun Gothic'
font.size = Pt(11)

for i in range(1, 4):
    heading_style = doc.styles[f'Heading {i}']
    heading_style.font.name = 'Malgun Gothic'
    heading_style.font.color.rgb = RGBColor(0x7B, 0x2D, 0x8E)

# ─── 페이지 설정 ───
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

# ════════════════════════════════════════
# 표지 (1페이지)
# ════════════════════════════════════════
for _ in range(6):
    doc.add_paragraph('')

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('Cursor AI')
run.font.size = Pt(36)
run.font.bold = True
run.font.color.rgb = RGBColor(0x7B, 0x2D, 0x8E)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('초보자를 위한 사용 가이드')
run.font.size = Pt(20)
run.font.color.rgb = RGBColor(0x5F, 0x63, 0x68)

doc.add_paragraph('')

version = doc.add_paragraph()
version.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = version.add_run('2026년 3월 | v1.0')
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x80, 0x86, 0x8B)

desc = doc.add_paragraph()
desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = desc.add_run('경험 없는 초보자도 쉽게 따라할 수 있는 단계별 안내서')
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x80, 0x86, 0x8B)

doc.add_page_break()

# ════════════════════════════════════════
# 목차 (2페이지)
# ════════════════════════════════════════
doc.add_heading('목차', level=1)
doc.add_paragraph('')

toc_items = [
    ('1.', 'Cursor AI란?'),
    ('2.', '설치 전 준비사항'),
    ('3.', '설치 방법 (단계별 가이드)'),
    ('4.', '첫 실행 및 초기 설정'),
    ('5.', '화면 구성 이해하기'),
    ('6.', '핵심 기능 살펴보기'),
    ('7.', '첫 번째 프로젝트 만들기'),
    ('8.', '요금제 안내 & 자주 묻는 질문'),
]
for num, item in toc_items:
    p = doc.add_paragraph()
    run = p.add_run(f'{num}  {item}')
    run.font.size = Pt(13)

doc.add_page_break()

# ════════════════════════════════════════
# 1. Cursor AI란? (3페이지)
# ════════════════════════════════════════
doc.add_heading('1. Cursor AI란?', level=1)

doc.add_paragraph(
    'Cursor AI는 스타트업 Anysphere가 VS Code를 기반으로 만든 AI 네이티브 코드 에디터입니다. '
    'GitHub Copilot이나 Claude Code가 기존 에디터의 "플러그인"이라면, Cursor는 AI가 처음부터 '
    '내장된 독립형 IDE(통합 개발 환경)입니다. 자연어로 원하는 것을 설명하면 AI가 코드를 '
    '작성, 수정, 디버깅해줍니다.'
)

doc.add_heading('쉽게 이해하기', level=2)
doc.add_paragraph(
    'VS Code가 "코드를 직접 쓰는 편집기"라면, Cursor는 "AI에게 말로 설명하면 코드를 '
    '대신 써주는 편집기"입니다. 마치 옆에 숙련된 개발자 친구가 앉아서 도와주는 것과 같습니다.'
)

doc.add_heading('주요 특징 요약', level=2)

table = doc.add_table(rows=6, cols=2, style='Light Grid Accent 1')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.rows[0].cells[0].text = '특징'
table.rows[0].cells[1].text = '설명'
data = [
    ('VS Code 기반', 'VS Code의 모든 확장 프로그램과 호환, 익숙한 인터페이스'),
    ('AI 코드 자동완성', '전체 프로젝트 맥락을 이해하는 스마트 코드 완성 (Cursor Tab)'),
    ('에이전트 모드', 'AI가 여러 파일을 동시에 수정하고 터미널 명령까지 실행'),
    ('다중 AI 모델', 'Claude Sonnet 4, GPT-4o 등 다양한 AI 모델 선택 가능'),
    ('무료 사용 가능', '무료 Hobby 플랜으로 시작 가능 (월 50회 빠른 요청)'),
]
for i, (feature, desc_text) in enumerate(data):
    table.rows[i + 1].cells[0].text = feature
    table.rows[i + 1].cells[1].text = desc_text

doc.add_paragraph('')
add_screenshot_ref(doc, 'Cursor 공식 홈페이지',
    'https://cursor.com',
    '메인 페이지에서 Cursor의 전체 인터페이스와 기능 소개를 확인할 수 있습니다')

doc.add_page_break()

# ════════════════════════════════════════
# 2. 설치 전 준비사항 (4페이지)
# ════════════════════════════════════════
doc.add_heading('2. 설치 전 준비사항', level=1)

doc.add_paragraph('Cursor를 설치하기 전에 다음 항목들을 확인해주세요.')

doc.add_heading('시스템 요구사항', level=2)

table2 = doc.add_table(rows=5, cols=2, style='Light Grid Accent 1')
table2.alignment = WD_TABLE_ALIGNMENT.CENTER
table2.rows[0].cells[0].text = '항목'
table2.rows[0].cells[1].text = '요구사항'
reqs = [
    ('운영체제', 'Windows 10/11 (64비트), macOS 10.15 이상, 또는 Linux'),
    ('메모리(RAM)', '최소 4GB (8GB 이상 권장)'),
    ('디스크 공간', '최소 500MB 이상 여유 공간'),
    ('인터넷', 'AI 기능 사용 시 인터넷 연결 필수'),
]
for i, (item, req) in enumerate(reqs):
    table2.rows[i + 1].cells[0].text = item
    table2.rows[i + 1].cells[1].text = req

doc.add_paragraph('')
doc.add_heading('필수 준비물', level=2)

items = [
    '이메일 계정 — Google, GitHub, 또는 일반 이메일로 가입 가능',
    '안정적인 인터넷 연결',
    '(선택) 기존 VS Code가 설치되어 있다면 설정을 가져올 수 있습니다',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_paragraph('')
p = doc.add_paragraph()
run = p.add_run('💡 참고: Cursor는 VS Code 기반이므로, VS Code를 사용해본 적이 있다면 '
                '거의 동일한 환경에서 작업할 수 있습니다.')
run.font.bold = True
run.font.size = Pt(10)

doc.add_page_break()

# ════════════════════════════════════════
# 3. 설치 방법 (5페이지)
# ════════════════════════════════════════
doc.add_heading('3. 설치 방법 (단계별 가이드)', level=1)

# Step 1
doc.add_heading('Step 1: 다운로드 페이지 접속', level=2)
doc.add_paragraph(
    '웹 브라우저를 열고 cursor.com 에 접속합니다. '
    '메인 페이지에서 "Download" 버튼을 클릭합니다. '
    '운영체제가 자동으로 감지되어 맞는 설치 파일이 다운로드됩니다.'
)
add_screenshot_ref(doc, '다운로드 페이지',
    'https://www.cursor.com/downloads',
    'OS별 다운로드 버튼이 있는 공식 다운로드 페이지')

# Step 2
doc.add_heading('Step 2: 설치 프로그램 실행', level=2)
doc.add_paragraph(
    '다운로드된 설치 파일을 실행합니다.\n\n'
    '• Windows: .exe 파일 실행 → 설치 마법사를 따라 "다음" 클릭\n'
    '• macOS: .dmg 파일 열기 → Cursor 아이콘을 Applications 폴더로 드래그\n'
    '  (보안 경고가 나타나면: 시스템 환경설정 → 보안 및 개인 정보 → "확인 없이 열기" 클릭)\n'
    '• Linux: AppImage 또는 .deb 파일로 설치'
)
add_screenshot_ref(doc, '설치 과정 상세 가이드 (스크린샷 포함)',
    'https://learn-cursor.com/en/wiki/user-guide/install',
    'OS별 설치 과정의 단계별 스크린샷을 확인할 수 있습니다')

# Step 3
doc.add_heading('Step 3: 계정 생성 및 로그인', level=2)
doc.add_paragraph(
    'Cursor를 처음 실행하면 로그인 화면이 나타납니다.\n\n'
    '1. "Sign Up" 버튼을 클릭합니다.\n'
    '2. Google, GitHub, 또는 이메일 중 하나로 가입합니다.\n'
    '3. 가입이 완료되면 자동으로 무료 Hobby 플랜이 적용됩니다.'
)
add_screenshot_ref(doc, '첫 실행 및 로그인 가이드 (스크린샷 포함)',
    'https://daily.dev/blog/setup-cursor-first-time',
    '로그인 화면, 초기 설정 등 단계별 스크린샷이 포함된 상세 가이드')

# Step 4
doc.add_heading('Step 4: 초기 환경 설정', level=2)
doc.add_paragraph(
    'VS Code를 사용한 적이 있다면 "Import VS Code Extensions"를 선택하여 '
    '기존 테마, 키 바인딩, 확장 프로그램을 가져올 수 있습니다.\n\n'
    '초보자라면 "Start from Scratch (새로 시작)"를 선택하세요.\n'
    '이어서 밝은 테마(Light) 또는 어두운 테마(Dark)를 선택합니다.'
)
add_screenshot_ref(doc, '초기 설정 화면 상세 (스크린샷 포함)',
    'https://www.bannerbear.com/blog/how-to-get-started-with-cursor-ide-a-complete-setup-guide-for-developers/',
    'Import/Start from Scratch 선택 화면, 테마 선택 등 초기 설정 스크린샷')

doc.add_page_break()

# ════════════════════════════════════════
# 4. 첫 실행 및 초기 설정 (6페이지)
# ════════════════════════════════════════
doc.add_heading('4. 첫 실행 및 초기 설정', level=1)

doc.add_heading('코드베이스 인덱싱', level=2)
doc.add_paragraph(
    '프로젝트 폴더를 열면 Cursor가 자동으로 코드베이스를 인덱싱합니다. '
    '이 과정에서 AI가 프로젝트 구조, 파일 관계, 코드 패턴을 학습합니다. '
    '인덱싱이 완료되면 AI가 여러분의 프로젝트를 더 잘 이해하고 도와줄 수 있습니다.'
)

doc.add_heading('프로젝트별 설정 파일', level=2)
doc.add_paragraph(
    'Cursor에서는 프로젝트별로 AI의 동작을 커스텀할 수 있습니다.'
)

table3 = doc.add_table(rows=3, cols=2, style='Light Grid Accent 1')
table3.alignment = WD_TABLE_ALIGNMENT.CENTER
table3.rows[0].cells[0].text = '파일명'
table3.rows[0].cells[1].text = '설명'
table3.rows[1].cells[0].text = '.cursorrules'
table3.rows[1].cells[1].text = 'AI에게 프로젝트별 지침을 제공 (예: "TypeScript를 사용해줘")'
table3.rows[2].cells[0].text = '.cursorignore'
table3.rows[2].cells[1].text = 'AI 인덱싱에서 제외할 파일/폴더 지정 (예: node_modules, 빌드 결과물)'

doc.add_paragraph('')
p = doc.add_paragraph()
run = p.add_run('💡 초보자 팁: 처음에는 이 설정 파일 없이 시작해도 괜찮습니다. '
                '프로젝트가 커지면 그때 추가하세요.')
run.font.bold = True

doc.add_heading('AI 모델 선택', level=2)
doc.add_paragraph(
    'Cursor 설정(Settings → Models)에서 사용할 AI 모델을 선택할 수 있습니다.\n\n'
    '• Claude Sonnet 4: 코드 이해력과 생성 능력이 뛰어남 (기본 추천)\n'
    '• GPT-4o: OpenAI의 최신 모델\n'
    '• cursor-small: 빠른 응답이 필요할 때 (자동완성에 적합)\n\n'
    '초보자라면 기본 설정 그대로 사용하시면 됩니다.'
)

add_screenshot_ref(doc, 'AI 모델 설정 공식 문서',
    'https://docs.cursor.com/settings/models',
    'AI 모델 선택 및 설정 방법에 대한 공식 문서')

doc.add_page_break()

# ════════════════════════════════════════
# 5. 화면 구성 이해하기 (7페이지)
# ════════════════════════════════════════
doc.add_heading('5. 화면 구성 이해하기', level=1)

doc.add_paragraph(
    'Cursor는 VS Code와 거의 동일한 화면 구성에 AI 기능이 추가된 형태입니다.'
)

doc.add_heading('기본 화면 구성', level=2)
layout_items = [
    '사이드바 (왼쪽): 파일 탐색기, 검색, 소스 제어(Git), 확장 프로그램 관리',
    '편집 영역 (가운데): 코드를 작성하고 편집하는 주요 작업 공간',
    'AI 채팅 패널 (오른쪽): Cmd+L(Mac) / Ctrl+L(Windows)로 열기',
    '터미널 (하단): Ctrl+`로 열기, 명령어 직접 실행',
    '상태 표시줄 (최하단): 현재 AI 모델, 사용량 정보 표시',
]
for item in layout_items:
    doc.add_paragraph(item, style='List Bullet')

add_screenshot_ref(doc, 'Cursor 화면 구성 상세 (스크린샷 포함)',
    'https://docs.cursor.com/get-started/overview',
    'Cursor의 전체 화면 레이아웃 및 각 영역 설명')

doc.add_heading('AI 모드 종류', level=2)
doc.add_paragraph('Cursor의 AI 채팅에는 4가지 모드가 있습니다.')

table4 = doc.add_table(rows=5, cols=3, style='Light Grid Accent 1')
table4.alignment = WD_TABLE_ALIGNMENT.CENTER
table4.rows[0].cells[0].text = '모드'
table4.rows[0].cells[1].text = '설명'
table4.rows[0].cells[2].text = '적합한 상황'
modes = [
    ('Agent (기본)', '파일 수정, 터미널 명령 등 자율적으로 수행', '복잡한 기능 개발, 다중 파일 수정'),
    ('Plan', '코드 작성 전 계획을 먼저 제시', '대규모 작업의 전략 수립'),
    ('Debug', '에러 분석 및 수정 제안', '버그 수정, 오류 해결'),
    ('Ask', '읽기 전용, 코드에 대한 질문/답변만', '코드 이해, 학습 목적'),
]
for i, (mode, desc_text, situation) in enumerate(modes):
    table4.rows[i + 1].cells[0].text = mode
    table4.rows[i + 1].cells[1].text = desc_text
    table4.rows[i + 1].cells[2].text = situation

add_screenshot_ref(doc, 'AI 모드 공식 문서',
    'https://docs.cursor.com/chat/overview',
    '각 AI 모드의 상세 설명과 사용법')

doc.add_page_break()

# ════════════════════════════════════════
# 6. 핵심 기능 살펴보기 (8페이지)
# ════════════════════════════════════════
doc.add_heading('6. 핵심 기능 살펴보기', level=1)

doc.add_heading('6-1. Cursor Tab (AI 자동완성)', level=2)
doc.add_paragraph(
    '코드를 타이핑하면 AI가 다음에 올 코드를 자동으로 제안합니다.\n\n'
    '• Tab 키: 제안을 수락\n'
    '• Esc 키: 제안을 취소\n'
    '• 일반 자동완성과 다른 점: 프로젝트 전체 맥락을 이해하여 더 정확한 제안을 합니다.'
)
add_screenshot_ref(doc, 'Cursor Tab 기능 상세 (스크린샷 포함)',
    'https://docs.cursor.com/tab/overview',
    'Cursor Tab 자동완성 기능의 동작 방식과 스크린샷')

doc.add_heading('6-2. 인라인 편집 (Cmd+K / Ctrl+K)', level=2)
doc.add_paragraph(
    '코드를 수정하고 싶을 때 사용하는 기능입니다.\n\n'
    '1. 수정하고 싶은 코드를 마우스로 선택합니다.\n'
    '2. Cmd+K (Mac) 또는 Ctrl+K (Windows)를 누릅니다.\n'
    '3. 작은 입력창이 나타나면 원하는 수정 내용을 자연어로 입력합니다.\n'
    '   예: "이 함수에 에러 처리를 추가해줘"\n'
    '4. AI가 선택 영역을 자동으로 수정합니다.'
)
add_screenshot_ref(doc, 'Cmd+K 인라인 편집 상세',
    'https://docs.cursor.com/cmdk/overview',
    'Cmd+K 기능의 사용법 및 인라인 편집 스크린샷')

doc.add_heading('6-3. AI 채팅 (Cmd+L / Ctrl+L)', level=2)
doc.add_paragraph(
    '채팅 패널에서 AI와 대화하며 코드를 작성할 수 있습니다.\n\n'
    '예시 명령어:\n'
    '• "이 코드가 무슨 일을 하는지 설명해줘"\n'
    '• "로그인 API 엔드포인트를 만들어줘"\n'
    '• "이 함수의 버그를 찾아줘"\n'
    '• "단위 테스트를 작성해줘"\n\n'
    'AI가 코드를 제안하면 "Apply" 버튼을 클릭하여 파일에 바로 적용할 수 있습니다.'
)

doc.add_heading('6-4. 멘션(@) 기능', level=2)
doc.add_paragraph(
    '채팅에서 "@"를 입력하면 다양한 컨텍스트를 참조할 수 있습니다.\n\n'
    '• @파일명: 특정 파일의 내용을 AI에게 전달\n'
    '• @폴더명: 특정 폴더의 구조를 AI에게 전달\n'
    '• @웹주소: 웹 페이지 내용을 참조\n'
    '• @Docs: 공식 문서를 참조하여 답변\n\n'
    '예시: "@index.html 이 파일에 다크모드 토글 버튼을 추가해줘"'
)
add_screenshot_ref(doc, '@ 멘션 및 컨텍스트 기능 상세',
    'https://docs.cursor.com/chat/context',
    '채팅에서 @ 기호로 파일, 폴더, 웹 등을 참조하는 방법 스크린샷')

doc.add_heading('6-5. 에이전트 모드', level=2)
doc.add_paragraph(
    'Agent 모드에서는 AI가 자율적으로 복잡한 작업을 수행합니다.\n\n'
    '• 여러 파일을 동시에 생성/수정\n'
    '• 터미널 명령어 실행 (npm install, git commit 등)\n'
    '• 에러 발생 시 자동으로 디버깅 및 재시도\n'
    '• 작업 진행 상황을 실시간으로 표시'
)
add_screenshot_ref(doc, 'Agent 모드 공식 문서',
    'https://docs.cursor.com/chat/agent',
    'Agent 모드의 동작 방식과 기능 스크린샷')

doc.add_page_break()

# ════════════════════════════════════════
# 7. 첫 번째 프로젝트 만들기 (9페이지)
# ════════════════════════════════════════
doc.add_heading('7. 첫 번째 프로젝트 만들기', level=1)

doc.add_paragraph('실제로 간단한 프로젝트를 만들어보며 Cursor를 체험해봅시다.')

doc.add_heading('예제: 간단한 계산기 웹앱 만들기', level=2)

doc.add_heading('Step 1: 프로젝트 폴더 열기', level=3)
doc.add_paragraph(
    '1. Cursor를 실행합니다.\n'
    '2. File → Open Folder를 클릭합니다.\n'
    '3. 새 폴더를 만들고 "my-calculator"라고 이름을 지어줍니다.\n'
    '4. 해당 폴더를 선택하여 엽니다.'
)

doc.add_heading('Step 2: AI 채팅에서 작업 지시', level=3)
doc.add_paragraph(
    'Cmd+L (Mac) 또는 Ctrl+L (Windows)를 눌러 AI 채팅을 엽니다.\n\n'
    '다음과 같이 입력합니다:\n\n'
    '"간단한 계산기 웹앱을 만들어줘. HTML, CSS, JavaScript로 만들어줘. '
    '사칙연산(더하기, 빼기, 곱하기, 나누기)이 가능하고, '
    '깔끔한 UI로 만들어줘."'
)

doc.add_heading('Step 3: AI의 응답 확인 및 적용', level=3)
doc.add_paragraph(
    'AI가 코드를 생성하면:\n\n'
    '1. 채팅 창에서 생성된 코드를 확인합니다.\n'
    '2. 코드 블록 옆의 "Apply" 버튼을 클릭합니다.\n'
    '3. 파일이 자동으로 생성되고 코드가 적용됩니다.\n'
    '4. Agent 모드에서는 파일 생성까지 자동으로 처리됩니다.'
)

doc.add_heading('Step 4: 결과 확인 및 수정', level=3)
doc.add_paragraph(
    '1. 생성된 index.html 파일을 우클릭 → "Open with Live Server" 또는\n'
    '   터미널에서 직접 브라우저로 열기\n'
    '2. 계산기가 제대로 동작하는지 테스트합니다.\n'
    '3. 수정이 필요하면 AI에게 추가 지시합니다.\n'
    '   예: "배경색을 파란색으로 바꿔줘" 또는 "퍼센트 계산 기능도 추가해줘"'
)

add_screenshot_ref(doc, '초보자 실습 튜토리얼 (영상 포함)',
    'https://www.codecademy.com/article/how-to-use-cursor-ai-a-complete-guide-with-practical-examples',
    'Cursor를 활용한 실전 프로젝트 예제와 단계별 스크린샷')
add_screenshot_ref(doc, 'Cursor 초보자 튜토리얼 2026',
    'https://www.nxcode.io/resources/news/cursor-tutorial-beginners-2026',
    '2026년 최신 Cursor 초보자 가이드 (스크린샷 다수 포함)')

doc.add_page_break()

# ════════════════════════════════════════
# 8. 요금제 안내 & FAQ (10페이지 - 마지막)
# ════════════════════════════════════════
doc.add_heading('8. 요금제 안내 & 자주 묻는 질문', level=1)

doc.add_heading('요금제 비교', level=2)

table5 = doc.add_table(rows=4, cols=3, style='Light Grid Accent 1')
table5.alignment = WD_TABLE_ALIGNMENT.CENTER
table5.rows[0].cells[0].text = '플랜'
table5.rows[0].cells[1].text = '가격'
table5.rows[0].cells[2].text = '주요 내용'
plans = [
    ('Hobby (무료)', '무료', '월 50회 프리미엄 요청, 기본 자동완성'),
    ('Pro', '월 $20', '무제한 자동완성, 월 500회 프리미엄 요청, 모든 AI 모델'),
    ('Business', '월 $40/인', 'Pro 기능 + 팀 관리, 개인정보 보호 모드, 중앙 관리'),
]
for i, (plan, price, desc_text) in enumerate(plans):
    table5.rows[i + 1].cells[0].text = plan
    table5.rows[i + 1].cells[1].text = price
    table5.rows[i + 1].cells[2].text = desc_text

doc.add_paragraph('')
add_screenshot_ref(doc, '요금제 상세 비교 페이지',
    'https://www.cursor.com/pricing',
    '각 플랜의 상세 기능 비교 및 최신 가격 정보')

p = doc.add_paragraph()
run = p.add_run('💡 초보자 팁: 무료 Hobby 플랜으로 시작하세요! '
                '월 50회 요청만으로도 학습용으로 충분합니다.')
run.font.bold = True

doc.add_paragraph('')
doc.add_heading('주요 단축키 모음', level=2)

table6 = doc.add_table(rows=6, cols=3, style='Light Grid Accent 1')
table6.alignment = WD_TABLE_ALIGNMENT.CENTER
table6.rows[0].cells[0].text = '기능'
table6.rows[0].cells[1].text = 'Mac'
table6.rows[0].cells[2].text = 'Windows'
shortcuts = [
    ('AI 채팅 열기', 'Cmd + L', 'Ctrl + L'),
    ('인라인 편집', 'Cmd + K', 'Ctrl + K'),
    ('자동완성 수락', 'Tab', 'Tab'),
    ('자동완성 취소', 'Esc', 'Esc'),
    ('터미널 열기', 'Ctrl + `', 'Ctrl + `'),
]
for i, (func, mac, win) in enumerate(shortcuts):
    table6.rows[i + 1].cells[0].text = func
    table6.rows[i + 1].cells[1].text = mac
    table6.rows[i + 1].cells[2].text = win

doc.add_paragraph('')
doc.add_heading('자주 묻는 질문 (FAQ)', level=2)

faqs = [
    ('Q: Cursor는 VS Code와 무엇이 다른가요?',
     'A: Cursor는 VS Code를 기반(포크)으로 만들어져 외형은 비슷하지만, '
     'AI 기능이 처음부터 내장되어 있어 별도의 확장 프로그램 없이 AI 코딩이 가능합니다.'),
    ('Q: 프로그래밍을 전혀 몰라도 사용할 수 있나요?',
     'A: 네! AI에게 자연어로 지시하면 코드를 생성해줍니다. '
     '다만 기초 개념을 알면 AI의 결과물을 더 잘 이해하고 활용할 수 있습니다.'),
    ('Q: 한국어로 대화할 수 있나요?',
     'A: 네, Cursor의 AI는 한국어를 완벽하게 이해합니다. '
     '편하게 한국어로 작업을 지시하세요.'),
    ('Q: VS Code 확장 프로그램을 사용할 수 있나요?',
     'A: 네, Cursor는 VS Code 기반이므로 대부분의 VS Code 확장 프로그램과 호환됩니다.'),
    ('Q: 인터넷 없이도 사용할 수 있나요?',
     'A: 기본 코드 편집은 오프라인에서 가능하지만, AI 기능(자동완성, 채팅 등)은 '
     '인터넷 연결이 필요합니다.'),
]
for question, answer in faqs:
    p = doc.add_paragraph()
    run = p.add_run(question)
    run.font.bold = True
    doc.add_paragraph(answer)

doc.add_paragraph('')

# 참고 자료
doc.add_heading('참고 자료 (스크린샷 포함 가이드)', level=2)
refs = [
    ('공식 웹사이트', 'https://cursor.com'),
    ('공식 문서 (스크린샷 포함)', 'https://docs.cursor.com'),
    ('초보자 설치 가이드 (상세 스크린샷)', 'https://daily.dev/blog/setup-cursor-first-time'),
    ('완전 초보자 설정 가이드 (스크린샷 포함)', 'https://www.bannerbear.com/blog/how-to-get-started-with-cursor-ide-a-complete-setup-guide-for-developers/'),
    ('Codecademy 실전 가이드', 'https://www.codecademy.com/article/how-to-use-cursor-ai-a-complete-guide-with-practical-examples'),
    ('2026 최신 초보자 튜토리얼', 'https://www.nxcode.io/resources/news/cursor-tutorial-beginners-2026'),
    ('Cursor 포럼 (커뮤니티)', 'https://forum.cursor.com'),
]
for label, url in refs:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(f'{label}: ')
    run.font.bold = True
    add_hyperlink(p, url, url)

# ─── 저장 ───
output_path = '/home/user/TRACE32/Cursor_AI_사용가이드_초보자용.docx'
doc.save(output_path)
print(f'문서가 성공적으로 생성되었습니다: {output_path}')
