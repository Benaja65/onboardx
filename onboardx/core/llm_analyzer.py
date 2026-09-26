"""
Module d'analyse LLM pour OnboardX.
Construit les prompts, appelle l'API Groq (compatible OpenAI) et parse la réponse structurée.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI

from onboardx.core.config import (
    GROQ_BASE_URL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


# ---------------------------------------------------------------------------
# Structures de données
# ---------------------------------------------------------------------------

@dataclass
class AnalysisResult:
    """Résultat structuré renvoyé par le LLM."""
    project_summary: str = ""
    network_summary: str = ""
    entry_points: list[str] = field(default_factory=list)
    vulnerabilities: list[dict] = field(default_factory=list)
    risk_score: int = 0
    raw_response: str = ""
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
Tu es un expert en sécurité informatique, en architecture logicielle et en infrastructure réseau Cisco.
Tu analyses du code source et des configurations réseau pour aider les équipes
techniques à comprendre rapidement un projet lors d'un onboarding, et pour identifier
les risques de sécurité présents.
Réponds UNIQUEMENT en JSON valide, sans aucun texte avant ou après le JSON.
"""

_USER_PROMPT_TEMPLATE = """\
Analyse les éléments suivants et retourne un objet JSON avec exactement ces cinq clés :

1. "project_summary" : (string, markdown autorisé)
   Un résumé clair du projet : langage(s) détecté(s), frameworks utilisés,
   structure globale et objectif probable de l'application.
   Inclus les dépendances remarquables et le style architectural (MVC, micro-services, etc.).

2. "network_summary" : (string, markdown autorisé)
   Un résumé de l'architecture réseau :
   - VLANs présents et leur rôle
   - Segments IP identifiés
   - Interfaces et leurs modes (access / trunk)
   - ACL / listes d'accès et leur impact
   - Routes statiques ou protocoles de routage
   - Points d'attention sécurité ou de configuration

3. "entry_points" : (liste de strings)
   Les 3 à 6 points d'entrée principaux du code que l'on doit examiner en premier
   lors de l'onboarding (fichiers, classes, fonctions, routes API…).
   Chaque élément doit être une courte phrase explicite.

4. "vulnerabilities" : (liste d'objets)
   La liste de toutes les vulnérabilités de sécurité détectées dans le code et la
   configuration réseau. Chaque objet doit contenir exactement ces cinq champs :
   - "category" : l'une des valeurs suivantes uniquement :
       "Injection SQL" | "Injection de commande" | "Secret exposé" |
       "Configuration réseau non sécurisée" | "Mode debug exposé" | "Autre"
   - "severity" : "critique" | "moyen" | "faible"
   - "location" : nom du fichier, de la fonction ou de la ligne de config concernée
   - "description" : explication courte du risque (une à deux phrases)
   - "recommendation" : correction suggérée en une phrase
   Si aucune vulnérabilité n'est détectée, renvoie une liste vide [].

5. "risk_score" : (entier de 0 à 10)
   Le niveau de risque global du projet, calculé en tenant compte du nombre et de la
   sévérité des vulnérabilités détectées. 10 = risque très critique, 0 = aucun risque.

---
CODE SOURCE :
```
{code}
```

---
CONFIG RÉSEAU CISCO (show running-config) :
```
{network}
```
"""


# ---------------------------------------------------------------------------
# Client LLM
# ---------------------------------------------------------------------------

def _build_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise ValueError(
            "La variable d'environnement GROQ_API_KEY n'est pas définie. "
            "Créez un fichier .env à la racine du projet avec : GROQ_API_KEY=gsk_..."
        )
    return OpenAI(api_key=OPENAI_API_KEY, base_url=GROQ_BASE_URL)


def _parse_json_response(raw: str) -> dict:
    """Extrait le JSON de la réponse (robuste aux balises markdown éventuelles)."""
    # Enlève les éventuels ```json ... ``` wrapper
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return json.loads(cleaned)


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def analyze(code: str, network_config: str) -> AnalysisResult:
    """
    Envoie le code et la config réseau au LLM et retourne un AnalysisResult.

    Parameters
    ----------
    code:           Contenu du code source (texte brut).
    network_config: Contenu de la configuration Cisco (show running-config).

    Returns
    -------
    AnalysisResult avec les champs remplis, ou .error défini en cas d'échec.
    """
    result = AnalysisResult()

    try:
        client = _build_client()

        user_prompt = _USER_PROMPT_TEMPLATE.format(
            code=code.strip() or "(aucun code fourni)",
            network=network_config.strip() or "(aucune configuration réseau fournie)",
        )

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or ""
        result.raw_response = raw

        data = _parse_json_response(raw)
        result.project_summary = data.get("project_summary", "")
        result.network_summary = data.get("network_summary", "")
        result.entry_points = data.get("entry_points", [])
        result.vulnerabilities = data.get("vulnerabilities", [])
        result.risk_score = int(data.get("risk_score", 0))

    except ValueError as exc:
        result.error = str(exc)
    except json.JSONDecodeError as exc:
        result.error = f"Réponse LLM non parseable en JSON : {exc}\n\nRéponse brute :\n{result.raw_response}"
    except Exception as exc:  # noqa: BLE001
        result.error = f"Erreur lors de l'appel au LLM : {exc}"

    return result
