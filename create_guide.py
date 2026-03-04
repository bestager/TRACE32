#!/usr/bin/env python3
"""
Google Antigravity 사용 가이드 DOCX 생성 스크립트
초보자 대상 한글 문서 (10장 미만)
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

# ─── 스타일 설정 ───
style = doc.styles['Normal']
font = style.font
font.name = 'Malgun Gothic'
font.size = Pt(11)

for i in range(1, 4):
    heading_style = doc.styles[f'Heading {i}']
    heading_style.font.name = 'Malgun Gothic'
    heading_style.font.color.rgb = RGBColor(0x1A, 0x73, 0xE8)  # Google Blue

# ─── 페이지 설정 ───
sections = doc.sections
for section in sections:
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
run = title.add_run('Google Antigravity')
run.font.size = Pt(36)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1A, 0x73, 0xE8)

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
    ('1.', 'Google Antigravity란?'),
    ('2.', '설치 전 준비사항'),
    ('3.', '설치 방법 (단계별 가이드)'),
    ('4.', '첫 실행 및 초기 설정'),
    ('5.', '화면 구성 이해하기'),
    ('6.', '핵심 기능 살펴보기'),
    ('7.', '첫 번째 프로젝트 만들기'),
    ('8.', '유용한 팁 & 자주 묻는 질문'),
]
for num, item in toc_items:
    p = doc.add_paragraph()
    run = p.add_run(f'{num}  {item}')
    run.font.size = Pt(13)

doc.add_page_break()

# ════════════════════════════════════════
# 1. Google Antigravity란? (3페이지)
# ════════════════════════════════════════
doc.add_heading('1. Google Antigravity란?', level=1)

doc.add_paragraph(
    'Google Antigravity(구글 안티그래비티)는 2025년 11월 Google DeepMind가 공개한 '
    'AI 기반 통합 개발 환경(IDE)입니다. 기존의 코드 편집기와 달리, AI 에이전트가 '
    '직접 코드를 작성하고, 테스트하고, 디버깅까지 해주는 혁신적인 개발 도구입니다.'
)

doc.add_heading('쉽게 이해하기', level=2)
doc.add_paragraph(
    '일반적인 코드 편집기(예: VS Code)가 "똑똑한 메모장"이라면, '
    'Antigravity는 "AI 개발 파트너"입니다. 여러분이 "로그인 페이지를 만들어줘"라고 '
    '말하면, AI가 직접 코드를 작성하고 실행까지 해줍니다.'
)

doc.add_heading('주요 특징 요약', level=2)

table = doc.add_table(rows=5, cols=2, style='Light Grid Accent 1')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = table.rows[0].cells
headers[0].text = '특징'
headers[1].text = '설명'
data = [
    ('에이전트 중심 개발', 'AI가 코드 작성, 테스트, 디버깅을 자율적으로 수행'),
    ('무료 사용', 'Preview 기간 동안 무료로 사용 가능'),
    ('다중 모델 지원', 'Gemini 3 Pro, Claude, GPT 등 다양한 AI 모델 선택 가능'),
    ('브라우저 통합', 'AI가 직접 웹 브라우저를 제어하여 테스트 자동화'),
]
for i, (feature, desc_text) in enumerate(data):
    row = table.rows[i + 1].cells
    row[0].text = feature
    row[1].text = desc_text

# 스크린샷 안내
doc.add_paragraph('')
p = doc.add_paragraph()
run = p.add_run('[스크린샷] Google Antigravity 공식 홈페이지 (antigravity.google)')
run.font.italic = True
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_page_break()

# ════════════════════════════════════════
# 2. 설치 전 준비사항 (4페이지)
# ════════════════════════════════════════
doc.add_heading('2. 설치 전 준비사항', level=1)

doc.add_paragraph('Antigravity를 설치하기 전에 다음 항목들을 확인해주세요.')

doc.add_heading('시스템 요구사항', level=2)

table2 = doc.add_table(rows=5, cols=2, style='Light Grid Accent 1')
table2.alignment = WD_TABLE_ALIGNMENT.CENTER
table2.rows[0].cells[0].text = '항목'
table2.rows[0].cells[1].text = '요구사항'
reqs = [
    ('운영체제', 'Windows 10 이상, macOS 12 이상, 또는 Ubuntu 20.04 이상'),
    ('메모리(RAM)', '최소 8GB (16GB 권장)'),
    ('디스크 공간', '최소 2GB 이상 여유 공간'),
    ('인터넷', '안정적인 인터넷 연결 필수'),
]
for i, (item, req) in enumerate(reqs):
    table2.rows[i + 1].cells[0].text = item
    table2.rows[i + 1].cells[1].text = req

doc.add_paragraph('')
doc.add_heading('필수 준비물', level=2)

items = [
    'Google 개인 계정 (Gmail) — 업무용(Workspace) 계정은 아직 지원되지 않습니다',
    'Chrome 웹 브라우저 (최신 버전 권장)',
    '안정적인 인터넷 연결',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_paragraph('')
p = doc.add_paragraph()
run = p.add_run('⚠ 참고: 업무용 Google Workspace 계정은 현재 지원되지 않습니다. '
                '반드시 개인 Gmail 계정으로 로그인해야 합니다.')
run.font.bold = True
run.font.size = Pt(10)

doc.add_page_break()

# ════════════════════════════════════════
# 3. 설치 방법 (5페이지)
# ════════════════════════════════════════
doc.add_heading('3. 설치 방법 (단계별 가이드)', level=1)

steps = [
    ('Step 1: 다운로드 페이지 접속',
     '웹 브라우저를 열고 antigravity.google 에 접속합니다. '
     '메인 페이지에서 "Download" 버튼을 클릭합니다.',
     '[스크린샷] antigravity.google 메인 페이지의 Download 버튼 위치'),

    ('Step 2: 운영체제 선택',
     '본인의 운영체제(Windows, macOS, Linux)를 선택합니다. '
     '운영체제에 맞는 설치 파일이 자동으로 다운로드됩니다.',
     '[스크린샷] 운영체제 선택 화면'),

    ('Step 3: 설치 프로그램 실행',
     '다운로드된 설치 파일을 더블클릭하여 실행합니다.\n'
     '• Windows: .exe 파일 실행 → "다음" 클릭하여 설치 진행\n'
     '• macOS: .dmg 파일 열기 → Applications 폴더로 드래그\n'
     '• Linux: .deb 또는 .rpm 패키지 설치',
     '[스크린샷] 설치 진행 화면'),

    ('Step 4: 설치 완료 및 실행',
     '설치가 완료되면 Antigravity를 실행합니다. '
     '처음 실행 시 기존 VS Code 또는 Cursor 설정을 가져올지 묻는 화면이 나타납니다. '
     '초보자라면 "Start Fresh (새로 시작)"를 선택하세요.',
     '[스크린샷] 초기 설정 선택 화면 (Import / Start Fresh)'),
]

for title, content, screenshot in steps:
    doc.add_heading(title, level=2)
    doc.add_paragraph(content)
    p = doc.add_paragraph()
    run = p.add_run(screenshot)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_page_break()

# ════════════════════════════════════════
# 4. 첫 실행 및 초기 설정 (6페이지)
# ════════════════════════════════════════
doc.add_heading('4. 첫 실행 및 초기 설정', level=1)

doc.add_heading('개발 모드 선택', level=2)
doc.add_paragraph(
    '처음 실행하면 개발 모드를 선택하라는 화면이 나타납니다. '
    '각 모드의 차이는 다음과 같습니다.'
)

table3 = doc.add_table(rows=4, cols=3, style='Light Grid Accent 1')
table3.alignment = WD_TABLE_ALIGNMENT.CENTER
table3.rows[0].cells[0].text = '모드'
table3.rows[0].cells[1].text = '설명'
table3.rows[0].cells[2].text = '추천 대상'

modes = [
    ('Agent-driven\n(에이전트 주도)', 'AI가 모든 작업을 자동으로 수행', '경험 있는 개발자'),
    ('Agent-assisted\n(에이전트 보조) ★추천', 'AI가 도와주되, 중요한 작업은 사용자 확인', '초보자에게 추천!'),
    ('Review-driven\n(검토 주도)', 'AI가 모든 작업 전에 사용자 승인 요청', '보안이 중요한 경우'),
]
for i, (mode, desc_text, target) in enumerate(modes):
    table3.rows[i + 1].cells[0].text = mode
    table3.rows[i + 1].cells[1].text = desc_text
    table3.rows[i + 1].cells[2].text = target

doc.add_paragraph('')
p = doc.add_paragraph()
run = p.add_run('💡 초보자 팁: "Agent-assisted (에이전트 보조)" 모드를 선택하세요! '
                'AI가 도와주면서도 중요한 결정은 여러분이 직접 할 수 있습니다.')
run.font.bold = True

doc.add_paragraph('')
p = doc.add_paragraph()
run = p.add_run('[스크린샷] 개발 모드 선택 화면')
run.font.italic = True
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_heading('Google 계정 로그인', level=2)
doc.add_paragraph(
    '모드를 선택한 후 Google 계정으로 로그인합니다.\n\n'
    '1. "Sign in with Google" 버튼을 클릭합니다.\n'
    '2. Chrome 브라우저가 자동으로 열리며 Google 로그인 페이지가 나타납니다.\n'
    '3. 개인 Gmail 계정으로 로그인합니다.\n'
    '4. 권한 허용 화면에서 "허용"을 클릭합니다.\n'
    '5. "인증 완료" 메시지가 나타나면 Antigravity로 돌아갑니다.'
)

p = doc.add_paragraph()
run = p.add_run('[스크린샷] Google 로그인 및 권한 허용 화면')
run.font.italic = True
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_page_break()

# ════════════════════════════════════════
# 5. 화면 구성 이해하기 (7페이지)
# ════════════════════════════════════════
doc.add_heading('5. 화면 구성 이해하기', level=1)

doc.add_paragraph(
    'Antigravity는 크게 두 가지 화면으로 구성되어 있습니다.'
)

doc.add_heading('① 에디터 뷰 (Editor View)', level=2)
doc.add_paragraph(
    '일반적인 코드 편집기와 비슷한 화면입니다. '
    'VS Code를 사용해본 적이 있다면 익숙한 구조입니다.'
)
editor_features = [
    '파일 탐색기: 왼쪽 사이드바에서 프로젝트 파일을 탐색',
    '코드 편집 영역: 가운데 영역에서 코드를 작성하고 편집',
    'AI 채팅 패널: 오른쪽 또는 하단에서 AI와 대화하며 작업 지시',
    '터미널: 하단에서 명령어를 직접 실행',
    '탭 자동완성: AI가 코드를 작성할 때 자동으로 다음 코드를 제안',
]
for f in editor_features:
    doc.add_paragraph(f, style='List Bullet')

p = doc.add_paragraph()
run = p.add_run('[스크린샷] 에디터 뷰 전체 화면 구성')
run.font.italic = True
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_heading('② 매니저 뷰 (Manager View / Agent Manager)', level=2)
doc.add_paragraph(
    'Antigravity만의 독자적인 화면입니다. 여러 AI 에이전트를 동시에 관리할 수 있는 '
    '"미션 컨트롤" 대시보드입니다.'
)
manager_features = [
    '에이전트 목록: 현재 실행 중인 AI 에이전트들의 상태를 한눈에 확인',
    '인박스: AI가 여러분의 승인이 필요할 때 알림이 표시되는 곳',
    '작업 진행 상황: 각 에이전트의 작업 진행률을 실시간으로 확인',
    'Artifacts: AI가 생성한 결과물(계획서, 스크린샷, 녹화 등)을 확인',
]
for f in manager_features:
    doc.add_paragraph(f, style='List Bullet')

p = doc.add_paragraph()
run = p.add_run('[스크린샷] 매니저 뷰 (Agent Manager) 대시보드')
run.font.italic = True
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_page_break()

# ════════════════════════════════════════
# 6. 핵심 기능 살펴보기 (8페이지)
# ════════════════════════════════════════
doc.add_heading('6. 핵심 기능 살펴보기', level=1)

doc.add_heading('6-1. AI 에이전트에게 작업 지시하기', level=2)
doc.add_paragraph(
    'AI 채팅 패널에서 자연어로 원하는 작업을 설명하면, AI가 자동으로 코드를 작성합니다.\n\n'
    '예시 명령어:\n'
    '• "간단한 할 일 목록 웹앱을 만들어줘"\n'
    '• "이 코드에서 버그를 찾아서 수정해줘"\n'
    '• "로그인 기능을 추가해줘"\n'
    '• "이 함수에 대한 테스트 코드를 작성해줘"'
)

doc.add_heading('6-2. Planning 모드 vs Fast 모드', level=2)

table4 = doc.add_table(rows=3, cols=3, style='Light Grid Accent 1')
table4.alignment = WD_TABLE_ALIGNMENT.CENTER
table4.rows[0].cells[0].text = '모드'
table4.rows[0].cells[1].text = '동작 방식'
table4.rows[0].cells[2].text = '적합한 상황'
table4.rows[1].cells[0].text = 'Planning 모드'
table4.rows[1].cells[1].text = '코드 작성 전에 상세 계획을 먼저 제시'
table4.rows[1].cells[2].text = '복잡한 기능 개발, 대규모 프로젝트'
table4.rows[2].cells[0].text = 'Fast 모드'
table4.rows[2].cells[1].text = '계획 없이 바로 코드 작성 시작'
table4.rows[2].cells[2].text = '간단한 수정, 빠른 프로토타이핑'

doc.add_heading('6-3. 브라우저 통합 (Browser Agent)', level=2)
doc.add_paragraph(
    'AI가 직접 Chrome 브라우저를 제어하여 여러분이 만든 앱을 테스트합니다.\n\n'
    '1. AI에게 "내 앱을 브라우저에서 테스트해줘"라고 말합니다.\n'
    '2. Chrome 창이 열리며 "Agent Control" 테두리가 표시됩니다.\n'
    '3. AI가 버튼 클릭, 폼 입력, 스크롤 등을 자동으로 수행합니다.\n'
    '4. 테스트 결과를 스크린샷과 영상으로 보여줍니다.'
)

p = doc.add_paragraph()
run = p.add_run('[스크린샷] Browser Agent가 앱을 테스트하는 모습')
run.font.italic = True
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_heading('6-4. 다중 AI 모델 지원', level=2)
doc.add_paragraph(
    'Antigravity는 여러 AI 모델을 지원하므로, 작업에 따라 최적의 모델을 선택할 수 있습니다.'
)
models = [
    'Gemini 3 Pro (High): 복잡한 코딩 작업에 적합 (기본 모델)',
    'Gemini 3 Pro (Low): 빠른 응답이 필요할 때',
    'Claude Sonnet 4.6: Anthropic의 AI 모델',
    'GPT-OSS 120B: OpenAI 기반 오픈소스 모델',
]
for m in models:
    doc.add_paragraph(m, style='List Bullet')

doc.add_page_break()

# ════════════════════════════════════════
# 7. 첫 번째 프로젝트 만들기 (9페이지)
# ════════════════════════════════════════
doc.add_heading('7. 첫 번째 프로젝트 만들기', level=1)

doc.add_paragraph('실제로 간단한 프로젝트를 만들어보며 Antigravity를 체험해봅시다.')

doc.add_heading('예제: 간단한 할 일 목록(Todo) 웹앱 만들기', level=2)

doc.add_heading('Step 1: 새 프로젝트 생성', level=3)
doc.add_paragraph(
    '1. 상단 메뉴에서 File → New Window를 클릭합니다.\n'
    '2. "Open Folder" 버튼을 클릭하여 프로젝트를 저장할 폴더를 선택합니다.\n'
    '3. 새 폴더를 만들고 "my-todo-app"이라고 이름을 지어줍니다.'
)

doc.add_heading('Step 2: AI에게 작업 지시', level=3)
doc.add_paragraph(
    'AI 채팅 패널에 다음과 같이 입력합니다:\n\n'
    '"간단한 할 일 목록 웹앱을 만들어줘. HTML, CSS, JavaScript로 만들어줘. '
    '할 일 추가, 완료 체크, 삭제 기능이 있으면 좋겠어."'
)

doc.add_heading('Step 3: AI의 작업 확인', level=3)
doc.add_paragraph(
    'AI가 Planning 모드에서 먼저 계획을 제시합니다:\n'
    '• 어떤 파일들을 만들 것인지\n'
    '• 각 파일의 역할은 무엇인지\n'
    '• 어떤 순서로 작업할 것인지\n\n'
    '계획을 확인하고 "승인(Approve)"을 클릭하면 AI가 코드를 작성하기 시작합니다.'
)

doc.add_heading('Step 4: 결과 확인', level=3)
doc.add_paragraph(
    'AI가 코드 작성을 완료하면:\n'
    '1. 에디터에서 생성된 파일들을 확인합니다.\n'
    '2. AI에게 "브라우저에서 열어줘"라고 말합니다.\n'
    '3. 완성된 할 일 목록 앱이 브라우저에 표시됩니다!'
)

p = doc.add_paragraph()
run = p.add_run('[스크린샷] 완성된 Todo 앱이 브라우저에서 실행되는 모습')
run.font.italic = True
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_page_break()

# ════════════════════════════════════════
# 8. 유용한 팁 & FAQ (10페이지 - 마지막)
# ════════════════════════════════════════
doc.add_heading('8. 유용한 팁 & 자주 묻는 질문', level=1)

doc.add_heading('초보자를 위한 팁', level=2)

tips = [
    ('구체적으로 지시하세요',
     '"앱 만들어줘"보다 "HTML/CSS/JS로 할 일 목록 앱을 만들어줘. '
     '추가, 삭제, 완료 기능이 있어야 해"처럼 구체적으로 말할수록 좋은 결과를 얻습니다.'),
    ('Planning 모드를 활용하세요',
     '복잡한 작업일수록 Planning 모드를 사용하여 AI의 계획을 먼저 확인하고 '
     '승인하는 것이 안전합니다.'),
    ('한국어로 대화하세요',
     'Antigravity는 한국어 프롬프트를 완벽하게 지원합니다. '
     '편하게 한국어로 작업을 지시하세요.'),
    ('여러 에이전트를 활용하세요',
     '매니저 뷰에서 여러 에이전트를 동시에 실행할 수 있습니다. '
     '예를 들어 한 에이전트는 코드를 작성하고, 다른 에이전트는 테스트를 실행할 수 있습니다.'),
]
for tip_title, tip_desc in tips:
    p = doc.add_paragraph()
    run = p.add_run(f'✅ {tip_title}: ')
    run.font.bold = True
    p.add_run(tip_desc)

doc.add_paragraph('')
doc.add_heading('자주 묻는 질문 (FAQ)', level=2)

faqs = [
    ('Q: Antigravity는 무료인가요?',
     'A: 현재 Public Preview 기간으로 무료 사용이 가능합니다. Google AI Plan을 구독하면 '
     '더 많은 사용량이 제공됩니다.'),
    ('Q: 프로그래밍을 전혀 몰라도 사용할 수 있나요?',
     'A: 네! AI에게 자연어로 지시하면 되므로 프로그래밍 지식이 없어도 기본적인 앱을 '
     '만들 수 있습니다. 다만, 기초 개념을 알면 더 효과적으로 활용할 수 있습니다.'),
    ('Q: 회사 계정으로 사용할 수 있나요?',
     'A: 현재는 개인 Gmail 계정만 지원됩니다. Google Workspace 계정 지원은 추후 예정입니다.'),
    ('Q: VS Code 확장 프로그램을 사용할 수 있나요?',
     'A: Antigravity는 VS Code 기반이므로 대부분의 VS Code 확장 프로그램과 호환됩니다.'),
    ('Q: 인터넷 없이도 사용할 수 있나요?',
     'A: AI 기능을 사용하려면 인터넷 연결이 필요합니다. 단, 기본 코드 편집은 오프라인에서도 가능합니다.'),
]
for question, answer in faqs:
    p = doc.add_paragraph()
    run = p.add_run(question)
    run.font.bold = True
    doc.add_paragraph(answer)

doc.add_paragraph('')
doc.add_paragraph('')

# 참고 자료
doc.add_heading('참고 자료', level=2)
refs = [
    '공식 웹사이트: antigravity.google',
    '공식 문서: antigravity.google/docs',
    '시작 가이드 (Codelab): codelabs.developers.google.com/getting-started-google-antigravity',
    'Google 공식 블로그: developers.googleblog.com',
]
for ref in refs:
    doc.add_paragraph(ref, style='List Bullet')

# ─── 저장 ───
output_path = '/home/user/TRACE32/Google_Antigravity_사용가이드_초보자용.docx'
doc.save(output_path)
print(f'문서가 성공적으로 생성되었습니다: {output_path}')
