# rag-boardgame-assistant

## Installation

1. Cloner le projet :

```bash
git clone <url-du-repo>
cd rag-boardgame-assistant
```

2. Créer l'environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Installer Ollama et télécharger le modèle Mistral :

```bash
# Installer Ollama: https://ollama.ai
ollama pull mistral
```

5. Configurer la clé API OpenAI :
   - Obtenir une clé : https://platform.openai.com/api-keys
   - Créer un fichier `.env` à la racine du projet :

```
OPENAI_API_KEY=votre_cle_api_ici
```

## Lancement des chatbot en console

Avec le LLM OpenAI gpt-4o-mini en version gratuite - meilleures réponses et rapidité mais nécessite un compte openAI

```bash
python starter_openai.py
```

ou avec le LLM open source Mistral - réponses plus lentes, mauvais respect du prompt system, mauvaise réponse/invention concernant le document de règle fictif du RAG.

```bash
python starter_mistral.py
```

Exemples de questions pour tester le RAG :

- Salut ça va ?
- Combien y a t-il de pions aux dames ?
- Quel est le but du jeu de BiduleChouette (jeu fictif présent dans les documents du RAG) => ne doit pas inventer de réponse mais donner le but du jeu fictif présent dans test.txt.
- Quel temps fait-il aujourd'hui ? => doit rediriger vers le jeu

A faire / autres idées :

- Intégrer des documents plus longs et de différents formats dans les data (ex: pdf de règles du jeu réels) et tester l'efficacité de l'extraction avec llamaindex
- Tester une extraction par un OCR pour les pdf
- Script pour structurer les règles extraites de façon similaire pour chaque jeu
- Métadonnées/Filtres par jeu, par page, par section
- Demander le nom du jeu en début de chat pour pouvoir filtrer le rag par game.

- Transformer en API fastAPI
- Récupérer les images/légendes pour les afficher en front et lmieux expliquer une règle -> plus complexe
