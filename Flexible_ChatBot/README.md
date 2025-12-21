# Flexible_ChatBot
A ChatBot that scrapes the given website then outputs


This intelligent chatbot is a flexible and contextual conversational assistant, designed to respond solely based on the actual content of a website. By integrating Langchain, HuggingFace embeddings, and FAISS, it understands user questions, searches for relevant information in indexed web pages, and then generates a coherent response.

Required Modifications for Setup :

    Installation package : pip install Flask python-dotenv langchain langgraph langchain-core langchain-community langchain-huggingface huggingface-hub faiss-cpu sentence-transformers typing-extensions requests beautifulsoup4
    pip install -U langchain-google-genai


    1)
        Go to the .env file and place an API key, ex :
        GOOGLE_API_KEY=CLÉ
        
        here, the key is a Google API key

    2)
        Go to app.py and add the pages you want to register in the root , ex : 
        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/page2")
        def page2():
            return render_template("page2.html")

        @app.route("/page3")
        def page3():
            return render_template("page3.html")
    
    3)
        In chatbot.py, modify the model according to the API that we have set :
        model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
        as well as os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY") 

    4)
       In index_data.py, add the pages in URL format (here the application is local) in the urls dictionary : 
            urls = [
                "http://127.0.0.1:5000/",
                "http://127.0.0.1:5000/page2",   
                "http://127.0.0.1:5000/page3"
            ] 
