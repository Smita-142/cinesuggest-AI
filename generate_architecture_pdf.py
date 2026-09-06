import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, Polygon, Group, String as DString

def draw_arrow(drawing, x1, y1, x2, y2, color=colors.HexColor("#64748B"), width=2, head_size=7, bidirectional=False):
    """Draw a line with an arrowhead at the end (or both ends)."""
    drawing.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=width))
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    
    # Arrow head at (x2, y2)
    p1_x = x2 - head_size * math.cos(angle - math.pi / 6)
    p1_y = y2 - head_size * math.sin(angle - math.pi / 6)
    p2_x = x2 - head_size * math.cos(angle + math.pi / 6)
    p2_y = y2 - head_size * math.sin(angle + math.pi / 6)
    drawing.add(Polygon([x2, y2, p1_x, p1_y, p2_x, p2_y], fillColor=color, strokeColor=color))
    
    if bidirectional:
        rev_angle = angle + math.pi
        p1_rx = x1 - head_size * math.cos(rev_angle - math.pi / 6)
        p1_ry = y1 - head_size * math.sin(rev_angle - math.pi / 6)
        p2_rx = x1 - head_size * math.cos(rev_angle + math.pi / 6)
        p2_ry = y1 - head_size * math.sin(rev_angle + math.pi / 6)
        drawing.add(Polygon([x1, y1, p1_rx, p1_ry, p2_rx, p2_ry], fillColor=color, strokeColor=color))

def create_card(drawing, x, y, w, h, title, subtitle_lines, fill_color, border_color, title_color=colors.white, text_color=colors.HexColor("#E2E8F0"), rx=8, ry=8):
    """Helper to draw a rounded card with title and bullet points."""
    drawing.add(Rect(x, y, w, h, rx=rx, ry=ry, fillColor=fill_color, strokeColor=border_color, strokeWidth=1.5))
    
    # Title bar / text
    title_y = y + h - 18
    drawing.add(DString(x + w / 2, title_y, title, textAnchor="middle", fontName="Helvetica-Bold", fontSize=11, fillColor=title_color))
    
    # Separator line
    drawing.add(Line(x + 10, title_y - 6, x + w - 10, title_y - 6, strokeColor=border_color, strokeWidth=0.8))
    
    # Subtitle lines
    line_y = title_y - 20
    for line in subtitle_lines:
        drawing.add(DString(x + 12, line_y, line, fontName="Helvetica", fontSize=8.5, fillColor=text_color))
        line_y -= 13

def build_architecture_pdf(output_path):
    # Landscape A4: 841.89 x 595.27 points
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        leftMargin=25,
        rightMargin=25,
        topMargin=25,
        bottomMargin=25
    )
    
    story = []
    
    # =========================================================================
    # PAGE 1: VISUAL ARCHITECTURE DIAGRAM
    # =========================================================================
    
    # Header styling
    header_dw = Drawing(790, 45)
    header_dw.add(Rect(0, 0, 790, 45, rx=6, ry=6, fillColor=colors.HexColor("#0F172A"), strokeColor=colors.HexColor("#1E293B"), strokeWidth=1))
    header_dw.add(DString(20, 24, "CineSuggest-AI / CineMatch-AI", fontName="Helvetica-Bold", fontSize=16, fillColor=colors.HexColor("#38BDF8")))
    header_dw.add(DString(20, 10, "End-to-End System & Machine Learning Architecture", fontName="Helvetica", fontSize=10, fillColor=colors.HexColor("#94A3B8")))
    header_dw.add(DString(770, 17, "Production Blueprint v1.0", textAnchor="end", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor("#10B981")))
    story.append(header_dw)
    story.append(Spacer(1, 10))
    
    # Main Diagram Canvas (790 x 460)
    dw = Drawing(790, 460)
    
    # Background Canvas
    dw.add(Rect(0, 0, 790, 460, rx=8, ry=8, fillColor=colors.HexColor("#090D16"), strokeColor=colors.HexColor("#1E293B"), strokeWidth=1))
    
    # Grid lines subtle accent
    for gx in range(40, 780, 50):
        dw.add(Line(gx, 0, gx, 460, strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.5))
    for gy in range(40, 460, 50):
        dw.add(Line(0, gy, 790, gy, strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.5))
        
    # ------------------ NODES DEFINITION ------------------
    # 1. USER NODE
    dw.add(Rect(20, 220, 110, 80, rx=10, ry=10, fillColor=colors.HexColor("#1E1B4B"), strokeColor=colors.HexColor("#818CF8"), strokeWidth=2))
    dw.add(Circle(75, 272, 12, fillColor=colors.HexColor("#818CF8"), strokeColor=colors.HexColor("#C7D2FE"), strokeWidth=1))
    dw.add(DString(75, 246, "CLIENT USER", textAnchor="middle", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.white))
    dw.add(DString(75, 232, "Web Browser", textAnchor="middle", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#A5B4FC")))

    # 2. FRONTEND NODE (React 19 + Vite)
    create_card(
        dw, x=160, y=170, w=155, h=180,
        title="React 19 + Vite",
        subtitle_lines=[
            "• Single Page App (SPA)",
            "• React Router v7",
            "• Discover & Home Page",
            "• Live Search Bar",
            "• Movie Details & Ratings",
            "• My List (Favorites)",
            "• Watch History Log",
            "• AI Recommendations",
            "• LocalStorage Sessions"
        ],
        fill_color=colors.HexColor("#0B253A"),
        border_color=colors.HexColor("#06B6D4"),
        title_color=colors.HexColor("#22D3EE"),
        text_color=colors.HexColor("#CFFAFE")
    )
    
    # 3. FASTAPI BACKEND (CENTRAL CORE)
    create_card(
        dw, x=345, y=160, w=175, h=200,
        title="FastAPI Backend Core",
        subtitle_lines=[
            "• Python ASGI (Uvicorn)",
            "• REST API (JSON)",
            "• CORS Middleware",
            "• /auth (Register/Login)",
            "• /movies (Catalog & Search)",
            "• /ratings (Live Ingestion)",
            "• /favorites (My List)",
            "• /watch-history (Logs)",
            "• /recommendations Router",
            "• SQLAlchemy ORM"
        ],
        fill_color=colors.HexColor("#2D124D"),
        border_color=colors.HexColor("#A855F7"),
        title_color=colors.HexColor("#E9D5FF"),
        text_color=colors.HexColor("#F3E8FF")
    )
    
    # 4. TMDB API (EXTERNAL SERVICE) - TOP
    create_card(
        dw, x=345, y=380, w=175, h=70,
        title="TMDB API (External)",
        subtitle_lines=[
            "• High-Res Posters & Backdrops",
            "• Synopses, Runtimes & Genres",
            "• Live New Releases Proxy"
        ],
        fill_color=colors.HexColor("#3B0721"),
        border_color=colors.HexColor("#F43F5E"),
        title_color=colors.HexColor("#FECDD3"),
        text_color=colors.HexColor("#FFE4E6")
    )
    
    # 5. MYSQL DATABASE - BOTTOM
    create_card(
        dw, x=345, y=10, w=175, h=130,
        title="MySQL Database",
        subtitle_lines=[
            "• Database: Cinematch_ai",
            "• users (Accounts & Passwords)",
            "• user_ml_mapping (ML Bridge)",
            "• movies (Enriched Catalog)",
            "• ratings (MovieLens 100k)",
            "• user_ratings (Live Ratings)",
            "• favorites & watch_history"
        ],
        fill_color=colors.HexColor("#063327"),
        border_color=colors.HexColor("#10B981"),
        title_color=colors.HexColor("#6EE7B7"),
        text_color=colors.HexColor("#D1FAE5")
    )
    
    # 6. MACHINE LEARNING ENGINE - RIGHT
    create_card(
        dw, x=550, y=150, w=220, h=220,
        title="Machine Learning Engine",
        subtitle_lines=[
            "• Core Recommender (ml/recommender.py)",
            "• MovieLens 100K Dataset (9.7k movies)",
            "1. User-Based CF (Cosine Sim)",
            "2. Item-Based CF (Cosine Sim)",
            "3. SVD Matrix Factorization (Latent)",
            "4. Hybrid Ensemble Formula:",
            "   Score = 0.30*User + 0.30*Item + 0.40*SVD",
            "• Match % = (Score / 5.0) * 100",
            "5. New User Cold-Start Recommender",
            "   Dynamic projection of live ratings"
        ],
        fill_color=colors.HexColor("#331F06"),
        border_color=colors.HexColor("#F59E0B"),
        title_color=colors.HexColor("#FDE68A"),
        text_color=colors.HexColor("#FEF3C7")
    )
    
    # ------------------ CONNECTING ARROWS ------------------
    # User -> Frontend
    draw_arrow(dw, 130, 260, 160, 260, color=colors.HexColor("#818CF8"), width=2)
    dw.add(DString(145, 266, "Interacts", textAnchor="middle", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#C7D2FE")))
    
    # Frontend <-> FastAPI Backend
    draw_arrow(dw, 315, 260, 345, 260, color=colors.HexColor("#06B6D4"), width=2.5, bidirectional=True)
    dw.add(DString(330, 268, "REST API", textAnchor="middle", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#22D3EE")))
    dw.add(DString(330, 250, "JSON", textAnchor="middle", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#94A3B8")))

    # FastAPI <-> TMDB API (Vertical top)
    draw_arrow(dw, 432, 360, 432, 380, color=colors.HexColor("#F43F5E"), width=2.5, bidirectional=True)
    dw.add(DString(432, 368, "HTTP Requests (Posters/Meta)", textAnchor="middle", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#FDA4AF")))

    # FastAPI <-> MySQL Database (Vertical bottom)
    draw_arrow(dw, 432, 160, 432, 140, color=colors.HexColor("#10B981"), width=2.5, bidirectional=True)
    dw.add(DString(432, 148, "SQL Queries (Read / Write)", textAnchor="middle", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#6EE7B7")))

    # FastAPI <-> Machine Learning Engine (Horizontal right)
    draw_arrow(dw, 520, 260, 550, 260, color=colors.HexColor("#F59E0B"), width=2.5, bidirectional=True)
    dw.add(DString(535, 268, "Inference", textAnchor="middle", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#FDE68A")))
    dw.add(DString(535, 250, "Top-N Recs", textAnchor="middle", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#94A3B8")))

    # ML to MySQL link (Ratings data loop)
    dw.add(Line(660, 150, 660, 75, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=1.2, strokeDashArray=[4, 3]))
    dw.add(Line(660, 75, 520, 75, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=1.2, strokeDashArray=[4, 3]))
    draw_arrow(dw, 530, 75, 520, 75, color=colors.HexColor("#F59E0B"), width=1.5)
    dw.add(DString(600, 80, "Reads user_ratings for Cold-Start", textAnchor="middle", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor("#FCD34D")))

    story.append(dw)
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 2: ARCHITECTURE SPECIFICATIONS & DATA FLOW
    # =========================================================================
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'Heading2',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=6,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )

    story.append(Paragraph("CineSuggest-AI: Architectural Specifications & Flow", title_style))
    story.append(Paragraph("Technical reference guide documenting component responsibilities, data interfaces, and machine learning formulations for the CineMatch-AI / CineSuggest-AI platform.", body_style))
    story.append(Spacer(1, 6))

    # Architecture Breakdown Table
    table_data = [
        [
            Paragraph("<b>Layer / Component</b>", body_style),
            Paragraph("<b>Technologies</b>", body_style),
            Paragraph("<b>Primary Responsibilities</b>", body_style),
            Paragraph("<b>Data Interfaces</b>", body_style)
        ],
        [
            Paragraph("<b>Presentation Layer</b>", body_style),
            Paragraph("React 19, Vite, React Router v7, Vanilla CSS", body_style),
            Paragraph("• Responsive Netflix-style UI<br/>• Discover carousels & live search view<br/>• Movie detail viewer with dynamic routing<br/>• Star ratings, watchlist & history management", body_style),
            Paragraph("Calls FastAPI REST endpoints via Native Fetch (JSON over HTTP on Port 8000)", body_style)
        ],
        [
            Paragraph("<b>Application Layer</b>", body_style),
            Paragraph("FastAPI, Uvicorn, SQLAlchemy, PyMySQL, Bcrypt", body_style),
            Paragraph("• Central orchestrator for all business logic & API routes<br/>• User authentication & password hashing<br/>• Hybrid catalog search (MySQL first, TMDB fallback)<br/>• Rating, Watchlist, and History management<br/>• Recommendation dispatcher", body_style),
            Paragraph("Inbound: React HTTP Requests<br/>Outbound: PyMySQL to Database, Requests to TMDB, In-process ML calls", body_style)
        ],
        [
            Paragraph("<b>Machine Learning Core</b>", body_style),
            Paragraph("Scikit-Learn, Scikit-Surprise, Pandas, NumPy, Joblib", body_style),
            Paragraph("• <b>User-Based CF:</b> Cosine similarity on User-Item matrix<br/>• <b>Item-Based CF:</b> Cosine similarity on Item-User matrix<br/>• <b>SVD Matrix Factorization:</b> Latent user-item factors<br/>• <b>Hybrid Formula:</b> 0.30*User + 0.30*Item + 0.40*SVD<br/>• <b>Cold-Start Recommender:</b> Live user rating weights", body_style),
            Paragraph("Loads MovieLens CSVs, SVD pickle model; reads live user_ratings from MySQL for users > 610", body_style)
        ],
        [
            Paragraph("<b>Database Layer</b>", body_style),
            Paragraph("MySQL (Cinematch_ai)", body_style),
            Paragraph("• Persistent storage for users and application data<br/>• <b>user_ml_mapping:</b> Bridges app users to ML ID space<br/>• <b>user_ratings:</b> Live submitted user reviews<br/>• <b>movies:</b> Enriched metadata from TMDB", body_style),
            Paragraph("SQLAlchemy ORM session pool over localhost:3306", body_style)
        ],
        [
            Paragraph("<b>External Services</b>", body_style),
            Paragraph("The Movie Database (TMDB) API v3", body_style),
            Paragraph("• High-resolution poster & backdrop image CDN<br/>• Live Now-Playing and upcoming releases<br/>• Movie synopses, runtimes, and genres", body_style),
            Paragraph("HTTPS REST API (api.themoviedb.org)", body_style)
        ]
    ]

    spec_table = Table(table_data, colWidths=[110, 130, 340, 200])
    spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    story.append(spec_table)
    story.append(Spacer(1, 6))

    # Flow Explanation
    story.append(Paragraph("Execution Workflow & Interaction Stages", h2_style))
    flow_steps = [
        "<b>1. User Registration & ML Bridge:</b> When a user registers (/auth/register), FastAPI creates a record in `users` and automatically maps them in `user_ml_mapping` with an ML ID starting from 611 (MovieLens users occupy 1-610).",
        "<b>2. Dynamic Search Flow:</b> The user types in the React search bar. FastAPI checks MySQL first. If absent, it queries TMDB live, ensuring unlimited movie discovery without manual catalog entry.",
        "<b>3. User Rating Ingestion:</b> When the user rates a film (1-5 stars) on the details page, the rating is committed directly to `user_ratings` in MySQL.",
        "<b>4. Recommendation Pipeline:</b> Visiting `/recommendations/{user_id}` inspects `ml_user_id`: If benchmark user (<=610), it runs the full Hybrid formula (30% User-CF + 30% Item-CF + 40% SVD). If a new app user (>610), it fetches their real ratings from MySQL, calculates cosine similarity against the MovieLens matrix, weights by rating, and normalizes scores to 0-100% Match."
    ]
    for step in flow_steps:
        story.append(Paragraph(step, body_style))
        story.append(Spacer(1, 2))

    doc.build(story)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    output = "c:/Users/khush/OneDrive/Desktop/New folder (2)/CineMatch-AI/CineSuggest_System_Architecture.pdf"
    build_architecture_pdf(output)
