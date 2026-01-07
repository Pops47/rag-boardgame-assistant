import os
import shutil
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI 
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import asyncio

# Récupère la clé API OpenAI
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Désactive les logs (requêtes HTTP, etc.)
logging.basicConfig(level=logging.WARNING)

# Setting du LLM et du modèle d'embedding
Settings.llm = OpenAI(
    model="gpt-4o-mini", 
    api_key=OPENAI_API_KEY)

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Création ou chargement de l'index
STORAGE_DIR = "storage"

if os.path.exists(STORAGE_DIR):
    print(f"Chargement de l'index à partir des documents fournis...")
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
    index = load_index_from_storage(
        storage_context,
        embed_model=Settings.embed_model  # Important d'utiliser le même embed_model que l'agent
    )
    print("Index chargé avec succès !")
else:
    print("Création d'un nouvel index à partir des documents fournis...")
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=Settings.embed_model
    )
    # Save the index
    index.storage_context.persist(STORAGE_DIR)
    print(f"Index créé avec succès !")

# Creation du query engine
query_engine = index.as_query_engine(
    llm=Settings.llm,
    response_mode="compact" # Mode de réponse compact pour les réponses courtes
)

async def search_documents(query: str) -> str:
    """Recherche des documents similaires à la question"""
    response = await query_engine.aquery(query)
    return str(response)



# Création de l'agent
agent = FunctionAgent(
    tools=[search_documents],
    llm=Settings.llm,  # même LLM que pour l'indexation
    system_prompt="""Tu es Buddy, un assistant spécialisé dans les jeux de plateau et les jeux de société. 
    Réponds en français uniquement. 
    Soit précis et factuel dans tes réponses. 
    N'invente pas d'informations.
    Quand une question concerne un jeu de plateau ou de société, utilise l'outil search_documents, 
    Si la question ne concerne pas le domaine du jeu de plateau ou de société, 
    réponds poliment et ramène la conversation sur le domaine du jeu de plateau ou de société.
    Si la question n'est pas claire, réponds poliment et invite l'utilisateur à reformuler sa question."""
)

def cleanup(storage_dir: str, ctx: Context = None):
    """ Supprime le storage (index) """
    print("\nNettoyage de l'index...")
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
    print("Nettoyage terminé !")


async def chat(ctx: Context):
    """Boucle de conversation avec l'agent IA"""
    # Présentation du bot et des instructions
    print("\n" + "="*50)
    response = await agent.run("Dis bonjour et présente toi en une ligne", ctx=ctx)
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
        
        # Réponse à la question du user avec l'agent
        try:
            response = await agent.run(user_input, ctx=ctx)
            print(f"Buddy : {response}\n")
        except Exception as e:
            print(f"Erreur : {e}\n")

async def main():
    # Création du contexte pour maintenir l'historique de conversation
    ctx = Context(agent)
    # Lancement du chat
    try:
        await chat(ctx)
    # Gestion d'erreurs
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