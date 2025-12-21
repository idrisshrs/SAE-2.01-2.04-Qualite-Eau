from scraper import scrape_site
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
# Liste des pages à indexer
def data_scraping():
    urls = [
        "http://127.0.0.1:1000/",
        "http://127.0.0.1:1000/tableau-bord/carte-prelevements",   
        "http://127.0.0.1:1000/tableau-bord/evolution-temporelle",
        "http://127.0.0.1:1000/jeux-donnees/chroniques",
        "http://127.0.0.1:1000/jeux-donnees/points-prelevement",
        "http://127.0.0.1:1000/jeux-donnees/ouvrages",
        "http://127.0.0.1:1000/a-propos/manuel-utilisation",
        "http://127.0.0.1:1000/a-propos/notre-equipe-projet",
        "http://127.0.0.1:1000/contact",
        "http://127.0.0.1:1000/8743b52063cd84097a65d1633f5c74f5"
    ]

    text = scrape_site(urls)

    docs = [Document(page_content=text)]
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs_split = splitter.split_documents(docs)

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs_split, embedding)
    db.save_local("vectordb")

    print("Base vectorielle créée avec", len(docs_split), "documents.")

data_scraping()