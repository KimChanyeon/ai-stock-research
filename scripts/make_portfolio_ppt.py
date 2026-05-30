#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock Agent Hub 포트폴리오 PPT 생성 스크립트
- 화면 캡처 / 소스 코드 삽입용 플레이스홀더 영역 포함
- 16:9 와이드 슬라이드
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ── 색상 팔레트 ────────────────────────────────────────────
NAVY     = RGBColor(0x0F, 0x17, 0x2A)   # 타이틀 배경
SLATE    = RGBColor(0x1E, 0x29, 0x3B)   # 본문 진한 텍스트
SLATE2   = RGBColor(0x47, 0x55, 0x69)   # 보조 텍스트
GRAY     = RGBColor(0x94, 0xA3, 0xB8)   # 흐린 텍스트
LIGHT    = RGBColor(0xF8, 0xFA, 0xFC)   # 카드 배경
LINE     = RGBColor(0xE2, 0xE8, 0xF0)   # 경계선
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
BLUE     = RGBColor(0x25, 0x63, 0xEB)   # 메인 액센트
BLUE_DK  = RGBColor(0x03, 0x69, 0xA1)
SKY      = RGBColor(0xE0, 0xF2, 0xFE)   # 연한 파랑 배경
AMBER    = RGBColor(0xF5, 0x9E, 0x0B)   # 진행/강조
AMBER_BG = RGBColor(0xFF, 0xFB, 0xEB)
GREEN    = RGBColor(0x16, 0xA3, 0x4A)
GREEN_BG = RGBColor(0xDC, 0xFC, 0xE7)
RED      = RGBColor(0xDC, 0x26, 0x26)
RED_BG   = RGBColor(0xFE, 0xE2, 0xE2)
PURPLE   = RGBColor(0x63, 0x66, 0xF1)

FONT = "Apple SD Gothic Neo"   # macOS 한글 폰트 (필요시 'Malgun Gothic' 등으로 변경)
FONT_MONO = "Menlo"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


# ── 헬퍼 함수 ──────────────────────────────────────────────
def slide():
    return prs.slides.add_slide(BLANK)

def bg(s, color):
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = color

def rect(s, x, y, w, h, fill=None, line=None, line_w=1.0, shape=MSO_SHAPE.RECTANGLE, shadow=False):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(line_w)
    sp.shadow.inherit = False
    if shadow:
        el = sp._element.spPr
        ef = el.makeelement(qn('a:effectLst'), {}); el.append(ef)
        sh = ef.makeelement(qn('a:outerShdw'),
            {'blurRad':'90000','dist':'40000','dir':'5400000','rotWithShape':'0'}); ef.append(sh)
        c = sh.makeelement(qn('a:srgbClr'), {'val':'1E293B'}); sh.append(c)
        a = c.makeelement(qn('a:alpha'), {'val':'18000'}); c.append(a)
    return sp

def dashed(sp, color=GRAY, w=1.25):
    """플레이스홀더용 점선 테두리"""
    sp.line.color.rgb = color; sp.line.width = Pt(w)
    ln = sp.line._get_or_add_ln()
    d = ln.makeelement(qn('a:prstDash'), {'val':'dash'}); ln.append(d)

def text(s, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         space_after=4, line_spacing=1.0):
    """runs = [(텍스트, 크기, 색, 볼드, 폰트?)] 또는 문단 리스트"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Pt(0)
    tf.margin_top = tf.margin_bottom = Pt(0)
    if runs and not isinstance(runs[0], list):
        runs = [runs]
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(space_after); p.space_before = Pt(0)
        p.line_spacing = line_spacing
        for r in para:
            txt, sz, col, bold = r[0], r[1], r[2], r[3]
            fn = r[4] if len(r) > 4 else FONT
            run = p.add_run(); run.text = txt
            run.font.size = Pt(sz); run.font.color.rgb = col
            run.font.bold = bold; run.font.name = fn
    return tb

def placeholder(s, x, y, w, h, label, kind="screen"):
    """화면 캡처 / 소스 코드 삽입 영역"""
    fill = SKY if kind == "screen" else RGBColor(0xF1, 0xF5, 0xF9)
    box = rect(s, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    dashed(box, color=(BLUE if kind == "screen" else SLATE2))
    icon = "🖼️" if kind == "screen" else "💻"
    sub = "여기에 화면 캡처를 넣어주세요" if kind == "screen" else "여기에 소스 코드를 넣어주세요"
    col = BLUE_DK if kind == "screen" else SLATE2
    text(s, x, y + h/2 - 0.62, w, 1.3,
         [[(icon + "  " + label, 15, col, True)],
          [(sub, 11, GRAY, False)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space_after=6)
    return box

def header(s, idx, title, sub=None):
    """본문 슬라이드 상단 헤더"""
    bg(s, WHITE)
    rect(s, 0, 0, 13.333, 1.15, fill=WHITE)
    rect(s, 0.55, 0.42, 0.12, 0.52, fill=BLUE)           # 액센트 바
    text(s, 0.85, 0.36, 9.5, 0.7, [(title, 25, SLATE, True)])
    if sub:
        text(s, 0.87, 0.92, 11.5, 0.4, [(sub, 12.5, GRAY, False)])
    text(s, 11.6, 0.45, 1.3, 0.5, [(f"{idx:02d}", 26, LINE, True)], align=PP_ALIGN.RIGHT)
    rect(s, 0.85, 1.32, 11.63, 0.022, fill=LINE)

def chip(s, x, y, w, label, fill, fg, size=11.5, h=0.42):
    c = rect(s, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    c.adjustments[0] = 0.5
    text(s, x, y, w, h, [(label, size, fg, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

def bullet(s, x, y, w, items, gap=0.52, dot=BLUE, size=13.5, title_size=None):
    """items = [(strong, desc)] 또는 [str]"""
    cy = y
    for it in items:
        rect(s, x, cy + 0.07, 0.13, 0.13, fill=dot, shape=MSO_SHAPE.OVAL)
        if isinstance(it, tuple):
            strong, desc = it
            text(s, x + 0.32, cy - 0.04, w - 0.32, gap,
                 [[(strong + "  ", (title_size or size), SLATE, True), (desc, size, SLATE2, False)]],
                 line_spacing=1.05)
        else:
            text(s, x + 0.32, cy - 0.04, w - 0.32, gap, [(it, size, SLATE2, False)], line_spacing=1.05)
        cy += gap
    return cy


# ════════════════════════════════════════════════════════════
# 1. 타이틀
# ════════════════════════════════════════════════════════════
s = slide(); bg(s, NAVY)
rect(s, 0, 0, 13.333, 0.14, fill=BLUE)
rect(s, 0, 7.36, 13.333, 0.14, fill=AMBER)
chip(s, 0.9, 1.5, 2.4, "PORTFOLIO PROJECT", RGBColor(0x1D,0x4E,0xD8), RGBColor(0xBF,0xDB,0xFE), 12, 0.46)
text(s, 0.85, 2.35, 11.6, 1.5, [("Stock Agent Hub", 54, WHITE, True)])
text(s, 0.9, 3.55, 11.5, 0.8,
     [("멀티 에이전트 기반 주식 질의응답 서비스", 22, RGBColor(0xCB,0xD5,0xE1), False)])
rect(s, 0.9, 4.5, 5.4, 0.02, fill=RGBColor(0x33,0x41,0x55))
text(s, 0.9, 4.75, 11.5, 1.2,
     [[("질문 판별 · 정보 수집 · 답변 생성", 14, GRAY, False)],
      [("3개의 AI 에이전트가 역할을 분담하는 분석형 AI 서비스", 14, GRAY, False)]],
     space_after=6)
text(s, 0.9, 6.45, 11.5, 0.5,
     [[("Vue 3", 13, RGBColor(0x7D,0xD3,0xC0), True), ("   ·   ", 13, GRAY, False),
       ("Spring Boot", 13, RGBColor(0x86,0xEF,0xAC), True), ("   ·   ", 13, GRAY, False),
       ("FastAPI + crewAI", 13, RGBColor(0xFD,0xBA,0x74), True), ("   ·   ", 13, GRAY, False),
       ("Gemini", 13, RGBColor(0x93,0xC5,0xFD), True), ("   ·   ", 13, GRAY, False),
       ("Docker", 13, RGBColor(0xA5,0xB4,0xFC), True)]])


# ════════════════════════════════════════════════════════════
# 2. 프로젝트 개요
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 1, "프로젝트 개요", "Project Overview")
text(s, 0.85, 1.55, 11.6, 0.8,
     [[("주식 관련 질문에 ", 16, SLATE2, False), ("여러 AI 에이전트가 역할을 분담", 16, BLUE, True),
       ("하여 답변을 생성하는 서비스", 16, SLATE2, False)]], line_spacing=1.2)
# 좌측 설명
y = bullet(s, 0.9, 2.55, 6.0, [
    ("단일 챗봇이 아닌", "질문 판별 → 정보 수집 → 답변 생성을 독립 에이전트가 수행"),
    ("책임 분리(SRP)", "각 단계를 분리해 비용 최적화 · 투명성 확보"),
    ("실시간 진행 표시", "SSE로 에이전트 진행 상황을 단계별 스트리밍"),
    ("최신 정보 반영", "Google Search Grounding으로 실시간 시장 데이터 검색"),
], gap=0.78, size=13.5)
# 우측 카드 - 3개 에이전트 요약
cx = 7.4
rect(s, cx, 2.45, 5.1, 3.9, fill=LIGHT, line=LINE, line_w=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
text(s, cx+0.4, 2.7, 4.3, 0.4, [("AGENT PIPELINE", 11, GRAY, True)])
agents = [("1", "Router Agent", "주식 관련 질문인지 판별", BLUE, SKY),
          ("2", "Research Agent", "웹 검색 기반 정보 수집", AMBER, AMBER_BG),
          ("3", "Summary Agent", "구조화된 투자 분석 생성", GREEN, GREEN_BG)]
ay = 3.25
for num, name, desc, col, cbg in agents:
    rect(s, cx+0.4, ay, 4.3, 0.92, fill=cbg, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    n = rect(s, cx+0.62, ay+0.23, 0.46, 0.46, fill=col, shape=MSO_SHAPE.OVAL)
    text(s, cx+0.62, ay+0.23, 0.46, 0.46, [(num, 15, WHITE, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, cx+1.25, ay+0.16, 3.3, 0.4, [(name, 14, SLATE, True)])
    text(s, cx+1.25, ay+0.52, 3.3, 0.35, [(desc, 11, SLATE2, False)])
    ay += 1.04


# ════════════════════════════════════════════════════════════
# 3. 기획 배경 / 문제 정의
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 2, "기획 배경", "왜 멀티 에이전트인가?")
text(s, 0.85, 1.5, 11.6, 0.5,
     [("일반적인 단일 AI 챗봇이 특정 도메인 서비스에서 갖는 한계", 15, SLATE2, False)])
# 문제 (좌)
rect(s, 0.9, 2.25, 5.5, 4.4, fill=RED_BG, line=RGBColor(0xFE,0xCA,0xCA), line_w=1.2,
     shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 1.25, 2.5, 4.9, 0.5, [("⚠  기존 단일 챗봇의 문제", 15, RED, True)])
bullet(s, 1.25, 3.2, 4.9, [
    "관련 없는 질문에도 동일한 비용 발생",
    "답변 생성 과정이 불투명",
    "기능 확장 시 프롬프트 복잡도 증가",
    "문제 발생 시 원인 파악 어려움",
], gap=0.78, dot=RED, size=13)
# 해결 (우)
rect(s, 6.85, 2.25, 5.6, 4.4, fill=GREEN_BG, line=RGBColor(0xBB,0xF7,0xD0), line_w=1.2,
     shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 7.2, 2.5, 5.0, 0.5, [("✓  멀티 에이전트 구조로 해결", 15, GREEN, True)])
bullet(s, 7.2, 3.2, 5.0, [
    ("역할 분리", "Router가 비주식 질문을 조기 차단 → 비용 절감"),
    ("처리 과정 투명화", "단계별 진행 상황을 실시간 노출"),
    ("독립적 확장", "에이전트 단위로 기능 추가 가능"),
    ("장애 추적 용이", "실행 로그로 단계별 성공/실패 기록"),
], gap=0.82, dot=GREEN, size=12.5)


# ════════════════════════════════════════════════════════════
# 4. 시스템 아키텍처
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 3, "시스템 아키텍처", "3-Tier + 멀티 에이전트 구조")

def node(x, y, w, h, title, subtitle, fill, fg, sub_fg, tsize=13):
    rect(s, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
    text(s, x, y+0.16, w, 0.4, [(title, tsize, fg, True)], align=PP_ALIGN.CENTER)
    text(s, x, y+h-0.42, w, 0.35, [(subtitle, 10, sub_fg, False)], align=PP_ALIGN.CENTER)

def arrow(x, y, w, label=None, color=GRAY):
    a = rect(s, x, y, w, 0.045, fill=color)
    rect(s, x+w-0.02, y-0.07, 0.16, 0.18, fill=color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 90
    if label:
        text(s, x-0.3, y-0.42, w+0.6, 0.3, [(label, 9.5, GRAY, True)], align=PP_ALIGN.CENTER)

yc = 2.35
node(0.9, yc, 2.3, 1.15, "Frontend", "Vue 3 · Pinia", SLATE, WHITE, GRAY)
text(s, 0.9, yc+1.2, 2.3, 0.3, [("nginx + SSL", 10, GRAY, False)], align=PP_ALIGN.CENTER)
arrow(3.35, yc+0.55, 0.95, "REST/SSE")
node(4.45, yc, 2.5, 1.15, "Backend", "Spring Boot 4 · JPA", GREEN, WHITE, RGBColor(0xD1,0xFA,0xE5))
text(s, 4.45, yc+1.2, 2.5, 0.3, [("Java 21", 10, GRAY, False)], align=PP_ALIGN.CENTER)
arrow(7.1, yc+0.55, 0.95, "REST/SSE")
node(8.2, yc, 2.6, 1.15, "AI Service", "FastAPI · crewAI", AMBER, WHITE, RGBColor(0xFE,0xF3,0xC7))
text(s, 8.2, yc+1.2, 2.6, 0.3, [("Python 3.11", 10, GRAY, False)], align=PP_ALIGN.CENTER)
# Gemini
node(11.0, yc, 1.5, 1.15, "Gemini", "LLM + Search", BLUE, WHITE, RGBColor(0xBF,0xDB,0xFE), tsize=12)

# 데이터 계층
ymd = 4.55
text(s, 0.9, 4.05, 6.0, 0.35, [("데이터 계층 (Backend 전용)", 11.5, GRAY, True)])
node(4.45, ymd, 2.5, 1.0, "MySQL", "질문 이력 · 실행 로그", BLUE_DK, WHITE, RGBColor(0xBA,0xE6,0xFD), tsize=13)
node(7.1, ymd, 2.0, 1.0, "Redis", "답변 캐시 (24h)", RED, WHITE, RGBColor(0xFE,0xCA,0xCA), tsize=13)
# 연결선 (backend → db)
rect(s, 5.6, yc+1.15, 0.04, ymd-(yc+1.15), fill=LINE)
rect(s, 8.0, yc+1.15, 0.04, ymd-(yc+1.15), fill=LINE)

# 하단 설명
rect(s, 0.9, 5.95, 11.55, 0.85, fill=LIGHT, line=LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 1.2, 6.06, 11.0, 0.7,
     [[("핵심 포인트  ", 12, BLUE, True),
       ("Backend가 SSE 프록시 역할을 수행하여 AI Service의 이벤트 스트림을 클라이언트로 중계하고, "
        "AI Service는 DB에 독립적으로 LLM 추론에만 집중", 12, SLATE2, False)]], line_spacing=1.15)


# ════════════════════════════════════════════════════════════
# 5. 멀티 에이전트 파이프라인
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 4, "멀티 에이전트 파이프라인", "Router → Research → Summary")

steps = [
    ("RUNNING", "Router Agent", "질문 판별", "주식 관련 여부 분류\nnot_stock → 조기 종료", BLUE, SKY),
    ("RUNNING", "Research Agent", "정보 수집", "Google Search로\n최신 시장 데이터 검색", AMBER, AMBER_BG),
    ("RUNNING", "Summary Agent", "답변 생성", "구조화 JSON 분석\n매수의견 · 긍정 · 리스크", GREEN, GREEN_BG),
]
bx = 0.9; bw = 3.45; gap = 0.42; by = 1.95
for i, (st, name, role, desc, col, cbg) in enumerate(steps):
    x = bx + i*(bw+gap)
    rect(s, x, by, bw, 2.55, fill=cbg, line=col, line_w=1.4, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
    n = rect(s, x+0.35, by+0.32, 0.6, 0.6, fill=col, shape=MSO_SHAPE.OVAL)
    text(s, x+0.35, by+0.32, 0.6, 0.6, [(str(i+1), 20, WHITE, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x+1.1, by+0.34, bw-1.3, 0.4, [(role, 16, SLATE, True)])
    text(s, x+1.1, by+0.74, bw-1.3, 0.3, [(name, 11, col, True)])
    rect(s, x+0.35, by+1.25, bw-0.7, 0.02, fill=col)
    text(s, x+0.35, by+1.42, bw-0.7, 1.0,
         [(line, 12.5, SLATE2, False) for line in desc.split("\n")], line_spacing=1.15, space_after=3)
    if i < 2:
        ax = x + bw + 0.04
        rect(s, ax, by+1.2, gap-0.12, 0.05, fill=GRAY)
        rect(s, ax+gap-0.18, by+1.13, 0.16, 0.18, fill=GRAY, shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 90

# 이벤트 흐름
rect(s, 0.9, 4.95, 11.55, 1.75, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 1.25, 5.12, 11.0, 0.4, [("실시간 이벤트 스트림 (SSE)", 13, RGBColor(0x93,0xC5,0xFD), True)])
events = [("agent_status", "RUNNING / SUCCESS", AMBER),
          ("complete", "최종 분석 결과 JSON", GREEN),
          ("error", "예외 발생 시 메시지", RED)]
ex = 1.25
for ev, desc, col in events:
    rect(s, ex, 5.62, 3.5, 0.85, fill=RGBColor(0x1E,0x29,0x3B), shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(s, ex+0.25, 5.85, 0.13, 0.13, fill=col, shape=MSO_SHAPE.OVAL)
    text(s, ex+0.5, 5.74, 3.0, 0.35, [("event: " + ev, 12.5, WHITE, True, FONT_MONO)])
    text(s, ex+0.5, 6.08, 3.0, 0.35, [(desc, 10.5, GRAY, False)])
    ex += 3.72


# ════════════════════════════════════════════════════════════
# 6. 기술 스택
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 5, "기술 스택", "Tech Stack")
cols = [
    ("Frontend", SLATE, [("Vue 3", "Composition API"), ("Pinia", "상태 관리"),
                          ("TypeScript", ""), ("Vite", "빌드"), ("nginx", "정적 서빙 · SSL")]),
    ("Backend", GREEN, [("Spring Boot 4", "Java 21"), ("Spring Data JPA", ""),
                        ("SseEmitter", "SSE 스트리밍"), ("@Async", "비동기 처리"), ("MySQL · Redis", "")]),
    ("AI Service", AMBER, [("FastAPI", "Python 3.11"), ("crewAI", "멀티 에이전트"),
                           ("Gemini", "google-genai"), ("Search Grounding", "웹 검색"), ("sse-starlette", "")]),
    ("Infra", PURPLE, [("Docker Compose", "5개 서비스"), ("certbot", "Let's Encrypt"),
                       ("nginx", "리버스 프록시"), ("uv", "Python 패키지"), ("Gradle", "빌드")]),
]
cw = 2.78; cgap = 0.24; cx0 = 0.9; cy0 = 1.75
for i, (title, col, items) in enumerate(cols):
    x = cx0 + i*(cw+cgap)
    rect(s, x, cy0, cw, 4.85, fill=LIGHT, line=LINE, line_w=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
    rect(s, x, cy0, cw, 0.72, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(s, x, cy0+0.36, cw, 0.36, fill=col)   # 하단 모서리 정리
    text(s, x, cy0+0.13, cw, 0.5, [(title, 15, WHITE, True)], align=PP_ALIGN.CENTER)
    iy = cy0 + 1.0
    for name, desc in items:
        text(s, x+0.32, iy, cw-0.5, 0.4, [(name, 13.5, SLATE, True)])
        if desc:
            text(s, x+0.32, iy+0.34, cw-0.5, 0.3, [(desc, 10.5, GRAY, False)])
            iy += 0.78
        else:
            iy += 0.62


# ════════════════════════════════════════════════════════════
# 7. 핵심 구현 ① SSE 실시간 스트리밍
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 6, "핵심 구현 ①  실시간 스트리밍", "SSE 기반 에이전트 진행 상황 전달")
bullet(s, 0.9, 1.7, 5.7, [
    ("SSE 프록시 체인", "Client ← Backend(SseEmitter) ← AI Service(sse-starlette)"),
    ("@Async 분리", "AOP self-invocation 우회를 위해 별도 빈(QuestionProcessor)으로 추출"),
    ("이벤트 중계", "agent_status·complete·error를 클라이언트로 그대로 포워딩"),
    ("DB 기록 선행", "SSE 전송 전 실행 로그를 커밋해 상태 정합성 보장"),
], gap=0.92, size=13)
placeholder(s, 6.9, 1.7, 5.55, 4.9, "QuestionProcessor / useSSE 코드", "code")


# ════════════════════════════════════════════════════════════
# 8. 핵심 구현 ② 동기→비동기 브릿지
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 7, "핵심 구현 ②  동기 → 비동기 브릿지", "crewAI(동기)를 async FastAPI에 통합")
placeholder(s, 0.9, 1.7, 5.55, 4.9, "routers/agents.py 코드", "code")
bullet(s, 6.85, 1.75, 5.6, [
    ("문제", "crewAI는 동기 실행 → async 이벤트 루프를 블로킹"),
    ("run_in_executor", "스레드풀에서 파이프라인 실행, 루프 비블로킹 유지"),
    ("call_soon_threadsafe", "워커 스레드 → 이벤트 루프로 안전하게 이벤트 전달"),
    ("asyncio.Queue", "이벤트 버퍼링 후 EventSourceResponse로 스트리밍"),
], gap=0.96, size=12.5)
rect(s, 6.85, 5.95, 5.6, 0.75, fill=SKY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 7.1, 6.04, 5.1, 0.6,
     [[("흐름  ", 11.5, BLUE_DK, True),
       ("Thread Pool → call_soon_threadsafe → Queue → SSE", 11.5, SLATE2, False, FONT_MONO)]],
     line_spacing=1.1)


# ════════════════════════════════════════════════════════════
# 9. 핵심 구현 ③ 캐싱 & 검색 그라운딩
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 8, "핵심 구현 ③  캐싱 · 검색 그라운딩", "비용 최적화 & 최신성 확보")
# 좌: 캐싱
rect(s, 0.9, 1.7, 5.6, 4.95, fill=LIGHT, line=LINE, line_w=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
text(s, 1.25, 1.95, 5.0, 0.4, [("⚡  Redis 답변 캐싱", 15, RED, True)])
bullet(s, 1.25, 2.65, 4.95, [
    ("SHA-256 해시 키", "질문 정규화(소문자·trim) 후 해시"),
    ("TTL 24시간", "동일 질문 재요청 시 LLM 호출 없이 즉시 응답"),
    ("캐시 분기 처리", "not_stock 결과는 캐싱 제외"),
    ("즉시 complete", "캐시 히트 시 SSE로 바로 결과 전송"),
], gap=0.82, dot=RED, size=12.5)
# 우: 검색 그라운딩
rect(s, 6.85, 1.7, 5.6, 4.95, fill=LIGHT, line=LINE, line_w=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
text(s, 7.2, 1.95, 5.0, 0.4, [("🔍  Google Search Grounding", 15, BLUE, True)])
bullet(s, 7.2, 2.65, 4.95, [
    ("최신 정보 반영", "LLM 학습 데이터 한계를 실시간 검색으로 보완"),
    ("추가 키 불필요", "기존 Gemini API 키로 grounding 활용"),
    ("직접 주입 방식", "tool-loop 오류 우회 → 검색 결과를 프롬프트에 주입"),
    ("Research 전용", "정보 수집 단계에만 적용해 비용 절약"),
], gap=0.82, dot=BLUE, size=12.5)


# ════════════════════════════════════════════════════════════
# 10. 트러블슈팅
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 9, "트러블슈팅", "주요 문제 해결 경험")
rows = [
    ("HTTP/2 body 누락", "Java HttpClient 기본 HTTP/2 → uvicorn에서 body=null",
     "HTTP/1.1 강제 설정", RED),
    ("crewAI tool-loop 오류", "Agent.tools 등록 시 function-calling 모드 → 빈 응답",
     "검색 결과를 task 설명에 직접 주입", AMBER),
    ("@Async 미동작", "동일 빈 self-invocation으로 AOP 프록시 우회됨",
     "별도 빈(QuestionProcessor)으로 분리", BLUE),
    ("상태 표시 안됨", "AI는 대문자 SUCCESS, 프론트는 소문자 기대 → 불일치",
     "status.toLowerCase() 정규화", GREEN),
    ("실행 로그 미기록", "JSON 파싱이 콜론 뒤 공백 미처리로 항상 실패",
     "파싱 로직 수정 (공백 허용)", PURPLE),
]
ty = 1.65
# 헤더 행
rect(s, 0.9, ty, 11.55, 0.5, fill=SLATE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
for cx, w, t in [(1.2,3.0,"문제"),(4.3,4.6,"원인"),(9.0,3.3,"해결")]:
    text(s, cx, ty+0.08, w, 0.35, [(t, 12.5, WHITE, True)])
ty += 0.62
for prob, cause, sol, col in rows:
    rect(s, 0.9, ty, 11.55, 0.92, fill=LIGHT, line=LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(s, 0.9, ty, 0.1, 0.92, fill=col)
    text(s, 1.2, ty+0.1, 3.0, 0.75, [(prob, 12.5, SLATE, True)], anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
    text(s, 4.3, ty+0.1, 4.55, 0.75, [(cause, 11, SLATE2, False)], anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05)
    text(s, 9.0, ty+0.1, 3.3, 0.75, [("✓ " + sol, 11.5, GREEN, True)], anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05)
    ty += 1.0


# ════════════════════════════════════════════════════════════
# 11. 화면 — 메인 분석 플로우
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 10, "주요 화면 ①", "질문 입력 → 실시간 분석 → 결과")
placeholder(s, 0.9, 1.65, 7.4, 5.0, "메인 화면 (질문 입력 + 에이전트 진행 + 분석 결과)", "screen")
# 우측 설명
text(s, 8.55, 1.8, 3.9, 0.4, [("화면 구성", 13, GRAY, True)])
bullet(s, 8.6, 2.4, 3.85, [
    ("질문 입력", "단일 질문 기반 안내"),
    ("에이전트 타임라인", "스피너·LIVE 배지·단계 표시"),
    ("분석 결과 카드", "티커·매수의견·긍정·리스크"),
    ("실행 로그", "우측 사이드바 단계별 소요시간"),
    ("최근 질문", "좌측 사이드바 히스토리"),
], gap=0.82, size=12)


# ════════════════════════════════════════════════════════════
# 12. 화면 — 부가 기능
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 11, "주요 화면 ②", "히스토리 · 실행 로그 · 예외 처리")
placeholder(s, 0.9, 1.65, 5.7, 5.0, "히스토리 조회 / 캐시 히트 화면", "screen")
placeholder(s, 6.75, 1.65, 5.7, 2.4, "에이전트 실행 로그 (소요시간)", "screen")
placeholder(s, 6.75, 4.25, 5.7, 2.4, "비주식 질문 안내 / 에러 처리", "screen")


# ════════════════════════════════════════════════════════════
# 13. 데이터 모델
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 12, "데이터 모델", "질문 이력 & 에이전트 실행 로그")
# question_history
def table_card(x, w, title, color, fields):
    rect(s, x, 1.75, w, 4.9, fill=LIGHT, line=LINE, line_w=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
    rect(s, x, 1.75, w, 0.68, fill=color, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(s, x, 1.75+0.34, w, 0.34, fill=color)
    text(s, x+0.35, 1.87, w-0.5, 0.45, [(title, 14.5, WHITE, True, FONT_MONO)])
    fy = 2.65
    for fname, ftype, fdesc in fields:
        text(s, x+0.35, fy, 2.5, 0.35, [(fname, 12.5, SLATE, True, FONT_MONO)])
        text(s, x+0.35, fy+0.28, w-0.7, 0.3, [[(ftype+"  ", 10.5, BLUE, True, FONT_MONO),
                                               (fdesc, 10.5, GRAY, False)]])
        fy += 0.72
table_card(0.9, 5.6, "question_history", BLUE_DK, [
    ("id", "BIGINT", "PK"),
    ("user_key", "VARCHAR(36)", "브라우저 UUID"),
    ("question", "TEXT", "질문 내용"),
    ("answer", "JSON", "ticker·recommendation·summary…"),
    ("status", "ENUM", "PENDING·RUNNING·SUCCESS·FAIL"),
    ("created_at", "DATETIME", "생성 시각"),
])
table_card(6.85, 5.6, "agent_execution_log", AMBER, [
    ("id", "BIGINT", "PK"),
    ("question_id", "BIGINT", "FK → question_history"),
    ("run_id", "VARCHAR(36)", "실행 단위 식별자"),
    ("agent_name", "VARCHAR(50)", "Router·Research·Summary"),
    ("status", "ENUM", "RUNNING·SUCCESS·FAIL"),
    ("started_at / finished_at", "DATETIME", "단계별 소요시간 측정"),
])


# ════════════════════════════════════════════════════════════
# 14. 배포 구성
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 13, "배포 구성", "Docker Compose · nginx · Let's Encrypt SSL")
# compose 서비스
text(s, 0.9, 1.6, 11.5, 0.4, [("단일 docker compose up 으로 전체 스택 기동", 14, SLATE2, False)])
svcs = [("frontend", "nginx + SSL", PURPLE), ("backend", "Spring Boot", GREEN),
        ("ai-service", "FastAPI", AMBER), ("mysql", "8.4", BLUE_DK), ("redis", "8", RED),
        ("certbot", "자동 갱신", SLATE)]
sx = 0.9
for name, desc, col in svcs:
    rect(s, sx, 2.25, 1.85, 1.15, fill=WHITE, line=col, line_w=1.6, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
    rect(s, sx, 2.25, 1.85, 0.1, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, sx, 2.55, 1.85, 0.4, [(name, 13, SLATE, True)], align=PP_ALIGN.CENTER)
    text(s, sx, 2.95, 1.85, 0.35, [(desc, 10.5, GRAY, False)], align=PP_ALIGN.CENTER)
    sx += 1.95
# 배포 특징
bullet(s, 0.9, 4.0, 6.0, [
    ("환경변수 파라미터화", "${VAR:-default} 패턴, 단일 .env 관리"),
    ("자동 스키마 초기화", "init.sql을 MySQL 컨테이너 진입점에 마운트"),
    ("SSL 자동화", "certbot 발급 + 12시간마다 자동 갱신"),
    ("임시 인증서 폴백", "인증서 없어도 self-signed로 기동 보장"),
], gap=0.7, size=12.5)
placeholder(s, 7.2, 4.0, 5.25, 2.75, "docker-compose.yml / 배포 구조", "code")


# ════════════════════════════════════════════════════════════
# 15. 회고 & 향후 계획
# ════════════════════════════════════════════════════════════
s = slide(); header(s, 14, "회고 & 향후 계획", "Retrospective & Next Steps")
# 배운 점
rect(s, 0.9, 1.7, 5.6, 4.95, fill=SKY, line=RGBColor(0xBA,0xE6,0xFD), line_w=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 1.25, 1.95, 5.0, 0.4, [("💡  배운 점", 15, BLUE_DK, True)])
bullet(s, 1.25, 2.65, 4.95, [
    ("이종 스택 통합", "Java SSE ↔ Python async 스트림 연동 경험"),
    ("동기/비동기 경계", "스레드풀·이벤트 루프 브릿지 설계"),
    ("관심사 분리", "에이전트·서비스 단위 책임 분리의 효용"),
    ("실전 디버깅", "프로토콜·프레임워크 레벨 이슈 추적"),
], gap=0.86, dot=BLUE, size=12.5)
# 향후 계획
rect(s, 6.85, 1.7, 5.6, 4.95, fill=AMBER_BG, line=RGBColor(0xFD,0xE6,0x8A), line_w=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 7.2, 1.95, 5.0, 0.4, [("🚀  향후 계획", 15, AMBER, True)])
bullet(s, 7.2, 2.65, 4.95, [
    ("의미 기반 캐시", "임베딩 + 벡터 유사도로 유사 질문 캐시 히트"),
    ("대화 맥락 유지", "단일 질문 → 멀티턴 컨텍스트 확장"),
    ("에이전트 추가", "차트·재무제표 분석 에이전트 확장"),
    ("모니터링", "에이전트별 비용·지연 대시보드"),
], gap=0.86, dot=AMBER, size=12.5)


# ════════════════════════════════════════════════════════════
# 16. 마무리
# ════════════════════════════════════════════════════════════
s = slide(); bg(s, NAVY)
rect(s, 0, 0, 13.333, 0.14, fill=BLUE)
rect(s, 0, 7.36, 13.333, 0.14, fill=AMBER)
text(s, 0, 2.7, 13.333, 1.0, [("Thank You", 48, WHITE, True)], align=PP_ALIGN.CENTER)
text(s, 0, 3.9, 13.333, 0.6, [("Stock Agent Hub — 멀티 에이전트 기반 주식 질의응답 서비스", 16, GRAY, False)],
     align=PP_ALIGN.CENTER)
text(s, 0, 4.8, 13.333, 0.5,
     [[("GitHub  ", 13, RGBColor(0x93,0xC5,0xFD), True), ("github.com/your-repo", 13, GRAY, False),
       ("      ·      ", 13, GRAY, False),
       ("Demo  ", 13, RGBColor(0x86,0xEF,0xAC), True), ("your-domain.com", 13, GRAY, False)]],
     align=PP_ALIGN.CENTER)

# ── 저장 ──
out = "/Users/haejil24/portfolio/ai-stock-research/StockAgentHub_Portfolio.pptx"
prs.save(out)
print("저장 완료:", out)
print("총 슬라이드:", len(prs.slides._sldIdLst))
