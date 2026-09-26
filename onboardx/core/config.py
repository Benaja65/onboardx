"""
Configuration centrale de OnboardX.
Chargement des variables d'environnement et constantes de l'application.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Clé API Groq ---
OPENAI_API_KEY: str = os.getenv("GROQ_API_KEY", "")
OPENAI_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

# --- Paramètres LLM ---
LLM_MAX_TOKENS: int = 2048
LLM_TEMPERATURE: float = 0.2

# --- Limites d'entrée ---
MAX_CODE_SIZE_KB: int = 200
MAX_CONFIG_SIZE_KB: int = 100

# --- Titres et labels UI ---
APP_TITLE: str = "OnboardX"
APP_SUBTITLE: str = "Analyse intelligente de code source & infrastructure réseau Cisco"
APP_ICON: str = "🚀"
