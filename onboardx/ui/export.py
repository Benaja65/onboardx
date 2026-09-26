"""
Fonctions d'export du rapport d'analyse OnboardX.
Génère un fichier Markdown et un fichier PDF à partir d'un AnalysisResult.
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO

from onboardx.core.llm_analyzer import AnalysisResult

# Ordre de tri des sévérités
_SEVERITY_ORDER = {"critique": 0, "moyen": 1, "faible": 2}
_SEVERITY_LABEL = {"critique": "🔴 CRITIQUE", "moyen": "🟡 MOYEN", "faible": "🟢 FAIBLE"}


# ---------------------------------------------------------------------------
# Nom de fichier horodaté
# ---------------------------------------------------------------------------

def report_filename(extension: str) -> str:
    """Retourne un nom de fichier avec horodatage, ex : onboardx_rapport_20260925_1630.md"""
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    return f"onboardx_rapport_{ts}.{extension}"


# ---------------------------------------------------------------------------
# Export Markdown
# ---------------------------------------------------------------------------

def generate_markdown(result: AnalysisResult) -> str:
    """Génère un rapport complet au format Markdown à partir d'un AnalysisResult."""
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")
    lines: list[str] = []

    lines.append("# 📊 Rapport d'analyse OnboardX")
    lines.append(f"\n**Date de l'analyse :** {now}")
    lines.append("\n---\n")

    # Score de risque
    score = result.risk_score
    if score <= 3:
        level = "Faible"
    elif score <= 6:
        level = "Modéré"
    else:
        level = "Critique"

    lines.append("## 🛡️ Score de risque global")
    lines.append(f"\n**{score}/10 — {level}**\n")
    lines.append("\n---\n")

    # Vulnérabilités
    if result.vulnerabilities:
        sorted_vulns = sorted(
            result.vulnerabilities,
            key=lambda v: _SEVERITY_ORDER.get(v.get("severity", "faible"), 2),
        )
        lines.append("## 🔐 Vulnérabilités détectées")
        lines.append(
            f"\n_{len(sorted_vulns)} vulnérabilité(s) identifiée(s), triée(s) par sévérité décroissante._\n"
        )
        for i, vuln in enumerate(sorted_vulns, start=1):
            severity = vuln.get("severity", "faible")
            category = vuln.get("category", "Autre")
            location = vuln.get("location", "—")
            description = vuln.get("description", "")
            recommendation = vuln.get("recommendation", "")
            badge = _SEVERITY_LABEL.get(severity, severity.upper())

            lines.append(f"### {i}. {category}")
            lines.append(f"\n- **Sévérité :** {badge}")
            lines.append(f"- **Localisation :** `{location}`")
            lines.append(f"- **Description :** {description}")
            lines.append(f"- **Recommandation :** {recommendation}\n")
        lines.append("\n---\n")

    # Résumé du projet
    lines.append("## 📦 Résumé du projet")
    lines.append(f"\n{result.project_summary}\n")
    lines.append("\n---\n")

    # Architecture réseau
    lines.append("## 🌐 Architecture réseau")
    lines.append(f"\n{result.network_summary}\n")
    lines.append("\n---\n")

    # Points d'entrée
    lines.append("## 🎯 Points d'entrée principaux")
    if result.entry_points:
        lines.append("")
        for i, point in enumerate(result.entry_points, start=1):
            lines.append(f"{i}. {point}")
    else:
        lines.append("\n_Aucun point d'entrée identifié._")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Export PDF
# ---------------------------------------------------------------------------

def generate_pdf(result: AnalysisResult) -> bytes:
    """Génère un rapport PDF à partir d'un AnalysisResult. Retourne les bytes du PDF."""
    from fpdf import FPDF  # import local pour ne pas crasher si fpdf2 absent

    def _s(text: str) -> str:
        """Encode en latin-1 en remplaçant les caractères non supportés."""
        return text.encode("latin-1", errors="replace").decode("latin-1")

    _SEVERITY_COLOR = {
        "critique": (220, 38, 38),
        "moyen":    (202, 138, 4),
        "faible":   (22, 163, 74),
    }

    now = datetime.now().strftime("%d/%m/%Y a %H:%M")
    score = result.risk_score
    level = "Faible" if score <= 3 else ("Modere" if score <= 6 else "Critique")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- Titre ---
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(31, 35, 40)
    pdf.cell(0, 12, "Rapport d'analyse OnboardX", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(87, 96, 106)
    pdf.cell(0, 7, _s(f"Date de l'analyse : {now}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    pdf.set_draw_color(229, 231, 235)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    def section_title(text: str) -> None:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(31, 35, 40)
        pdf.cell(0, 9, _s(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def body_text(text: str) -> None:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(31, 35, 40)
        pdf.multi_cell(0, 6, _s(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    def mono_text(text: str) -> None:
        pdf.set_font("Courier", "", 9)
        pdf.set_text_color(55, 65, 81)
        pdf.multi_cell(0, 5, _s(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def divider() -> None:
        pdf.set_draw_color(229, 231, 235)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    # --- Score de risque ---
    section_title("SCORE DE RISQUE GLOBAL")
    r, g, b = _SEVERITY_COLOR.get(
        "critique" if score > 6 else ("moyen" if score > 3 else "faible"),
        (22, 163, 74),
    )
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 8, f"{score}/10  -  {level}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    divider()

    # --- Vulnérabilités ---
    if result.vulnerabilities:
        sorted_vulns = sorted(
            result.vulnerabilities,
            key=lambda v: _SEVERITY_ORDER.get(v.get("severity", "faible"), 2),
        )
        section_title(f"Vulnerabilites detectees  ({len(sorted_vulns)})")
        for i, vuln in enumerate(sorted_vulns, start=1):
            severity = vuln.get("severity", "faible")
            category = vuln.get("category", "Autre")
            location = vuln.get("location", "-")
            description = vuln.get("description", "")
            recommendation = vuln.get("recommendation", "")

            r, g, b = _SEVERITY_COLOR.get(severity, (22, 163, 74))
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(31, 35, 40)
            pdf.cell(0, 7, _s(f"{i}. {category}"), new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(r, g, b)
            pdf.cell(0, 5, _s(f"Severite : {severity.upper()}"), new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(87, 96, 106)
            pdf.cell(0, 5, _s(f"Localisation : {location}"), new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(31, 35, 40)
            pdf.multi_cell(0, 6, _s(description), new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(21, 128, 61)
            pdf.multi_cell(0, 5, _s(f"Recommandation : {recommendation}"), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
        divider()

    # --- Résumé du projet ---
    section_title("Resume du projet")
    body_text(result.project_summary)
    divider()

    # --- Architecture réseau ---
    section_title("Architecture reseau")
    body_text(result.network_summary)
    divider()

    # --- Points d'entrée ---
    section_title("Points d'entree principaux")
    if result.entry_points:
        for i, point in enumerate(result.entry_points, start=1):
            body_text(f"{i}. {point}")
    else:
        body_text("Aucun point d'entree identifie.")

    return bytes(pdf.output())
