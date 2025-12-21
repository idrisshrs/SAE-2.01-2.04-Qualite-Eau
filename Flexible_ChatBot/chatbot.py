import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
# Selon le goat on doit pip install tout ça pip install langchain langgraph langchain-core langchain-community langchain-huggingface huggingface-hub faiss-cpu python-dotenv pip install sentence-transformers
# Importations spécifiques pour la base de vecteurs
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Charge les variables d'environnement depuis le fichier .env (ex: GOOGLE_API_KEY)
load_dotenv()

# Assurez-vous que la clé API Google est bien définie
# Si elle n'est pas récupérée via load_dotenv(), vous pouvez décommenter la ligne suivante :
# os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialise le modèle d'embedding pour la vectorisation du texte
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialise la base de données de vecteurs et le retriever à None
# Ils seront chargés si le fichier existe, sinon l'application démarrera sans eux.
db = None
retriever = None

# Définit le chemin du dossier de la base de vecteurs pour plus de clarté
VECTODB_PATH = "Flexible_ChatBot/vectordb"
INDEX_FAISS_FILE = os.path.join(VECTODB_PATH, "index.faiss") # Nom standard du fichier d'index FAISS

print("\n--- Initialisation du Chatbot ---")
# Vérifie si le répertoire de la base de données et le fichier d'index existent avant de tenter le chargement
if os.path.isdir(VECTODB_PATH) and os.path.exists(INDEX_FAISS_FILE):
    try:
        # Tente de charger la base de données FAISS locale
        db = FAISS.load_local(VECTODB_PATH, embedding, allow_dangerous_deserialization=True)
        # Crée un retriever à partir de la base de données pour récupérer les documents pertinents
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        print(f"Base de données vectorielle chargée avec succès depuis '{VECTODB_PATH}'.")
    except RuntimeError as e:
        # Gère les erreurs si le chargement échoue (ex: fichier corrompu)
        print(f"ERREUR : Échec du chargement de la base de données vectorielle depuis '{VECTODB_PATH}'. Exception : {e}")
        print("Les fichiers de la base de données pourraient être corrompus ou inaccessibles.")
else:
    # Informe l'utilisateur si la base de données n'est pas trouvée
    print(f"INFO : Répertoire de la base de données vectorielle '{VECTODB_PATH}' ou fichier 'index.faiss' non trouvé.")
    print("Veuillez exécuter 'python index_data.py' dans le répertoire 'Flexible_ChatBot' pour la créer.")
    print("Le chatbot fonctionnera sans le contexte du site tant que la base de données n'est pas chargée (nécessite un redémarrage de l'application).")

# Affiche l'état final de l'initialisation de la base de données
print(f"Base de données initialisée : {'Oui' if db is not None else 'Non'}")
print("--- Initialisation du Chatbot terminée ---\n")


# Définit l'état du graphe LangGraph
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] # Liste des messages dans la conversation
    language: str # Langue (actuellement non utilisée activement mais peut l'être)

# Initialise le modèle de chat (ici, Gemini-2.0-flash de Google)
model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# Définit le prompt strict qui force le bot à ne répondre qu'à partir du contexte fourni
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant qui répond uniquement avec les informations fournies dans le contexte ci-dessous. "
               "Si l'information n'est pas présente dans le contexte, dis simplement que tu ne sais pas."),
    MessagesPlaceholder(variable_name="messages"), # Placeholder pour l'historique des messages
    ("user", "Voici le contexte du site :\n{context}\nQuestion: {question}") # Template pour la question de l'utilisateur avec le contexte
])


# Fonction principale du noeud du modèle dans LangGraph
def call_model(state: State):
    messages = state["messages"]

    # Extrait le contenu du dernier message de l'utilisateur pour l'utiliser comme requête
    if isinstance(messages, list) and messages:
        query = messages[-1].content
    else:
        # Gestion des cas où les messages ne sont pas valides ou sont vides
        print("Avertissement : L'état des messages n'est pas une liste ou est vide. Impossible d'extraire la requête.")
        response_content = "Désolé, je n'ai pas pu comprendre votre requête."
        return {"messages": [HumanMessage(content=response_content)]}

    # Vérifie si le retriever est initialisé. Si non, fournit une réponse par défaut.
    if retriever is None:
        print(f"Utilisateur : {query} -> Bot : (Pas de contexte disponible)")
        response_content = "Désolé, la base de connaissances du site n'est pas encore chargée. Je ne peux pas répondre aux questions basées sur le contenu du site pour le moment. Veuillez lancer 'index_data.py' (une fois que l'application est démarrée dans un autre terminal), puis relancer cette application."
        return {"messages": [HumanMessage(content=response_content)]}

    # Si le retriever est disponible, procède à la récupération des documents pertinents
    docs = retriever.invoke(query)

    print("\n=== Documents Récupérés ===")
    if docs:
        for i, doc in enumerate(docs):
            print(f"[{i+1}] {doc.page_content[:300]}...\n") # Affiche un aperçu des documents
        doc_texts = "\n\n".join([d.page_content for d in docs]) # Concatène le contenu des documents
    else:
        print("Aucun document pertinent trouvé dans la base de données vectorielle.")
        doc_texts = "Aucun contexte spécifique trouvé." # Fournit un contexte vide si aucun document n'est trouvé

    # Construit le prompt final à envoyer au modèle avec les messages et le contexte
    final_prompt = qa_prompt.invoke({
        "messages": messages,
        "context": doc_texts,
        "question": query
    })

    # S'assure que le prompt est bien une chaîne de caractères pour l'appel au modèle
    final_prompt_str = final_prompt.to_string() if hasattr(final_prompt, "to_string") else str(final_prompt)

    print("\n=== Prompt envoyé au modèle ===\n", final_prompt_str[:1000], "\n")

    # Appelle le modèle de chat avec le prompt final
    response = model.invoke(final_prompt_str)
    return {"messages": [response]} # Retourne la réponse du modèle

# Configuration du workflow LangGraph
workflow = StateGraph(state_schema=State)
workflow.add_node("model", call_model) # Ajoute le noeud 'model' qui exécute call_model
workflow.add_edge(START, "model") # Définit la transition du démarrage vers le noeud 'model'
memory = MemorySaver() # Active la persistance de l'état de la conversation en mémoire
app = workflow.compile(checkpointer=memory) # Compile le graphe pour l'exécution

# Fonction exposée pour l'API Flask (app.py)
def ask_bot(question: str, thread_id="web-thread-1") -> str:
    # Configure la persistance de la conversation par un ID de thread
    config = {"configurable": {"thread_id": thread_id}}
    # Crée un message humain à partir de la question de l'utilisateur
    input_messages = [HumanMessage(content=question)]
    # Invoque le graphe LangGraph avec l'input et la configuration
    output = app.invoke({"messages": input_messages, "language": "fr"}, config)
    # Retourne le contenu du dernier message (la réponse du bot)
    return output["messages"][-1].content
