import requests
from bs4 import BeautifulSoup

def scrape_site(urls):
    all_text = ""

    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n")
            print(f"--- Contenu scrappé depuis {url} ---\n{text[:-1]}\n")
            all_text += text + "\n\n"
        except Exception as e:
            print(f"Erreur lors du scraping de {url} : {e}")

    return all_text
