import os
import shutil
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import asyncio

# Désactiver les logs (requêtes HTTP, etc.)
logging.basicConfig(level=logging.WARNING)

# Settings
Settings.llm = Ollama(
    model="mistral",  # Modèle Ollama open source 
    request_timeout=120.0
)

# Modèle d'embedding Hugging Face open source
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Create or load RAG index
STORAGE_DIR = "storage"

if os.path.exists(STORAGE_DIR):
    # Load existing index
    print(f"Chargement de l'index depuis {STORAGE_DIR}...")
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
    index = load_index_from_storage(
        storage_context,
        embed_model=Settings.embed_model  # Important d'utiliser le même embed_model
    )
    print("Index chargé avec succès !")
else:
    # Create new index
    print("Création d'un nouvel index...")
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=Settings.embed_model
    )
    # Save the index
    index.storage_context.persist(STORAGE_DIR)
    print(f"Index sauvegardé dans {STORAGE_DIR}")

query_engine = index.as_query_engine(
    llm=Settings.llm,
    response_mode="compact"
)

async def search_documents(query: str) -> str:
    response = await query_engine.aquery(query)
    return str(response)


# Create agent
agent = FunctionAgent(
    tools=[search_documents],
    llm=Settings.llm,  # Il faut initialiser le même LLM que pour l'indexation
    system_prompt="""Tu es Buddy, assistant expert en jeux de plateau et jeux de société.

RÈGLES STRICTES:
- Réponds UNIQUEMENT en français
- Pour toute question sur les jeux: utilise search_documents (sans le mentionner)
- Pour questions hors domaine: "Je suis spécialisé dans les jeux de plateau. Comment puis-je t'aider ?"
- Pour questions floues: demande poliment de reformuler
- Ne JAMAIS inventer d'informations - utilise uniquement search_documents et si tu ne trouves pas d'information correspondant à la question indique que tu n'as pas la réponse.

Réponds de manière naturelle, concise et amicale."""
)

def cleanup(storage_dir: str, ctx: Context = None):
    """ Supprime le storage """
    print("\nNettoyage de l'index...")
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
    print("Nettoyage terminé !")

async def chat_loop(ctx: Context):
    """Boucle de conversation interactive avec l'agent"""
    # Présentation du bot au début
    print("\n" + "="*50)
    response = await agent.run("Dis bonjour et présente toi EN UNE SEULE PHRASE", ctx=ctx)
    print(f"Buddy : {response}")
    print("="*50)
    print("\nTapez 'EXIT' pour quitter la conversation.\n")
    print("="*50)
    print("\n")
    
    # Boucle de conversation
    while True:
        user_input = input("Vous : ").strip()
        print("\n")
        
        # Verif exit
        if user_input.upper() == "EXIT":
            print("\nAu revoir et à bientôt !")
            break
        
        # Verif vide
        if not user_input:
            continue
        
        # Réponse avec l'agent
        try:
            response = await agent.run(user_input, ctx=ctx)
            print(f"Buddy : {response}\n")
        except Exception as e:
            print(f"Erreur : {e}\n")

async def main():
    # Création du contexte pour maintenir l'historique de conversation
    ctx = Context(agent)
    try:
        await chat_loop(ctx)
    except KeyboardInterrupt:
        print("\n\nInterruption détectée (Ctrl+C)...")
    except Exception as e:
        print(f"\nErreur inattendue : {e}")
    finally:
        # Nettoyage à la fermeture
        cleanup(STORAGE_DIR, ctx)

# Run the agent
if __name__ == "__main__":
    asyncio.run(main())