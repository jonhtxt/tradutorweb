import os
import requests
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
import deepl
import docx
import fitz  # PyMuPDF
import tempfile  # ✅ ESSA LINHA É A QUE FALTAVA


# Pega a chave da API DeepL do ambiente (Render.com ou local)
auth_key = os.environ.get("DEEPL_AUTH_KEY")
translator = deepl.Translator(auth_key)

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tradutor Web</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f2f2f2; }
        input[type=text], input[type=file] { width: 80%%; padding: 10px; }
        button { padding: 10px 20px; }
        textarea { width: 100%%; height: 300px; margin-top: 20px; }
    </style>
</head>
<body>
    <h2>Tradutor Web (URL ou Arquivo)</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="text" name="url" placeholder="Cole a URL aqui (opcional)" />
        <br><br>
        <input type="file" name="arquivo" accept=".pdf,.docx" />
        <br><br>
        <button type="submit">Traduzir</button>
    </form>
    {% if traducao %}
    <h3>Resultado:</h3>
    <textarea readonly>{{ traducao }}</textarea>
    {% endif %}
</body>
</html>
"""


# Função para dividir texto em blocos menores
def dividir_em_blocos(texto, tamanho=4500):
    return [texto[i:i+tamanho] for i in range(0, len(texto), tamanho)]

@app.route("/", methods=["GET", "POST"])
def index():
    traducao = ""
    if request.method == "POST":
        url = request.form.get("url")
        arquivo = request.files.get("arquivo")

        try:
            texto = ""

            if url:
                resposta = requests.get(url, timeout=10)
                soup = BeautifulSoup(resposta.text, "html.parser")
                tags = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'li'])
                texto = " ".join(tag.get_text().strip() for tag in tags if tag.get_text().strip())

            elif arquivo:
                with tempfile.NamedTemporaryFile(delete=False) as temp:
                    caminho_temp = temp.name
                    arquivo.save(caminho_temp)

                if arquivo.filename.endswith(".pdf"):
                    texto = extrair_texto_pdf(caminho_temp)
                elif arquivo.filename.endswith(".docx"):
                    texto = extrair_texto_docx(caminho_temp)
                else:
                    traducao = "Formato de arquivo não suportado."
                    return render_template_string(HTML, traducao=traducao)

            else:
                traducao = "Você deve fornecer uma URL ou um arquivo."
                return render_template_string(HTML, traducao=traducao)

            if not texto or len(texto) < 20:
                traducao = "Erro: nenhum conteúdo útil encontrado para tradução."
            elif len(texto) > 100000:
                traducao = "Erro: o conteúdo é muito grande para ser traduzido automaticamente."
            else:
                partes = dividir_em_blocos(texto)
                traduzido_final = []
                for parte in partes:
                    resultado = translator.translate_text(parte, target_lang="EN-US")
                    traduzido_final.append(resultado.text)
                traducao = "\n\n".join(traduzido_final)

        except Exception as e:
            traducao = f"Erro durante o processo: {e}"

    return render_template_string(HTML, traducao=traducao)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import fitz  # PyMuPDF
import docx
import tempfile

def extrair_texto_pdf(caminho):
    texto = ""
    with fitz.open(caminho) as pdf:
        for pagina in pdf:
            texto += pagina.get_text()
    return texto

def extrair_texto_docx(caminho):
    doc = docx.Document(caminho)
    texto = " ".join(p.text for p in doc.paragraphs if p.text.strip())
    return texto
