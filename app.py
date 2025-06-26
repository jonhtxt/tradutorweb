from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import deepl
import os

# Pega a chave da API DeepL do ambiente (Render.com ou local)
auth_key = os.environ.get("60bec253-fcec-437a-a2d8-cc1d3d8d196a:fx")
translator = deepl.Translator(auth_key)

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tradutor Web</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f2f2f2; }
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

# Função para dividir texto em blocos menores
def dividir_em_blocos(texto, tamanho=4500):
    return [texto[i:i+tamanho] for i in range(0, len(texto), tamanho)]

@app.route("/", methods=["GET", "POST"])
def index():
    traducao = ""
    if request.method == "POST":
        url = request.form.get("url")
        try:
            resposta = requests.get(url, timeout=10)
            if resposta.status_code != 200:
                traducao = "Erro: não foi possível acessar a página. Verifique o link."
            else:
                soup = BeautifulSoup(resposta.text, "html.parser")

                # Extrair tags comuns com texto
                tags = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'li'])
                texto = " ".join(tag.get_text().strip() for tag in tags if tag.get_text().strip())

                if not texto or len(texto) < 20:
                    traducao = "Erro: não foi possível encontrar texto útil para traduzir neste site."
                else:
                    # Verificação de tamanho opcional
                    if len(texto) > 100000:
                        traducao = "Erro: o conteúdo da página é muito grande para ser traduzido automaticamente."
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
