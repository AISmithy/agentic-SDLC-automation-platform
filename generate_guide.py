"""Generate the Agentic SDLC Platform — Developer UI Guide PDF."""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import Flowable
from datetime import date

# ── Colour palette ────────────────────────────────────────────────────────────
PRIMARY      = colors.HexColor("#4f46e5")   # indigo-600
PRIMARY_DARK = colors.HexColor("#3730a3")   # indigo-800
PRIMARY_LIGHT= colors.HexColor("#e0e7ff")   # indigo-100
AMBER        = colors.HexColor("#f59e0b")
AMBER_LIGHT  = colors.HexColor("#fef3c7")
GREEN        = colors.HexColor("#16a34a")
GREEN_LIGHT  = colors.HexColor("#dcfce7")
RED          = colors.HexColor("#dc2626")
RED_LIGHT    = colors.HexColor("#fee2e2")
GRAY_900     = colors.HexColor("#111827")
GRAY_700     = colors.HexColor("#374151")
GRAY_500     = colors.HexColor("#6b7280")
GRAY_200     = colors.HexColor("#e5e7eb")
GRAY_50      = colors.HexColor("#f9fafb")
WHITE        = colors.white
TEAL         = colors.HexColor("#0d9488")
TEAL_LIGHT   = colors.HexColor("#ccfbf1")
PURPLE       = colors.HexColor("#7c3aed")
PURPLE_LIGHT = colors.HexColor("#ede9fe")

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm

# ── Custom Flowables ──────────────────────────────────────────────────────────

class StepBox(Flowable):
    """Numbered step box with title and description."""
    def __init__(self, number, title, description, width=None):
        super().__init__()
        self.number = number
        self.title = title
        self.description = description
        self.width = width or (PAGE_W - 2 * MARGIN)
        self.height = 1.6 * cm

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        # background
        c.setFillColor(GRAY_50)
        c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
        # left accent
        c.setFillColor(PRIMARY)
        c.roundRect(0, 0, 6, h, 3, fill=1, stroke=0)
        # number circle
        c.setFillColor(PRIMARY)
        c.circle(22, h/2, 10, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        num_str = str(self.number)
        c.drawCentredString(22, h/2 - 3.5, num_str)
        # title
        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, h/2 + 2, self.title)
        # description
        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 8.5)
        c.drawString(40, h/2 - 10, self.description)


class InfoBox(Flowable):
    """Coloured info panel (tip / warning / note)."""
    def __init__(self, label, text, bg_color=None, border_color=None, width=None):
        super().__init__()
        self.label = label
        self.text = text
        self.bg = bg_color or PRIMARY_LIGHT
        self.border = border_color or PRIMARY
        self.width = width or (PAGE_W - 2 * MARGIN)
        # estimate height based on text length
        chars_per_line = int(self.width / 5.5)
        lines = max(2, len(text) // chars_per_line + 2)
        self.height = max(1.4 * cm, lines * 0.38 * cm + 0.6 * cm)

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        c.setFillColor(self.bg)
        c.roundRect(0, 0, w, h, 5, fill=1, stroke=0)
        c.setFillColor(self.border)
        c.roundRect(0, 0, 4, h, 2, fill=1, stroke=0)
        c.setFillColor(self.border)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(12, h - 14, self.label)
        c.setFillColor(GRAY_700)
        c.setFont("Helvetica", 8.5)
        # simple word-wrap
        words = self.text.split()
        line, y = "", h - 26
        max_w = w - 18
        for word in words:
            test = (line + " " + word).strip()
            if c.stringWidth(test, "Helvetica", 8.5) < max_w:
                line = test
            else:
                c.drawString(12, y, line)
                y -= 13
                line = word
        if line:
            c.drawString(12, y, line)


class UIPanel(Flowable):
    """Simulated UI panel showing field/button layout."""
    def __init__(self, title, fields, width=None):
        super().__init__()
        self.title = title
        self.fields = fields  # list of (label, value_hint) or ("btn", "Button Label", color)
        self.width = width or (PAGE_W - 2 * MARGIN)
        self.height = 1.0 * cm + len(fields) * 0.75 * cm + 0.4 * cm

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        # card border
        c.setStrokeColor(GRAY_200)
        c.setFillColor(WHITE)
        c.roundRect(0, 0, w, h, 6, fill=1, stroke=1)
        # title bar
        c.setFillColor(GRAY_50)
        c.roundRect(0, h - 0.9*cm, w, 0.9*cm, 6, fill=1, stroke=0)
        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(10, h - 0.6*cm, self.title)
        # fields
        y = h - 1.4*cm
        for field in self.fields:
            if field[0] == "btn":
                btn_color = field[2] if len(field) > 2 else PRIMARY
                c.setFillColor(btn_color)
                c.roundRect(10, y - 0.35*cm, 3.5*cm, 0.55*cm, 4, fill=1, stroke=0)
                c.setFillColor(WHITE)
                c.setFont("Helvetica-Bold", 8)
                c.drawString(16, y - 0.1*cm, field[1])
            elif field[0] == "badge":
                badge_color = field[2] if len(field) > 2 else PRIMARY_LIGHT
                text_color  = field[3] if len(field) > 3 else PRIMARY
                c.setFillColor(badge_color)
                c.roundRect(10, y - 0.3*cm, c.stringWidth(field[1], "Helvetica-Bold", 8) + 12, 0.48*cm, 4, fill=1, stroke=0)
                c.setFillColor(text_color)
                c.setFont("Helvetica-Bold", 8)
                c.drawString(16, y - 0.05*cm, field[1])
            else:
                label, hint = field[0], field[1]
                c.setFillColor(GRAY_500)
                c.setFont("Helvetica", 7.5)
                c.drawString(10, y + 0.05*cm, label)
                c.setFillColor(GRAY_200)
                c.roundRect(w//3, y - 0.3*cm, w - w//3 - 10, 0.5*cm, 3, fill=1, stroke=0)
                c.setFillColor(GRAY_500)
                c.setFont("Helvetica", 8)
                c.drawString(w//3 + 6, y - 0.05*cm, hint)
            y -= 0.75*cm


class SectionHeader(Flowable):
    """Full-width section header banner."""
    def __init__(self, number, title, subtitle="", width=None):
        super().__init__()
        self.number = number
        self.title = title
        self.subtitle = subtitle
        self.width = width or (PAGE_W - 2 * MARGIN)
        self.height = 1.8 * cm

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        c.setFillColor(PRIMARY)
        c.roundRect(0, 0, w, h, 8, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#6366f1"))
        c.roundRect(w - 2*cm, 0, 2*cm, h, 8, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(12, h - 14, f"SECTION {self.number}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(12, h - 30, self.title)
        if self.subtitle:
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.HexColor("#c7d2fe"))
            c.drawString(12, h - 44, self.subtitle)
        # section number big
        c.setFillColor(colors.HexColor("#6366f1"))
        c.setFont("Helvetica-Bold", 32)
        c.drawRightString(w - 8, 6, str(self.number))


class WorkflowState(Flowable):
    """Visual workflow state machine strip."""
    def __init__(self, states, current=None, width=None):
        super().__init__()
        self.states = states
        self.current = current
        self.width = width or (PAGE_W - 2 * MARGIN)
        rows = (len(states) + 3) // 4
        self.height = rows * 1.0 * cm + 0.3 * cm

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        w = self.width
        cols = 4
        cell_w = (w - (cols - 1) * 4) / cols
        cell_h = 0.75 * cm
        for i, state in enumerate(self.states):
            col = i % cols
            row = i // cols
            x = col * (cell_w + 4)
            y = self.height - (row + 1) * (cell_h + 4) + 4
            is_current = (state == self.current)
            is_done = (self.current and
                       self.states.index(state) < self.states.index(self.current)
                       if self.current in self.states else False)
            if is_current:
                bg = PRIMARY
                fg = WHITE
            elif is_done:
                bg = GREEN_LIGHT
                fg = GREEN
            else:
                bg = GRAY_50
                fg = GRAY_500
            c.setFillColor(bg)
            c.setStrokeColor(GRAY_200)
            c.roundRect(x, y, cell_w, cell_h, 4, fill=1, stroke=1)
            c.setFillColor(fg)
            c.setFont("Helvetica-Bold" if is_current else "Helvetica", 7)
            label = state.replace("_", " ").title()
            text_w = c.stringWidth(label, "Helvetica-Bold" if is_current else "Helvetica", 7)
            if text_w > cell_w - 8:
                label = label[:int((cell_w - 8) / 5)] + "…"
            c.drawCentredString(x + cell_w / 2, y + cell_h / 2 - 3.5, label)


# ── Styles ────────────────────────────────────────────────────────────────────

def make_styles():
    base = getSampleStyleSheet()
    s = {}
    s["title"] = ParagraphStyle("title",
        fontName="Helvetica-Bold", fontSize=28,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=6)
    s["subtitle"] = ParagraphStyle("subtitle",
        fontName="Helvetica", fontSize=13,
        textColor=colors.HexColor("#c7d2fe"), alignment=TA_CENTER, spaceAfter=4)
    s["h2"] = ParagraphStyle("h2",
        fontName="Helvetica-Bold", fontSize=13,
        textColor=GRAY_900, spaceBefore=14, spaceAfter=6)
    s["h3"] = ParagraphStyle("h3",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=PRIMARY_DARK, spaceBefore=10, spaceAfter=4)
    s["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=9,
        textColor=GRAY_700, leading=14, spaceAfter=4)
    s["body_bold"] = ParagraphStyle("body_bold",
        fontName="Helvetica-Bold", fontSize=9,
        textColor=GRAY_900, leading=14, spaceAfter=4)
    s["bullet"] = ParagraphStyle("bullet",
        fontName="Helvetica", fontSize=9,
        textColor=GRAY_700, leading=14,
        leftIndent=16, firstLineIndent=-10, spaceAfter=3)
    s["code"] = ParagraphStyle("code",
        fontName="Courier", fontSize=8.5,
        textColor=GRAY_900, backColor=GRAY_50,
        leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4,
        borderPad=6, leading=13)
    s["caption"] = ParagraphStyle("caption",
        fontName="Helvetica", fontSize=7.5,
        textColor=GRAY_500, alignment=TA_CENTER, spaceAfter=8)
    s["toc"] = ParagraphStyle("toc",
        fontName="Helvetica", fontSize=10,
        textColor=GRAY_700, leading=20, leftIndent=20)
    s["toc_h"] = ParagraphStyle("toc_h",
        fontName="Helvetica-Bold", fontSize=11,
        textColor=PRIMARY, leading=22)
    s["footer"] = ParagraphStyle("footer",
        fontName="Helvetica", fontSize=7.5,
        textColor=GRAY_500, alignment=TA_CENTER)
    return s


# ── Cover page ────────────────────────────────────────────────────────────────

def cover_page(S):
    elems = []
    # coloured background via Table trick
    cover_table = Table([
        [Paragraph("Agentic SDLC Automation Platform", S["title"])],
        [Paragraph("Developer UI Guide", S["subtitle"])],
        [Paragraph("Step-by-step walkthrough of every screen", S["subtitle"])],
        [Spacer(1, 0.5*cm)],
        [Paragraph(f"Version 1.0  ·  March 2026", ParagraphStyle("ver",
            fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#a5b4fc"),
            alignment=TA_CENTER))],
    ], colWidths=[PAGE_W - 2*MARGIN])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), PRIMARY),
        ("TOPPADDING", (0,0), (0,0), 3.5*cm),
        ("BOTTOMPADDING", (0,-1), (-1,-1), 2*cm),
        ("LEFTPADDING", (0,0), (-1,-1), 30),
        ("RIGHTPADDING", (0,0), (-1,-1), 30),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [PRIMARY]),
    ]))
    elems.append(cover_table)
    elems.append(Spacer(1, 0.8*cm))

    # Intro paragraph
    elems.append(Paragraph(
        "This guide walks a developer through every feature of the Agentic SDLC Platform UI — "
        "from logging in to monitoring a live deployment. Each section maps directly to one screen "
        "in the application and provides field-by-field instructions, button descriptions, and "
        "tips for common workflows.",
        ParagraphStyle("intro", fontName="Helvetica", fontSize=10,
                       textColor=GRAY_700, leading=16, alignment=TA_JUSTIFY,
                       spaceAfter=10)))
    elems.append(Spacer(1, 0.3*cm))

    # Quick-reference credential table
    elems.append(Paragraph("Default Login Credentials", S["h2"]))
    cred_data = [
        ["Role", "Email", "Password", "Permissions"],
        ["Admin", "admin@sdlc.local", "admin123", "Full access · approve plans/PRs · deploy"],
        ["Developer", "dev@sdlc.local", "dev123",  "Create runs · view diffs · read-only audit"],
    ]
    cred_table = Table(cred_data, colWidths=[3.2*cm, 5.5*cm, 3*cm, None])
    cred_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",    (0,0), (-1,0), WHITE),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",         (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]))
    elems.append(cred_table)
    elems.append(Spacer(1, 0.5*cm))

    # URLs
    elems.append(Paragraph("Application URLs", S["h2"]))
    url_data = [
        ["Service", "URL", "Notes"],
        ["Frontend (React)", "http://localhost:5173", "Main UI — start here"],
        ["Backend API",      "http://localhost:8000", "Django REST API"],
        ["Swagger Docs",     "http://localhost:8000/api/docs/", "Interactive API explorer"],
        ["Django Admin",     "http://localhost:8000/admin/",    "Superuser admin panel"],
    ]
    url_table = Table(url_data, colWidths=[3.8*cm, 7*cm, None])
    url_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(url_table)
    elems.append(PageBreak())
    return elems


# ── Table of Contents ─────────────────────────────────────────────────────────

def toc_page(S):
    elems = []
    elems.append(Paragraph("Table of Contents", S["h2"]))
    elems.append(HRFlowable(width="100%", thickness=1, color=GRAY_200))
    elems.append(Spacer(1, 0.3*cm))

    toc_entries = [
        ("1", "Getting Started",        "Starting the backend and frontend servers"),
        ("2", "Login Page",             "Authenticating and accessing the platform"),
        ("3", "Navigation Sidebar",     "Understanding the app layout"),
        ("4", "Dashboard",              "Overview — stats, alerts, recent runs"),
        ("5", "Story Intake",           "Starting a new workflow run from a Jira story"),
        ("6", "Diff Review",            "Reviewing workflow progress and proposed changes"),
        ("7", "Flow Builder",           "Designing custom workflow templates visually"),
        ("8", "Pull Request Management","Viewing and tracking AI-generated PRs"),
        ("9", "Deployment Console",     "Monitoring live deployments to dev environment"),
        ("10","Audit Timeline",         "Browsing the immutable event log"),
        ("11","Workflow State Machine",  "Understanding the 17-state lifecycle"),
        ("12","Admin Panel",            "Managing users, roles, and MCP capabilities"),
    ]
    for num, title, desc in toc_entries:
        row_data = [[
            Paragraph(f"<b>{num}</b>", ParagraphStyle("n", fontName="Helvetica-Bold",
                fontSize=10, textColor=PRIMARY, alignment=TA_CENTER)),
            Paragraph(f"<b>{title}</b><br/><font size=8 color='#6b7280'>{desc}</font>",
                ParagraphStyle("t", fontName="Helvetica", fontSize=10,
                    textColor=GRAY_900, leading=16)),
        ]]
        row_table = Table(row_data, colWidths=[1.2*cm, None])
        row_table.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (0,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        elems.append(row_table)
        elems.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_200))

    elems.append(PageBreak())
    return elems


# ── Section 1: Getting Started ────────────────────────────────────────────────

def section_getting_started(S):
    elems = []
    elems.append(SectionHeader(1, "Getting Started",
        "Start the backend, frontend, and optional Celery worker"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("Prerequisites", S["h2"]))
    prereqs = [
        ("Python 3.12+", "Already installed with virtualenv at backend/.venv"),
        ("Node.js 18+",  "Installed at C:\\Program Files\\nodejs"),
        ("Redis",        "Required only if running background agent tasks (Celery)"),
    ]
    prereq_table = Table(prereqs, colWidths=[4*cm, None])
    prereq_table.setStyle(TableStyle([
        ("FONTNAME",     (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 8.5),
        ("FONTNAME",     (1,0), (1,-1), "Helvetica"),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",         (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]))
    elems.append(prereq_table)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("Step 1 — Start the Backend (Terminal 1)", S["h3"]))
    elems.append(Paragraph(
        "Open a terminal, navigate to the <b>backend/</b> folder and run:", S["body"]))
    elems.append(Paragraph(
        "cd c:/GIT-REPO/agentic-SDLC-automation-platform/backend\n"
        "source .venv/Scripts/activate\n"
        "python manage.py runserver",
        S["code"]))
    elems.append(InfoBox("Expected output",
        "Starting development server at http://127.0.0.1:8000/ — Quit the server with CTRL-BREAK.",
        GREEN_LIGHT, GREEN))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Step 2 — Start the Frontend (Terminal 2)", S["h3"]))
    elems.append(Paragraph(
        "Open a <b>second</b> terminal and run:", S["body"]))
    elems.append(Paragraph(
        "cd c:/GIT-REPO/agentic-SDLC-automation-platform/frontend\n"
        "export PATH=\"/c/Program Files/nodejs:$PATH\"\n"
        "npm run dev",
        S["code"]))
    elems.append(InfoBox("Expected output",
        "VITE v6.x ready — Local: http://localhost:5173/  — both servers must be running simultaneously.",
        GREEN_LIGHT, GREEN))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Step 3 — (Optional) Start the Celery Worker (Terminal 3)", S["h3"]))
    elems.append(Paragraph(
        "Celery is needed for background agent execution tasks. Requires Redis on localhost:6379.", S["body"]))
    elems.append(Paragraph(
        "cd backend\n"
        "source .venv/Scripts/activate\n"
        "celery -A config worker --loglevel=info",
        S["code"]))
    elems.append(InfoBox("Note",
        "Without Celery, workflow state transitions triggered via the UI will be queued but not executed. "
        "For demo/UI exploration, you can proceed without it.",
        AMBER_LIGHT, AMBER))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Step 4 — Open the App", S["h3"]))
    elems.append(Paragraph(
        "Open your browser and go to: <b>http://localhost:5173</b>", S["body"]))
    elems.append(Paragraph(
        "You will be automatically redirected to the Login page.", S["body"]))

    elems.append(PageBreak())
    return elems


# ── Section 2: Login ──────────────────────────────────────────────────────────

def section_login(S):
    elems = []
    elems.append(SectionHeader(2, "Login Page",
        "http://localhost:5173/login"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "The login page is the entry point to the platform. It is shown automatically "
        "whenever you are not authenticated or your JWT session has expired.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("What you see on screen", S["h3"]))
    elems.append(UIPanel("Agentic SDLC Platform — Sign In", [
        ("Email",    "you@company.com"),
        ("Password", "••••••••  [eye icon to reveal]"),
        ("btn",      "Sign in", PRIMARY),
    ]))
    elems.append(Paragraph("Simulated login form layout", S["caption"]))

    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph("How to log in", S["h3"]))
    for n, title, desc in [
        (1, "Enter your email",    "Type admin@sdlc.local (admin) or dev@sdlc.local (developer)"),
        (2, "Enter your password", "admin123 for admin  /  dev123 for developer"),
        (3, "Click Sign in",       "The button shows a spinner while authenticating"),
        (4, "You are redirected",  "On success → Dashboard. On failure → red error banner appears"),
    ]:
        elems.append(StepBox(n, title, desc))
        elems.append(Spacer(1, 0.15*cm))

    elems.append(Spacer(1, 0.3*cm))
    elems.append(InfoBox("Security note",
        "The platform uses JWT tokens (access + refresh). The access token is stored in memory "
        "via Zustand and attached as a Bearer header on every API call. If the access token expires, "
        "it is silently refreshed using the refresh token stored in localStorage.",
        PRIMARY_LIGHT, PRIMARY))

    elems.append(PageBreak())
    return elems


# ── Section 3: Navigation ─────────────────────────────────────────────────────

def section_navigation(S):
    elems = []
    elems.append(SectionHeader(3, "Navigation Sidebar",
        "Persistent left-hand navigation present on all pages after login"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "After login every page shows a left sidebar. The sidebar contains the platform "
        "logo, all navigation links, and a footer showing the logged-in user.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    nav_data = [
        ["Icon", "Label",              "Route",             "Purpose"],
        ["⊞",   "Dashboard",          "/dashboard",        "Overview and stats"],
        ["📖",   "Story Intake",       "/stories",          "Start workflows, approve gates"],
        ["⬡",   "Flow Builder",       "/flow-builder",     "Design workflow templates"],
        ["</>",  "Diff Review",        "/runs/:id/review",  "Review AI-proposed code changes"],
        ["⑂",   "Pull Requests",      "/pull-requests",    "Track AI-generated PRs"],
        ["🚀",   "Deployment Console", "/deployments",      "Monitor live deployments"],
        ["📜",   "Audit Timeline",     "/audit",            "Immutable event log"],
    ]
    nav_table = Table(nav_data, colWidths=[1.2*cm, 3.8*cm, 5*cm, None])
    nav_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("ALIGN",         (0,0), (0,-1), "CENTER"),
    ]))
    elems.append(nav_table)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("Sidebar Footer", S["h3"]))
    elems.append(Paragraph(
        "At the bottom of the sidebar you will see your display name and role badge. "
        "Click the <b>Logout</b> button to sign out and return to the login page.", S["body"]))

    elems.append(PageBreak())
    return elems


# ── Section 4: Dashboard ──────────────────────────────────────────────────────

def section_dashboard(S):
    elems = []
    elems.append(SectionHeader(4, "Dashboard",
        "http://localhost:5173/dashboard  —  overview of platform activity"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "The Dashboard is the landing page after login. It gives a real-time snapshot "
        "of workflow activity, pending approvals, and deployment history.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Stats Cards (top row)", S["h3"]))
    cards = [
        ["Stat Card",          "What it shows",                  "When it is highlighted"],
        ["Active Runs",        "Workflows not yet in terminal state", "Always blue"],
        ["Pending Approvals",  "Approvals awaiting a decision",   "Amber when count > 0"],
        ["Deployments",        "Total deployment records",        "Always teal"],
        ["Successful Deploys", "Deployments with status=success", "Always green"],
    ]
    ct = Table(cards, colWidths=[4*cm, 6*cm, None])
    ct.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(ct)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("Pending Approvals Alert Banner", S["h3"]))
    elems.append(Paragraph(
        "If there are any pending approvals a yellow warning banner appears below the stats. "
        "It shows the count and includes a <b>Review</b> button that navigates to Story Intake.", S["body"]))
    elems.append(InfoBox("Tip",
        "The admin account sees ALL pending approvals. Developer accounts only see "
        "approvals they are authorised to action based on their role capabilities.",
        AMBER_LIGHT, AMBER))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Recent Workflow Runs Table", S["h3"]))
    for n, title, desc in [
        (1, "Story / Run column",  "Shows Jira issue key (e.g. PROJ-123) or first 8 chars of session ID"),
        (2, "State badge",         "Colour-coded badge: blue=in progress, green=deployed, red=failed"),
        (3, "Started column",      "Relative time (e.g. '3 minutes ago')"),
        (4, "Initiated By column", "Email of the user who started the run"),
        (5, "Arrow → button",      "Click to open the Diff Review page for that run"),
    ]:
        elems.append(StepBox(n, title, desc))
        elems.append(Spacer(1, 0.12*cm))

    elems.append(Spacer(1, 0.2*cm))
    elems.append(Paragraph(
        "Click <b>View all</b> (top right of the table) to go to Story Intake and see "
        "every workflow run, not just the most recent 10.", S["body"]))

    elems.append(PageBreak())
    return elems


# ── Section 5: Story Intake ───────────────────────────────────────────────────

def section_story_intake(S):
    elems = []
    elems.append(SectionHeader(5, "Story Intake",
        "http://localhost:5173/stories  —  start workflows & action approvals"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "Story Intake has two panels side by side: the <b>New Workflow Run form</b> "
        "(left) and the <b>Pending Approvals list</b> (right).", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Part A — Starting a New Workflow Run", S["h3"]))
    elems.append(UIPanel("Start New Workflow Run", [
        ("Workflow Template", "Select a template… ▾   [dropdown]"),
        ("Jira Issue Key",    "PROJ-123"),
        ("Repository URL",    "https://github.com/org/repo"),
        ("btn",               "▶  Start Workflow", PRIMARY),
    ]))
    elems.append(Paragraph("New workflow run form layout", S["caption"]))

    elems.append(Spacer(1, 0.2*cm))
    for n, title, desc in [
        (1, "Select Workflow Template",
            "Choose from published templates. The seeded 'Standard Feature Delivery' template covers the full SDLC."),
        (2, "Enter Jira Issue Key",
            "Type your story ID, e.g. PROJ-123. This is used to pull story details via the MCP Jira integration."),
        (3, "Enter Repository URL",
            "Full GitHub/GitLab URL, e.g. https://github.com/org/my-service. Used for branch creation and code context."),
        (4, "Click Start Workflow",
            "Creates a WorkflowRun record (state=story_selected) and navigates you to Diff Review for that run."),
    ]:
        elems.append(StepBox(n, title, desc))
        elems.append(Spacer(1, 0.12*cm))

    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph("Part B — Pending Approvals (right panel)", S["h3"]))
    elems.append(Paragraph(
        "Every approval gate in the workflow appears here as an amber-bordered card.", S["body"]))
    elems.append(UIPanel("Pending Approvals", [
        ("badge",   "approve plan",        AMBER_LIGHT,   AMBER),
        ("Run ID",  "Run: abc12345-..."),
        ("badge",   "Requested 2 min ago", GRAY_50,      GRAY_500),
        ("btn",     "✓ Approve",           PRIMARY),
    ]))

    elems.append(Spacer(1, 0.2*cm))
    for n, title, desc in [
        (1, "Read the action type",  "E.g. 'approve plan', 'create branch', 'create pr draft'"),
        (2, "Review in Diff Review", "Click the Run ID link or navigate to Diff Review to inspect the details first"),
        (3, "Click Approve",         "Sets approval status=approved; the workflow engine unblocks the transition"),
        (4, "Click Reject",          "Sets status=rejected; workflow moves to rework_required state"),
    ]:
        elems.append(StepBox(n, title, desc))
        elems.append(Spacer(1, 0.12*cm))

    elems.append(InfoBox("Access control",
        "Only users whose Role has can_approve_plan=True can approve plan gates. "
        "Only users with can_deploy=True can approve deployment gates. "
        "The admin role has all capabilities enabled.",
        PRIMARY_LIGHT, PRIMARY))

    elems.append(PageBreak())
    return elems


# ── Section 6: Diff Review ────────────────────────────────────────────────────

def section_diff_review(S):
    elems = []
    elems.append(SectionHeader(6, "Diff Review",
        "http://localhost:5173/runs/:id/review  —  per-run workflow progress & code inspection"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "Diff Review is the main working screen for a developer. It shows the workflow "
        "progress, available actions for the current state, and the AI-proposed code diff "
        "once changes have been generated.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Layout — Three Columns", S["h3"]))
    layout_data = [
        ["Area", "Content"],
        ["Header",         "Jira key · repository name · working branch · current state badge"],
        ["Left panel",     "Workflow progress tracker — 10 steps with done/active/pending indicators"],
        ["Right top",      "Actions panel — buttons that appear based on current state"],
        ["Right middle",   "Diff viewer — syntax-highlighted code diff (appears at change stages)"],
        ["Right bottom",   "Run details — session ID, started time, initiated by, working branch"],
    ]
    lt = Table(layout_data, colWidths=[4.5*cm, None])
    lt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(lt)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("Workflow Progress Tracker", S["h3"]))
    elems.append(Paragraph(
        "The left panel shows 10 key states as a numbered list:", S["body"]))
    STEPS = [
        "story_selected", "story_analyzed", "plan_generated", "plan_approved",
        "branch_created", "change_proposal_generated", "changes_reviewed",
        "pr_draft_created", "review_approved", "deployed_to_development",
    ]
    elems.append(WorkflowState(STEPS, current="plan_generated"))
    elems.append(Paragraph(
        "Example: run is at 'plan_generated' — steps 1–2 are green (done), step 3 is highlighted (current)",
        S["caption"]))

    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph("State-specific Action Buttons", S["h3"]))
    actions = [
        ["Current State",          "Button(s) shown",                   "What it does"],
        ["story_selected",         "Analyze Story",                     "Triggers StoryAnalysisAgent (async)"],
        ["plan_generated",         "Approve Plan / Request Rework",     "Gates branch creation. Rework → rework_required"],
        ["changes_reviewed",       "Create PR Draft",                   "Triggers PRPackagingAgent and PR creation via MCP"],
        ["review_approved",        "Request Deployment",                "Moves to deployment_pending; Celery polls CI/CD"],
        ["any non-terminal state", "Cancel Run",                        "Moves run to closed state immediately"],
    ]
    at = Table(actions, colWidths=[4.5*cm, 5.5*cm, None])
    at.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(at)
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Code Diff Viewer", S["h3"]))
    elems.append(Paragraph(
        "The diff viewer appears automatically when the run reaches "
        "<b>change_proposal_generated</b>, <b>changes_reviewed</b>, or <b>pr_draft_created</b>.",
        S["body"]))
    diff_data = [
        ["Line colour",   "Meaning"],
        ["Green (+)",     "Line added by the AI agent"],
        ["Red (–)",       "Line removed / replaced"],
        ["Blue (@@)",     "Hunk header — shows context position in file"],
        ["Yellow (diff)", "File header — shows which file was changed"],
        ["Gray",          "Context line — unchanged surrounding code"],
    ]
    dt = Table(diff_data, colWidths=[4*cm, None])
    dt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#111827")),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1), "Courier-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#1f2937"), colors.HexColor("#111827")]),
        ("TEXTCOLOR",     (0,1), (0,1), colors.HexColor("#86efac")),
        ("TEXTCOLOR",     (0,2), (0,2), colors.HexColor("#fca5a5")),
        ("TEXTCOLOR",     (0,3), (0,3), colors.HexColor("#93c5fd")),
        ("TEXTCOLOR",     (0,4), (0,4), colors.HexColor("#fde68a")),
        ("TEXTCOLOR",     (0,5), (0,5), colors.HexColor("#9ca3af")),
        ("TEXTCOLOR",     (1,1), (1,-1), colors.HexColor("#d1d5db")),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#374151")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(dt)

    elems.append(PageBreak())
    return elems


# ── Section 7: Flow Builder ───────────────────────────────────────────────────

def section_flow_builder(S):
    elems = []
    elems.append(SectionHeader(7, "Flow Builder",
        "http://localhost:5173/flow-builder  —  visual workflow template designer"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "The Flow Builder lets you design new workflow templates using a drag-and-drop "
        "ReactFlow canvas. It comes pre-loaded with a sample feature delivery pipeline.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Toolbar (top bar)", S["h3"]))
    toolbar = [
        ["Control",             "Description"],
        ["Node type dropdown",  "Select the type of node to add next (8 types available)"],
        ["Add Node button",     "Adds the selected node type to the canvas at a random position"],
        ["Save button",         "Serialises the canvas and saves the template definition (shows 'Saved!' briefly)"],
    ]
    tt = Table(toolbar, colWidths=[5*cm, None])
    tt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(tt)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("Node Types (right panel palette)", S["h3"]))
    node_types = [
        ["Node Type",    "Colour",    "Purpose"],
        ["Trigger",      "Blue",      "Entry point — e.g. 'Story Selected' event"],
        ["Agent Task",   "Purple",    "LangChain agent execution — e.g. StoryAnalysisAgent"],
        ["MCP Tool",     "Indigo",    "Direct MCP tool call — e.g. GitHub branch create"],
        ["Approval Gate","Amber",     "Human-in-the-loop gate; blocks progression until approved"],
        ["Condition",    "Yellow",    "Branching logic — e.g. complexity > high → extra review"],
        ["PR Action",    "Green",     "Pull request operations — create, update, merge"],
        ["Deploy Action","Teal",      "Deployment trigger — e.g. deploy to dev environment"],
        ["Notification", "Gray",      "Send a Slack/email notification event"],
    ]
    nt = Table(node_types, colWidths=[3.5*cm, 2.5*cm, None])
    nt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(nt)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("Canvas Controls", S["h3"]))
    for n, title, desc in [
        (1, "Pan the canvas",        "Click and drag on empty canvas space to move the viewport"),
        (2, "Zoom in/out",           "Mouse wheel, or use the +/– buttons in the bottom-left Controls panel"),
        (3, "Move a node",           "Click and drag any node to reposition it"),
        (4, "Connect two nodes",     "Hover over the edge of a node until a blue handle appears, then drag to another node"),
        (5, "Delete a node/edge",    "Select it (click) then press Backspace or Delete"),
        (6, "MiniMap (bottom-right)","Shows bird's-eye view of the entire canvas; click to navigate"),
    ]:
        elems.append(StepBox(n, title, desc))
        elems.append(Spacer(1, 0.12*cm))

    elems.append(Spacer(1, 0.2*cm))
    elems.append(InfoBox("Tip",
        "Approval Gate nodes should always sit between high-risk steps (MCP write tools, deploys) "
        "and the preceding agent or trigger. The workflow engine enforces this at runtime.",
        AMBER_LIGHT, AMBER))

    elems.append(PageBreak())
    return elems


# ── Section 8: PR Management ──────────────────────────────────────────────────

def section_pr_management(S):
    elems = []
    elems.append(SectionHeader(8, "Pull Request Management",
        "http://localhost:5173/pull-requests  —  track AI-generated PRs"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "The PR Management page shows all pull request records created by the platform "
        "across all workflow runs. PRs are grouped into <b>Open / Under Review</b> and "
        "<b>Closed / Merged</b> sections.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("PR Card Fields", S["h3"]))
    pr_fields = [
        ["Field",            "Description"],
        ["PR number",        "External PR number (e.g. #42) or 'draft' if not yet pushed to GitHub"],
        ["Status badge",     "draft · open · under review · approved · merged · closed · declined"],
        ["Title",            "AI-generated PR title from PRPackagingAgent"],
        ["Repository",       "Name of the target repository"],
        ["Branch",           "source_branch → target_branch (e.g. feature/PROJ-123 → main)"],
        ["Diff stats",       "+lines added (green)  –lines removed (red)  N files changed"],
        ["Created by",       "Email of the user who triggered the PR packaging step"],
        ["Time",             "Relative time since the PR record was created"],
        ["↗ External link",  "Opens the actual PR on GitHub/GitLab in a new tab (if available)"],
    ]
    prt = Table(pr_fields, colWidths=[4*cm, None])
    prt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(prt)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("PR Status Lifecycle", S["h3"]))
    status_flow = [
        ["Status",       "Meaning",                          "Colour"],
        ["draft",        "PR packaged but not pushed to VCS","Gray"],
        ["open",         "PR created on GitHub/GitLab",      "Blue"],
        ["under_review", "Reviewers assigned, review started","Yellow"],
        ["approved",     "All reviewers approved",           "Green"],
        ["merged",       "PR merged to target branch",       "Purple"],
        ["closed",       "PR closed without merging",        "Gray"],
        ["declined",     "PR rejected",                      "Red"],
    ]
    st = Table(status_flow, colWidths=[3*cm, 7*cm, None])
    st.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(st)

    elems.append(PageBreak())
    return elems


# ── Section 9: Deployment Console ────────────────────────────────────────────

def section_deployments(S):
    elems = []
    elems.append(SectionHeader(9, "Deployment Console",
        "http://localhost:5173/deployments  —  live deployment status (polls every 15s)"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "The Deployment Console shows the history of all deployments to the development "
        "environment. It auto-refreshes every 15 seconds and a manual Refresh button "
        "is available in the top-right corner.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Summary Stats (top row)", S["h3"]))
    elems.append(Paragraph(
        "Three stat cards show: <b>In Progress</b> (blue), <b>Successful</b> (green), "
        "<b>Failed</b> (red) counts for the current deployment list.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Deployment Table Columns", S["h3"]))
    cols = [
        ["Column",      "Description"],
        ["Status",      "pending · in_progress (spinner) · success · failed · rolled_back · cancelled"],
        ["Environment", "Target environment name (e.g. development, staging)"],
        ["Deployed By", "Email of user who triggered the deployment request"],
        ["Commit",      "First 8 chars of the commit SHA being deployed"],
        ["Duration",    "How many seconds the deployment took (blank if still running)"],
        ["Started",     "Relative time (e.g. '5 minutes ago')"],
        ["Links",       "↗ Pipeline URL (CI/CD run) and Logs link if available"],
    ]
    ct = Table(cols, colWidths=[3.5*cm, None])
    ct.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(ct)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(InfoBox("Auto-refresh behaviour",
        "The page polls the API every 15 seconds automatically. An 'in_progress' row shows "
        "a spinning icon on the status. The Celery task poll_deployment_status also updates "
        "the status from the real CI/CD pipeline in the background.",
        TEAL_LIGHT, TEAL))

    elems.append(PageBreak())
    return elems


# ── Section 10: Audit Timeline ────────────────────────────────────────────────

def section_audit(S):
    elems = []
    elems.append(SectionHeader(10, "Audit Timeline",
        "http://localhost:5173/audit  —  immutable append-only event log"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "The Audit Timeline provides a complete, tamper-proof log of every action taken "
        "on the platform — by users, agents, or the system. Records cannot be edited or deleted.",
        S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Category Filter Buttons (top right)", S["h3"]))
    elems.append(Paragraph(
        "Click any category badge to filter events. The active filter turns indigo. "
        "Click <b>All</b> to clear the filter.", S["body"]))
    cats = [
        ["Category",  "Icon",  "Events included"],
        ["All",       "—",     "Show every event regardless of category"],
        ["workflow",  "⊞",     "Workflow run state transitions"],
        ["agent",     "🤖",    "LangChain agent start, complete, fail"],
        ["mcp_call",  "⊕",     "Every MCP tool invocation and its result"],
        ["approval",  "✓",     "Approval decisions (approved / rejected / expired)"],
        ["pr",        "⑂",    "Pull request created, updated, merged"],
        ["deployment","🚀",    "Deployment triggered, succeeded, failed"],
        ["auth",      "🔒",    "Login, logout, token refresh"],
        ["admin",     "⚙",    "User/role/team changes, MCP capability sync"],
    ]
    ctt = Table(cats, colWidths=[2.8*cm, 1.5*cm, None])
    ctt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("ALIGN",         (1,0), (1,-1), "CENTER"),
    ]))
    elems.append(ctt)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("Event Item Fields", S["h3"]))
    for n, title, desc in [
        (1, "Coloured icon",      "Category-specific icon and background colour (purple=workflow, amber=approval, etc.)"),
        (2, "Action name",        "What happened, e.g. 'workflow.advance' or 'approval.decided'"),
        (3, "Result badge",       "Green 'success' or red badge for the action outcome"),
        (4, "Actor email",        "Who triggered the event (user email or 'system' for automated events)"),
        (5, "Target description", "What resource was acted upon, e.g. 'WorkflowRun abc123'"),
        (6, "Timestamp",          "Exact time in 'MMM D HH:mm:ss' format (UTC)"),
        (7, "Correlation ID",     "Monospace UUID linking this event to a specific HTTP request chain"),
    ]:
        elems.append(StepBox(n, title, desc))
        elems.append(Spacer(1, 0.12*cm))

    elems.append(Spacer(1, 0.2*cm))
    elems.append(InfoBox("Immutability guarantee",
        "AuditEvent.save() raises a RuntimeError if you attempt to update an existing record. "
        "This is enforced at the Django model layer, making the audit log legally defensible "
        "for compliance and non-repudiation purposes.",
        RED_LIGHT, RED))

    elems.append(PageBreak())
    return elems


# ── Section 11: Workflow State Machine ───────────────────────────────────────

def section_state_machine(S):
    elems = []
    elems.append(SectionHeader(11, "Workflow State Machine",
        "The 17-state lifecycle every WorkflowRun passes through"))
    elems.append(Spacer(1, 0.4*cm))

    ALL_STATES = [
        "session_created", "story_selected", "story_analyzed", "plan_generated",
        "plan_approved", "repository_confirmed", "branch_created", "context_prepared",
        "change_proposal_generated", "changes_reviewed", "pr_draft_created",
        "review_pending", "review_approved", "deployment_pending",
        "deployed_to_development", "rework_required", "closed",
    ]
    elems.append(WorkflowState(ALL_STATES, current="change_proposal_generated",
        width=PAGE_W - 2*MARGIN))
    elems.append(Paragraph(
        "All 17 states — current example at 'change_proposal_generated' (indigo); "
        "green = completed; white = not yet reached",
        S["caption"]))
    elems.append(Spacer(1, 0.4*cm))

    transitions = [
        ["Action (trigger)",     "From State",               "To State",                "Approval required?"],
        ["select_story",         "session_created",          "story_selected",          "No"],
        ["analyze_story",        "story_selected",           "story_analyzed",          "No"],
        ["generate_plan",        "story_analyzed",           "plan_generated",          "No"],
        ["approve_plan",         "plan_generated",           "plan_approved",           "YES — plan gate"],
        ["confirm_repository",   "plan_approved",            "repository_confirmed",    "No"],
        ["create_branch",        "repository_confirmed",     "branch_created",          "YES — branch gate"],
        ["prepare_context",      "branch_created",           "context_prepared",        "No"],
        ["generate_changes",     "context_prepared",         "change_proposal_generated","No"],
        ["review_changes",       "change_proposal_generated","changes_reviewed",        "No"],
        ["create_pr_draft",      "changes_reviewed",         "pr_draft_created",        "YES — pr gate"],
        ["submit_for_review",    "pr_draft_created",         "review_pending",          "No"],
        ["approve_review",       "review_pending",           "review_approved",         "No"],
        ["request_deployment",   "review_approved",          "deployment_pending",      "No"],
        ["confirm_deployed",     "deployment_pending",       "deployed_to_development", "No"],
        ["request_rework",       "any",                      "rework_required",         "No"],
        ["close",                "any non-terminal",         "closed",                  "No"],
    ]
    tr_table = Table(transitions, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, None])
    tr_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 7.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("TEXTCOLOR",     (3,1), (3,-1), AMBER),
        ("FONTNAME",      (3,1), (3,-1), "Helvetica-Bold"),
    ]))
    elems.append(tr_table)

    elems.append(PageBreak())
    return elems


# ── Section 12: Admin Panel ───────────────────────────────────────────────────

def section_admin(S):
    elems = []
    elems.append(SectionHeader(12, "Django Admin Panel",
        "http://localhost:8000/admin/  —  superuser management interface"))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph(
        "The Django Admin panel is separate from the React UI. It is used by "
        "superusers to manage platform data directly.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Accessing the Admin Panel", S["h3"]))
    for n, title, desc in [
        (1, "Open http://localhost:8000/admin/", "Django admin login page"),
        (2, "Log in with admin@sdlc.local / admin123", "Must be superuser=True"),
        (3, "You see the full model list",  "All models grouped by app"),
    ]:
        elems.append(StepBox(n, title, desc))
        elems.append(Spacer(1, 0.12*cm))

    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph("Key Admin Tasks", S["h3"]))
    admin_tasks = [
        ["Task",                     "Where in Admin",                   "How"],
        ["Create a new user",        "Accounts → Users → Add",           "Set email, password, role"],
        ["Create/edit a Role",       "Accounts → Roles → Add/Change",    "Toggle capability flags"],
        ["Create a Team",            "Accounts → Teams → Add",           "Assign users to team"],
        ["View workflow templates",  "Workflows → Workflow Templates",    "See all templates + versions"],
        ["Enable an MCP capability", "Mcp Client → MCP Capabilities",    "Set is_enabled=True"],
        ["View all audit events",    "Audit → Audit Events",             "Read-only, cannot edit"],
        ["View agent run logs",      "Agents → Agent Runs",              "See input/output/error per run"],
    ]
    at = Table(admin_tasks, colWidths=[4.5*cm, 5*cm, None])
    at.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_50]),
        ("GRID",          (0,0), (-1,-1), 0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(at)
    elems.append(Spacer(1, 0.4*cm))

    elems.append(InfoBox("MCP Capability management",
        "Any newly discovered MCP tool with write capability is disabled by default (is_enabled=False). "
        "A superuser must review the capability in Admin and set is_enabled=True before the platform "
        "will invoke it. This is a core security constraint of the platform.",
        RED_LIGHT, RED))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Swagger API Explorer", S["h3"]))
    elems.append(Paragraph(
        "Visit <b>http://localhost:8000/api/docs/</b> for the interactive Swagger UI. "
        "Click Authorize and enter your JWT token to test any endpoint directly from the browser.",
        S["body"]))

    return elems


# ── Page footer callback ──────────────────────────────────────────────────────

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawString(MARGIN, 1.2*cm, "Agentic SDLC Automation Platform — Developer UI Guide v1.0")
    canvas.drawRightString(PAGE_W - MARGIN, 1.2*cm, f"Page {doc.page}")
    canvas.setStrokeColor(GRAY_200)
    canvas.line(MARGIN, 1.5*cm, PAGE_W - MARGIN, 1.5*cm)
    canvas.restoreState()


# ── Build ─────────────────────────────────────────────────────────────────────

def build():
    out = "c:/GIT-REPO/agentic-SDLC-automation-platform/Agentic_SDLC_Platform_Developer_Guide.pdf"
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=2*cm,
        title="Agentic SDLC Platform — Developer UI Guide",
        author="AISmithy",
    )
    S = make_styles()
    story = []
    story += cover_page(S)
    story += toc_page(S)
    story += section_getting_started(S)
    story += section_login(S)
    story += section_navigation(S)
    story += section_dashboard(S)
    story += section_story_intake(S)
    story += section_diff_review(S)
    story += section_flow_builder(S)
    story += section_pr_management(S)
    story += section_deployments(S)
    story += section_audit(S)
    story += section_state_machine(S)
    story += section_admin(S)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF written: {out}")


if __name__ == "__main__":
    build()
