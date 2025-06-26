from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import deepl
import os

# Sua chave da API DeepL
auth_key = "60bec253-fcec-437a-a2d8-cc1d3d8d196a:fx"
translator = deepl.Translator(auth_key)

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tradutor Web</title>
    <style>
        body { font-family: Arial; padding: 20px; background-color: #f2f2f2; }
        input[type=text] { width: 80%%; padding: 10px; }
        button { padding: 10px 20px; }
        textarea { width: 100%%; height: 300px; margin-top: 20px; }
    </style>
</head>
<body>
    <h2>Tradutor de Página Web (DeepL)</h2>
    <form method="POST">
        <input type="text" name="url" placeholder="Cole a URL aqui" required />
        <button type="submit">Traduzir</button>
    </form>
    {% if traducao %}
    <h3>Resultado:</h3>
    <textarea readonly>{{ traducao }}</textarea>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    traducao = ""
    if request.method == "POST":
        url = request.form.get("url")
        try:
            resposta = requests.get(url)
            soup = BeautifulSoup(resposta.text, "html.parser")
            paragrafos = soup.find_all("p")
            tags = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'li'])
            texto = " ".join(tag.get_text().strip() for tag in tags if tag.get_text().strip())
            if texto:
                resultado = translator.translate_text(texto, target_lang="EN-US")
                traducao = resultado.text
            else:
                traducao = "Nenhum texto encontrado na página."
        except Exception as e:
            traducao = f"Erro: {e}"

    return render_template_string(HTML, traducao=traducao)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def pegar_texto_com_selenium(url):
    options = Options()
    options.add_argument("--headless")  # roda o navegador invisível
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Ajuste o caminho do chromedriver abaixo:
    driver = webdriver.Chrome(executable_path="C:/webdrivers/chromedriver.exe", options=options)
    driver.get(url)
    
    # Espera um pouco para a página carregar
    driver.implicitly_wait(5)
    
    html = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(html, "html.parser")
    # Pega textos em várias tags
    tags = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'li'])
    texto = " ".join(tag.get_text().strip() for tag in tags if tag.get_text().strip())
    return texto
    