"""
OnboardX — Application principale Streamlit.
Point d'entrée : streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from onboardx.core.config import APP_ICON, APP_SUBTITLE, APP_TITLE, MAX_CODE_SIZE_KB, MAX_CONFIG_SIZE_KB
from onboardx.core.llm_analyzer import analyze
from onboardx.core.network_parser import parse_cisco_config
from onboardx.ui.components import (
    render_analysis_results,
    render_footer,
    render_header,
    render_network_badges,
)

# ---------------------------------------------------------------------------
# Chemins des fichiers d'exemple
# ---------------------------------------------------------------------------

_SAMPLE_DIR = Path(__file__).parent / "sample_data"
_SAMPLE_CODE = _SAMPLE_DIR / "exemple_code.py"
_SAMPLE_CISCO = _SAMPLE_DIR / "exemple_cisco.txt"


# ---------------------------------------------------------------------------
# Configuration de la page Streamlit
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_uploaded_file(uploaded_file) -> str:
    """Lit un fichier uploadé et retourne son contenu texte."""
    return uploaded_file.read().decode("utf-8", errors="replace")


def _load_sample(path: Path) -> str:
    """Charge un fichier exemple depuis le disque."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _check_size(content: str, max_kb: int, label: str) -> bool:
    """Avertit si le contenu dépasse la limite de taille. Retourne True si OK."""
    size_kb = len(content.encode("utf-8")) / 1024
    if size_kb > max_kb:
        st.warning(f"⚠️ {label} : le contenu dépasse {max_kb} Ko ({size_kb:.1f} Ko). "
                   "Considérez de réduire la taille pour de meilleures performances.")
    return True  # on laisse passer malgré tout


# ---------------------------------------------------------------------------
# Interface principale
# ---------------------------------------------------------------------------

def main() -> None:
    render_header(APP_TITLE, APP_SUBTITLE, APP_ICON)

    # --- Barre latérale : paramètres ---
    with st.sidebar:
        st.markdown("### ⚙️ Paramètres")
        st.info(
            "Assurez-vous que la variable `GROQ_API_KEY` est définie dans "
            "votre fichier `.env` à la racine du projet."
        )
        st.markdown("---")
        st.markdown("**Exemples intégrés**")
        load_examples = st.button("📂 Charger les exemples", use_container_width=True)
        st.markdown("---")
        st.markdown("**À propos**")
        st.caption(
            "OnboardX analyse votre code source et votre configuration réseau "
            "Cisco pour générer un rapport d'onboarding structuré grâce à l'IA."
        )

    # --- Bloc d'intro (page d'accueil, avant toute analyse) ---
    if "code_value" not in st.session_state or (
        not st.session_state.get("code_value", "").strip()
        and not st.session_state.get("network_value", "").strip()
    ):
        st.markdown(
            """
            <div style="
                background:#f5f3ff;
                border:1px solid #ddd6fe;
                border-radius:12px;
                padding:1.2rem 1.6rem 1rem 1.6rem;
                margin-bottom:1.4rem;
            ">
                <p style="
                    font-weight:700;
                    font-size:1rem;
                    color:#4f46e5;
                    margin:0 0 0.65rem 0;
                ">OnboardX analyse votre infrastructure en quelques secondes.</p>
                <div style="display:flex; flex-wrap:wrap; gap:0.6rem;">
                    <span style="
                        background:#fff;
                        border:1px solid #c4b5fd;
                        border-radius:8px;
                        padding:0.45rem 0.9rem;
                        font-size:0.88rem;
                        color:#4f46e5;
                        font-weight:500;
                    ">🔍 Détectez les injections SQL et XSS dans votre code</span>
                    <span style="
                        background:#fff;
                        border:1px solid #c4b5fd;
                        border-radius:8px;
                        padding:0.45rem 0.9rem;
                        font-size:0.88rem;
                        color:#4f46e5;
                        font-weight:500;
                    ">🔐 Repérez les secrets et credentials exposés</span>
                    <span style="
                        background:#fff;
                        border:1px solid #c4b5fd;
                        border-radius:8px;
                        padding:0.45rem 0.9rem;
                        font-size:0.88rem;
                        color:#4f46e5;
                        font-weight:500;
                    ">🛡️ Auditez vos ACL et configurations Cisco</span>
                </div>
                <p style="font-size:0.8rem; color:#6b7280; margin:0.75rem 0 0 0;">
                    Collez votre code source et/ou votre <code>show running-config</code> ci-dessous,
                    puis lancez l'analyse — un rapport structuré sera généré automatiquement.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Zones de saisie principales ---
    col_left, col_right = st.columns(2, gap="large")

    # Initialisation des valeurs de session
    if "code_value" not in st.session_state:
        st.session_state.code_value = ""
    if "network_value" not in st.session_state:
        st.session_state.network_value = ""

    # Chargement des exemples
    if load_examples:
        st.session_state.code_value = _load_sample(_SAMPLE_CODE)
        st.session_state.network_value = _load_sample(_SAMPLE_CISCO)
        st.rerun()

    with col_left:
        st.markdown("### 💻 Code source")
        st.caption("Collez votre code directement ou uploadez un fichier texte.")

        uploaded_code = st.file_uploader(
            "Uploader un fichier de code",
            type=["py", "js", "ts", "java", "go", "rb", "php", "cs", "cpp", "c", "txt"],
            key="upload_code",
            label_visibility="collapsed",
        )
        if uploaded_code:
            st.session_state.code_value = _read_uploaded_file(uploaded_code)

        code_input = st.text_area(
            "Code source",
            value=st.session_state.code_value,
            height=350,
            placeholder="# Collez votre code source ici...\n# Python, JavaScript, Java, Go, etc.",
            label_visibility="collapsed",
            key="textarea_code",
        )

    with col_right:
        st.markdown("### 🌐 Configuration réseau Cisco")
        st.caption("Collez la sortie de `show running-config` ou uploadez un fichier.")

        uploaded_network = st.file_uploader(
            "Uploader une config Cisco",
            type=["txt", "cfg", "conf", "log"],
            key="upload_network",
            label_visibility="collapsed",
        )
        if uploaded_network:
            st.session_state.network_value = _read_uploaded_file(uploaded_network)

        network_input = st.text_area(
            "Configuration réseau",
            value=st.session_state.network_value,
            height=350,
            placeholder="! Collez ici votre show running-config Cisco...\nhostname Switch-01\n!",
            label_visibility="collapsed",
            key="textarea_network",
        )

    # --- Badges de pré-analyse réseau ---
    if network_input and network_input.strip():
        network_meta = parse_cisco_config(network_input)
        if not network_meta.is_empty:
            st.markdown("**Détection rapide dans la configuration :**")
            render_network_badges(network_meta)
    else:
        network_meta = parse_cisco_config("")

    st.markdown("---")

    # --- Bouton d'analyse ---
    col_btn, col_hint = st.columns([1, 4])
    with col_btn:
        analyze_clicked = st.button(
            "🔍 Analyser",
            type="primary",
            use_container_width=True,
        )
    with col_hint:
        if not code_input.strip() and not network_input.strip():
            st.caption("💡 Remplissez au moins une des deux zones avant d'analyser.")

    # --- Déclenchement de l'analyse ---
    if analyze_clicked:
        if not code_input.strip() and not network_input.strip():
            st.warning("⚠️ Veuillez fournir au moins du code source ou une configuration réseau.")
        else:
            _check_size(code_input, MAX_CODE_SIZE_KB, "Code source")
            _check_size(network_input, MAX_CONFIG_SIZE_KB, "Config réseau")

            with st.spinner("🤖 Analyse en cours avec le LLM… cela peut prendre quelques secondes."):
                result = analyze(code=code_input, network_config=network_input)

            st.markdown("---")
            render_analysis_results(result)

    render_footer()


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
