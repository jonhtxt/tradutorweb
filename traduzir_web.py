import requests
from bs4 import BeautifulSoup
import deepl
import time

# Sua chave da API DeepL
auth_key = "60bec253-fcec-437a-a2d8-cc1d3d8d196a:fx"
translator = deepl.Translator(auth_key)

# URL da página que você quer traduzir
url = "https://pt.wikipedia.org/wiki/Intelig%C3%AAncia_artificial"  # você pode trocar isso

# Coleta o conteúdo HTML da página
resposta = requests.get(url)
soup = BeautifulSoup(resposta.text, "html.parser")

# Pega todo o texto visível dos parágrafos <p>
paragrafos = soup.find_all("p")
texto_coletado = [p.get_text().strip() for p in paragrafos if p.get_text().strip()]

# Traduz e salva os resultados
traduzido_final = []

for texto in texto_coletado:
    try:
        resultado = translator.translate_text(texto, target_lang="EN-US")
        print(f"\n🔍 Detectado: {resultado.detected_source_lang}")
        print(f"🔁 Original: {texto[:100]}...")
        print(f"✅ Traduzido: {resultado.text[:100]}...\n")
        traduzido_final.append(resultado.text)
        time.sleep(1)  # para não estourar o limite da API
    except Exception as e:
        print(f"Erro ao traduzir: {e}")
        traduzido_final.append("[Erro nesta parte]")

# Salvar em um arquivo de texto traduzido
with open("pagina_traduzida.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(traduzido_final))

print("\n✅ Tradução completa salva em 'pagina_traduzida.txt'")
