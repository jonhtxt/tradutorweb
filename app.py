from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import deepl
import os
import fitz  # PyMuPDF
import docx
import tempfile

# Configura o Flask
app = Flask(__name__)

# DeepL API KEY (via variáveis de ambiente)
auth_key = os.environ.get("DEEPL_AUTH_KEY")
translator = deepl.Translator(auth_key)

# HTML simples da interface
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tradutor Web</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f2f2f2; }
        input[type=text], input[type=file] { width: 80%%; padding: 10px; margin-bottom: 10px; }
        button { padding: 10px 20px; }
        textarea { width: 100%%; height: 300px; margin-top: 20px; }
    </style>
</head>
<body>
    <h2>Tradutor Web (URL ou Arquivo)</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="text" name="url" placeholder="Cole a URL aqui (opcional)" />
        <br>
        <input type="file" name="arquivo" accept=".pdf,.docx" />
        <br>
        <button type="submit">Traduzir</button>
    </form>
    {% if traducao %}
    <h3>Resultado:</h3>
    <textarea readonly>{{ traducao }}</textarea>
    {% endif %}
</body>
</html>
"""

# Divide texto em blocos menores (para evitar erro 413)
def dividir_em_blocos(texto, tamanho=4500):
    return [texto[i:i+tamanho] for i in range(0, len(texto), tamanho)]

# Extrai texto de PDF
def extrair_texto_pdf(caminho):
    texto = ""
    with fitz.open(caminho) as pdf:
        for pagina in pdf:
            texto += pagina.get_text()
    return texto

# Extrai texto de DOCX
def extrair_texto_docx(caminho):
    doc = docx.Document(caminho)
    texto = " ".join(p.text for p in doc.paragraphs if p.text.strip())
    return texto

@app.route("/", methods=["GET", "POST"])
def index():
    traducao = ""
    if request.method == "POST":
        url = request.form.get("url")
        arquivo = request.files.get("arquivo")

        try:
            texto = ""

            # Se URL foi fornecida
            if url:
                resposta = requests.get(url, timeout=10)
                if resposta.status_code != 200:
                    traducao = "Erro: não foi possível acessar a página."
                else:
                    soup = BeautifulSoup(resposta.text, "html.parser")
                    tags = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'li'])
                    texto = " ".join(tag.get_text().strip() for tag in tags if tag.get_text().strip())

            # Se arquivo foi enviado
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
                traducao = "Erro: não foi possível encontrar texto útil para traduzir."
            elif len(texto) > 100000:
                traducao = "Erro: o conteúdo é muito grande para tradução automática."
            else:
                partes = dividir_em_blocos(texto)
                traducao_partes = []
                for parte in partes:
                    resultado = translator.translate_text(parte, target_lang="EN-US")
                    traducao_partes.append(resultado.text)
                traducao = "\n\n".join(traducao_partes)

        except Exception as e:
            traducao = f"Erro durante o processo: {e}"

    return render_template_string(HTML, traducao=traducao)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

