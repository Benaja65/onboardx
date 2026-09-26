# 🛡️ OnboardX

> Comprenez un projet et auditez son infrastructure réseau en quelques secondes — grâce à l'IA.

![Propulsé par Groq](https://img.shields.io/badge/Propulsé%20par-Groq%20(Llama%20%2F%20GPT--OSS)-orange?style=flat-square)
![Built with Bob IDE](https://img.shields.io/badge/Built%20with-IBM%20Bob%20IDE-4f46e5?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Interface-Streamlit-ff4b4b?style=flat-square)

---

## 🔴 Le problème

L'onboarding sur un nouveau projet ou une nouvelle infrastructure réseau est
**long, fastidieux et sujet à erreurs**.

Un développeur ou ingénieur qui intègre une équipe doit :
- Comprendre un code existant souvent non documenté, écrit par d'autres ;
- Déchiffrer une configuration réseau Cisco (`show running-config`) de
  plusieurs centaines de lignes ;
- Identifier les zones à risque de sécurité **sans filet**.

Le résultat : une intégration ralentie de plusieurs jours et, surtout, des
**vulnérabilités de sécurité qui passent entre les mailles** faute de contexte
global au moment de la prise en main.

---

## ✅ La solution

**OnboardX** analyse automatiquement du **code source** (Python, JavaScript,
Java, Go…) et une **configuration réseau Cisco** (`show running-config`) pour
générer un rapport d'onboarding structuré piloté par l'IA.

Un rapport OnboardX comprend :

| Section | Contenu |
|---|---|
| 📦 Résumé du projet | Rôle de l'application, technologies identifiées, points clés |
| 🌐 Architecture réseau | Topologie, VLANs, interfaces, routage, services actifs |
| 🎯 Points d'entrée | Interfaces exposées, routes critiques, services accessibles |
| 🛡️ Score de risque | Note globale de 0 (sûr) à 10 (critique) avec jauge visuelle |
| 🔐 Vulnérabilités | Liste catégorisée avec sévérité, localisation et recommandation |

### Exemple de sortie

```
🛡️ Score de risque global : 8/10 — Critique

🔐 Vulnérabilités détectées (3)
  🔴 Injection SQL — critique
     Localisation : app/db.py:42
     La requête est construite par concaténation de chaînes.
     ✅ Utiliser des requêtes paramétrées (cursor.execute(sql, params)).

  🟡 Secret exposé — modéré
     Localisation : config.py:7
     Une clé API est codée en dur dans le fichier source.
     ✅ Déplacer vers une variable d'environnement et ajouter au .gitignore.

  🟢 ACL permissive — faible
     Localisation : interface GigabitEthernet0/1
     L'ACL "permit ip any any" autorise tout le trafic entrant.
     ✅ Restreindre aux plages IP légitimes uniquement.
```

---

## ✨ Fonctionnalités

- **Détection statique rapide** : extraction immédiate du hostname, des VLANs,
  interfaces et identifiants ACL sans appel LLM.
- **Analyse approfondie par IA** : le modèle Groq (Llama / GPT-OSS) comprend
  le contexte du code *et* de la configuration réseau pour produire un rapport
  cohérent.
- **Catégorisation des vulnérabilités** avec sévérité (`critique` / `modéré` /
  `faible`) : injection SQL, injection de commande, secrets exposés, mauvaise
  gestion des erreurs, configuration réseau non sécurisée, contrôles d'accès
  insuffisants, etc.
- **Score de risque global 0–10** avec jauge visuelle (anneau SVG coloré).
- **Export** du rapport en **Markdown** et **PDF** (via `fpdf2`).

---

## 🚀 Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/Benaja65/onboardx.git
cd onboardx

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la clé API Groq
#    Obtenez votre clé sur https://console.groq.com
cp .env.example .env
# Éditez .env et renseignez :
# GROQ_API_KEY=<votre_clé_groq>

# 4. Lancer l'interface
python -m streamlit run app.py
```

> **Note :** `fpdf2` est requis pour l'export PDF. Il est inclus dans
> `requirements.txt`. Si vous voulez uniquement l'export Markdown, vous pouvez
> l'omettre — l'application affiche un avertissement non bloquant.

---

## 🖥️ Utilisation

1. **Collez votre code source** dans la zone de gauche (ou uploadez un fichier
   `.py`, `.js`, `.java`, `.go`, etc.).
2. **Collez la sortie de `show running-config`** dans la zone de droite (ou
   uploadez un fichier `.txt` / `.cfg`).
3. Cliquez sur **🔍 Analyser** — l'analyse prend généralement 5 à 15 secondes.
4. Consultez le rapport : score de risque, vulnérabilités, résumé du projet,
   architecture réseau, points d'entrée.
5. **Exportez** le rapport en Markdown ou en PDF via les boutons de
   téléchargement.

> Vous pouvez aussi charger les données d'exemple intégrées via
> **📂 Charger les exemples** dans le panneau latéral.

---

## 🧰 Stack technique

| Composant | Technologie |
|---|---|
| Interface utilisateur | [Streamlit](https://streamlit.io) ≥ 1.32 |
| LLM | [Groq API](https://console.groq.com) — modèle `openai/gpt-oss-20b` |
| Client API | `openai` ≥ 1.25 (compatible Groq via `base_url`) |
| Export PDF | [fpdf2](https://py-pdf.github.io/fpdf2/) ≥ 2.7 |
| Variables d'environnement | `python-dotenv` ≥ 1.0 |
| Langage | Python 3.11+ |

---

## 🤖 Développé avec IBM Bob IDE

Ce projet a été entièrement construit dans le cadre du **Hackathon IBM Bob 2.0**
en utilisant **IBM Bob IDE** comme assistant de développement.

Chaque étape de construction — architecture, code, tests, refactoring — a été
réalisée en sessions de tâches documentées. Les captures de session sont
disponibles dans le dossier [`bob_sessions/`](bob_sessions/) :

| Session | Sujet |
|---|---|
| `task01` | Création du projet OnboardX — structure, parser Cisco, LLM analyzer |
| `task02` | Migration vers l'API Groq (remplacement OpenAI) |
| `task03` | Catégorisation des vulnérabilités et score de risque |
| `task04` | Export du rapport en Markdown et PDF |
| `task05` | Design et amélioration visuelle de l'interface (jauge de risque, cartes de vulnérabilités, page d'accueil) |
| `task06` | Correction de la référence GROQ_API_KEY dans le panneau Paramètres |

---

## ⚠️ Limites connues

- **Variabilité LLM** : l'analyse dépend de la qualité et de l'état du modèle
  Groq. Les résultats peuvent varier légèrement d'une exécution à l'autre, en
  particulier sur des configurations très longues ou du code très dense.
- **Pas un audit de sécurité complet** : OnboardX est un outil d'aide à
  l'onboarding et de première détection. Il ne remplace pas un audit de
  sécurité professionnel (pentest, analyse statique outillée, revue de code
  humaine).
- **Taille des entrées** : les très grands fichiers (> 100 Ko) peuvent
  dépasser la fenêtre de contexte du modèle et produire des résultats
  tronqués. Préférez des extraits ciblés pour de meilleurs résultats.
- **Langues** : le rapport est généré en français par défaut, en fonction du
  prompt système. D'autres langues ne sont pas encore configurables depuis
  l'interface.

---

<p align="center">
  Made with ❤️ during <strong>IBM Bob Hackathon 2.0</strong>
</p>
