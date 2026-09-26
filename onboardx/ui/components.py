"""
Composants d'affichage Streamlit pour OnboardX.
Centralise tous les éléments visuels pour garder app.py propre et lisible.
"""

from __future__ import annotations

import streamlit as st

from onboardx.core.llm_analyzer import AnalysisResult
from onboardx.core.network_parser import NetworkMeta
from onboardx.ui.export import generate_markdown, generate_pdf, report_filename


# ---------------------------------------------------------------------------
# En-tête
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CSS global injecté une seule fois
# ---------------------------------------------------------------------------

_GLOBAL_CSS = """
<style>
/* Bouton primaire Streamlit → accent violet */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6d28d9, #4f46e5);
    color: #fff;
    border: none;
    font-weight: 600;
    letter-spacing: 0.02em;
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
    transition: opacity 0.2s;
}
div.stButton > button[kind="primary"]:hover {
    opacity: 0.88;
}
/* Titres de section h2 → accent violet */
h2 {
    color: #4f46e5 !important;
    font-size: 1.25rem !important;
    margin-top: 1.4rem !important;
}
/* Download buttons → style cohérent */
div.stDownloadButton > button {
    border-radius: 8px;
    font-weight: 500;
}
</style>
"""


def render_header(title: str, subtitle: str, icon: str) -> None:
    """Affiche le titre et le sous-titre de l'application avec le CSS global."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding: 2rem 1rem 1rem 1rem;
            background: linear-gradient(160deg, #1e1b4b 0%, #312e81 60%, #4f46e5 100%);
            border-radius: 12px;
            margin-bottom: 0.5rem;
        ">
            <span style="font-size:3.2rem; filter:drop-shadow(0 2px 4px rgba(0,0,0,0.4));">{icon}</span>
            <h1 style="
                margin: 0.3rem 0 0.15rem 0;
                font-size: 3rem;
                font-weight: 800;
                letter-spacing: -0.02em;
                color: #ffffff;
                text-shadow: 0 2px 8px rgba(0,0,0,0.3);
            ">{title}</h1>
            <p style="
                color: #c7d2fe;
                font-size: 1.05rem;
                margin: 0;
                font-weight: 400;
                letter-spacing: 0.01em;
            ">{subtitle}</p>
        </div>
        <div style="
            height: 4px;
            background: linear-gradient(90deg, #6d28d9, #4f46e5, #818cf8);
            border-radius: 0 0 4px 4px;
            margin-bottom: 1.8rem;
        "></div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Badges réseau rapides
# ---------------------------------------------------------------------------

def render_network_badges(meta: NetworkMeta) -> None:
    """Affiche de petits badges de synthèse extraits statiquement de la config."""
    if meta.is_empty:
        return

    cols = st.columns(4)
    badge_data = [
        ("🏷️ Hostname", meta.hostname or "—"),
        ("🔌 VLANs", str(len(meta.vlans)) if meta.vlans else "0"),
        ("🖧 Interfaces", str(len(meta.interfaces)) if meta.interfaces else "0"),
        ("🛡️ ACL", str(len(meta.acl_ids)) if meta.acl_ids else "0"),
    ]
    for col, (label, value) in zip(cols, badge_data):
        with col:
            st.metric(label=label, value=value)


# ---------------------------------------------------------------------------
# Résultats de l'analyse
# ---------------------------------------------------------------------------

def render_analysis_results(result: AnalysisResult) -> None:
    """Affiche le résultat complet de l'analyse LLM de manière structurée."""

    if result.error:
        st.error(f"**Erreur lors de l'analyse :**\n\n{result.error}")
        return

    st.success("✅ Analyse terminée avec succès !")
    st.markdown('<div style="height:0.2rem;background:linear-gradient(90deg,#6d28d9,#4f46e5,#818cf8);border-radius:2px;margin:0.8rem 0 1.2rem 0;"></div>', unsafe_allow_html=True)

    # --- Section 0a : Score de risque global ---
    _render_risk_score(result.risk_score)

    # --- Section 0b : Vulnérabilités détectées ---
    _render_vulnerabilities(result.vulnerabilities)

    # --- Section 1 : Résumé du projet ---
    with st.container():
        st.markdown('<h2 style="color:#4f46e5;font-size:1.25rem;margin-top:1.4rem;">📦 Résumé du projet</h2>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="
                background:#f0f9ff;
                border-left: 4px solid #3b82f6;
                border-radius: 6px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
            ">
            {_md_to_html_safe(result.project_summary)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Section 2 : Architecture réseau ---
    with st.container():
        st.markdown('<h2 style="color:#4f46e5;font-size:1.25rem;margin-top:1.4rem;">🌐 Architecture réseau</h2>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="
                background:#f0fdf4;
                border-left: 4px solid #22c55e;
                border-radius: 6px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
            ">
            {_md_to_html_safe(result.network_summary)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Section 3 : Points d'entrée ---
    with st.container():
        st.markdown('<h2 style="color:#4f46e5;font-size:1.25rem;margin-top:1.4rem;">🎯 Points d\'entrée principaux</h2>', unsafe_allow_html=True)
        if result.entry_points:
            for i, point in enumerate(result.entry_points, start=1):
                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        align-items:flex-start;
                        gap:0.75rem;
                        background:#fefce8;
                        border-left: 4px solid #eab308;
                        border-radius: 6px;
                        padding: 0.6rem 1rem;
                        margin-bottom: 0.5rem;
                    ">
                        <span style="
                            font-weight:700;
                            color:#ca8a04;
                            font-size:1.1rem;
                            min-width:1.5rem;
                        ">{i}.</span>
                        <span style="color:#1f2328;">{point}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aucun point d'entrée identifié.")

    # --- Section optionnelle : JSON brut ---
    with st.expander("🔍 Voir la réponse brute du LLM", expanded=False):
        st.code(result.raw_response, language="json")

    # --- Export du rapport ---
    st.markdown('<div style="height:0.2rem;background:linear-gradient(90deg,#6d28d9,#4f46e5,#818cf8);border-radius:2px;margin:1.2rem 0 0.8rem 0;"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#4f46e5;font-size:1.25rem;">📥 Exporter le rapport</h2>', unsafe_allow_html=True)
    col_md, col_pdf = st.columns(2)

    with col_md:
        md_content = generate_markdown(result)
        st.download_button(
            label="📥 Télécharger en Markdown",
            data=md_content.encode("utf-8"),
            file_name=report_filename("md"),
            mime="text/markdown",
            use_container_width=True,
        )

    with col_pdf:
        try:
            pdf_bytes = generate_pdf(result)
            st.download_button(
                label="📄 Télécharger en PDF",
                data=pdf_bytes,
                file_name=report_filename("pdf"),
                mime="application/pdf",
                use_container_width=True,
            )
        except ImportError:
            st.warning("⚠️ `fpdf2` n'est pas installé. Lancez `pip install fpdf2` pour activer l'export PDF.")


# ---------------------------------------------------------------------------
# Sections sécurité
# ---------------------------------------------------------------------------

_SEVERITY_ORDER = {"critique": 0, "moyen": 1, "faible": 2}
_SEVERITY_BADGE = {
    "critique": ("🔴", "#fee2e2", "#dc2626"),
    "moyen":    ("🟡", "#fef9c3", "#ca8a04"),
    "faible":   ("🟢", "#dcfce7", "#16a34a"),
}


def _render_risk_score(score: int) -> None:
    """Affiche le score de risque global sous forme d'anneau SVG + barre colorée."""
    score = max(0, min(10, score))

    if score <= 3:
        color, label, bg, border = "#16a34a", "Faible",   "#f0fdf4", "#86efac"
    elif score <= 6:
        color, label, bg, border = "#d97706", "Modéré",   "#fefce8", "#fde68a"
    else:
        color, label, bg, border = "#dc2626", "Critique", "#fff1f2", "#fca5a5"

    # Anneau SVG (stroke-dasharray trick)
    radius = 38
    circumference = 2 * 3.14159 * radius  # ≈ 238.76
    fill_arc = circumference * (score / 10)
    gap_arc  = circumference - fill_arc

    fill_pct = score * 10  # pour la barre linéaire

    st.markdown(
        f"""
        <div style="
            background:{bg};
            border:1px solid {border};
            border-radius:12px;
            padding:1.2rem 1.6rem;
            margin-bottom:1.4rem;
            display:flex;
            align-items:center;
            gap:1.6rem;
        ">
            <!-- Anneau SVG -->
            <div style="flex-shrink:0;">
                <svg width="96" height="96" viewBox="0 0 96 96" style="transform:rotate(-90deg);">
                    <circle cx="48" cy="48" r="{radius}"
                        fill="none" stroke="#e5e7eb" stroke-width="10"/>
                    <circle cx="48" cy="48" r="{radius}"
                        fill="none" stroke="{color}" stroke-width="10"
                        stroke-linecap="round"
                        stroke-dasharray="{fill_arc:.2f} {gap_arc:.2f}"/>
                </svg>
                <div style="
                    position:relative;
                    top:-68px;
                    text-align:center;
                    font-size:1.5rem;
                    font-weight:800;
                    color:{color};
                    line-height:1;
                    height:0;
                ">{score}<span style="font-size:0.7rem; font-weight:500; color:#6b7280;">/10</span></div>
            </div>
            <!-- Texte + barre -->
            <div style="flex:1; min-width:0;">
                <div style="font-weight:700; font-size:1.1rem; color:#1f2328; margin-bottom:0.25rem;">
                    🛡️ Score de risque global
                </div>
                <div style="
                    display:inline-block;
                    background:{color};
                    color:#fff;
                    font-size:0.78rem;
                    font-weight:700;
                    letter-spacing:0.06em;
                    text-transform:uppercase;
                    padding:0.18rem 0.7rem;
                    border-radius:999px;
                    margin-bottom:0.75rem;
                ">{label}</div>
                <!-- Barre de progression -->
                <div style="background:#e5e7eb; border-radius:999px; height:10px; overflow:hidden;">
                    <div style="
                        width:{fill_pct}%;
                        height:100%;
                        background:linear-gradient(90deg, {color}aa, {color});
                        border-radius:999px;
                    "></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:0.3rem;">
                    <span style="font-size:0.72rem; color:#9ca3af;">0 — Sûr</span>
                    <span style="font-size:0.72rem; color:#9ca3af;">10 — Critique</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Libellés lisibles pour les badges de sévérité
_SEVERITY_LABEL_FR = {"critique": "Critique", "moyen": "Modéré", "faible": "Faible"}


def _render_vulnerabilities(vulnerabilities: list[dict]) -> None:
    """Affiche les vulnérabilités triées par sévérité sous forme de cartes enrichies."""
    if not vulnerabilities:
        return

    sorted_vulns = sorted(
        vulnerabilities,
        key=lambda v: _SEVERITY_ORDER.get(v.get("severity", "faible"), 2),
    )

    st.markdown(
        '<h2 style="color:#4f46e5;font-size:1.25rem;margin-top:1.4rem;">🔐 Vulnérabilités détectées</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:#6b7280; font-size:0.88rem; margin-bottom:1rem;'>"
        f"{len(sorted_vulns)} vulnérabilité(s) identifiée(s) — triée(s) par sévérité décroissante.</p>",
        unsafe_allow_html=True,
    )

    for vuln in sorted_vulns:
        severity       = vuln.get("severity", "faible")
        category       = vuln.get("category", "Autre")
        location       = vuln.get("location", "—")
        description    = vuln.get("description", "")
        recommendation = vuln.get("recommendation", "")

        emoji, bg_color, accent = _SEVERITY_BADGE.get(severity, _SEVERITY_BADGE["faible"])
        label_fr = _SEVERITY_LABEL_FR.get(severity, severity.capitalize())

        expander_title = f"{emoji} {category}  —  {label_fr}"
        with st.expander(expander_title, expanded=(severity == "critique")):
            st.markdown(
                f"""
                <div style="
                    background:{bg_color};
                    border-left: 5px solid {accent};
                    border-radius: 0 8px 8px 0;
                    padding: 1rem 1.3rem 1rem 1.2rem;
                    margin-bottom: 0.2rem;
                ">
                    <!-- En-tête carte : catégorie + badge sévérité -->
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.65rem;">
                        <span style="
                            font-size:1rem;
                            font-weight:700;
                            color:#1f2328;
                            letter-spacing:-0.01em;
                        ">{category}</span>
                        <span style="
                            background:{accent};
                            color:#fff;
                            font-size:0.72rem;
                            font-weight:700;
                            letter-spacing:0.07em;
                            text-transform:uppercase;
                            padding:0.2rem 0.75rem;
                            border-radius:999px;
                        ">{label_fr}</span>
                    </div>
                    <!-- Localisation -->
                    <p style="margin:0 0 0.55rem 0; font-size:0.85rem; color:#57606a;">
                        📍 <span style="font-weight:600; color:#374151;">Localisation :</span>
                        &nbsp;<code style="
                            background:#f3f4f6;
                            color:#1f2328;
                            padding:0.15rem 0.5rem;
                            border-radius:4px;
                            font-size:0.82rem;
                        ">{location}</code>
                    </p>
                    <!-- Description -->
                    <p style="
                        margin:0 0 0.75rem 0;
                        color:#1f2328;
                        font-size:0.92rem;
                        line-height:1.55;
                    ">{description}</p>
                    <!-- Recommandation -->
                    <div style="
                        background:#f0fdf4;
                        border: 1px solid #86efac;
                        border-radius: 6px;
                        padding: 0.6rem 1rem;
                    ">
                        <span style="font-weight:700; color:#15803d; font-size:0.87rem;">✅ Recommandation :</span>
                        <span style="color:#1f2328; font-size:0.87rem;"> {recommendation}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div style="height:0.15rem;background:#e5e7eb;border-radius:2px;margin:1rem 0 1.2rem 0;"></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _md_to_html_safe(text: str) -> str:
    """
    Convertit minimalement le markdown en HTML inlineable dans st.markdown.
    Streamlit gère déjà le markdown natif, donc on se contente de retourner
    le texte brut (il sera rendu dans un div via unsafe_allow_html).
    On remplace les sauts de ligne pour le rendu HTML.
    """
    # Préserve les listes markdown comme HTML
    lines = text.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{line.strip()[2:]}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if line.startswith("### "):
                html_lines.append(f"<h4>{line[4:]}</h4>")
            elif line.startswith("## "):
                html_lines.append(f"<h3>{line[3:]}</h3>")
            elif line.startswith("**") and line.endswith("**"):
                html_lines.append(f"<strong>{line[2:-2]}</strong>")
            elif line.strip() == "":
                html_lines.append("<br>")
            else:
                # Gestion inline bold
                import re
                line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
                line = re.sub(r"`(.+?)`", r"<code>\1</code>", line)
                html_lines.append(f"<p style='margin:0.2rem 0;'>{line}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

def render_footer() -> None:
    st.markdown(
        """
        <hr style="margin-top:3rem; border-color:#e5e7eb;">
        <p style="text-align:center; color:#9ca3af; font-size:0.8rem;">
            OnboardX — Propulsé par Groq (Llama / GPT-OSS) &nbsp;|&nbsp; Hackathon IBM Bob
        </p>
        """,
        unsafe_allow_html=True,
    )
