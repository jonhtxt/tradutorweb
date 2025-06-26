import fitz  # PyMuPDF
import deepl
import time

# 🔐 Sua chave da API DeepL (mantida em sigilo!)
auth_key = "60bec253-fcec-437a-a2d8-cc1d3d8d196a:fx"
translator = deepl.Translator(auth_key)

# 📄 Nome do arquivo original
arquivo_pdf = "texto.pdf"
pdf_original = fitz.open(arquivo_pdf)

# 📄 Novo PDF onde o conteúdo traduzido será salvo
pdf_traduzido = fitz.open()

# 📃 Loop por página
for pagina in pdf_original:
    texto = pagina.get_text().strip()
    if texto:
        try:
            resultado = translator.translate_text(texto, target_lang="EN-US")  # idioma destino
            texto_traduzido = resultado.text
        except deepl.exceptions.DeepLException as e:
            print(f"Erro na tradução: {e}")
            texto_traduzido = "[Erro ao traduzir esta página]"

        # Cria uma nova página e adiciona o texto traduzido
        nova_pagina = pdf_traduzido.new_page(width=pagina.rect.width, height=pagina.rect.height)
        nova_pagina.insert_text((50, 50), texto_traduzido, fontsize=12)
        
        time.sleep(1)  # evitar limite da API gratuita
    else:
        nova_pagina = pdf_traduzido.new_page()
        nova_pagina.insert_text((50, 50), "[Página vazia]")

# 💾 Salva o PDF final
pdf_traduzido.save("texto_traduzido.pdf")
print("✅ Tradução concluída e salva como texto_traduzido.pdf")

# Loop por página
for pagina in pdf_original:
    texto = pagina.get_text().strip()
    if texto:
        try:
            # Sem source_lang: DeepL detecta automaticamente
            resultado = translator.translate_text(texto, target_lang="EN-US")
            print("Idioma detectado:", resultado.detected_source_lang)
            texto_traduzido = resultado.text
        except deepl.exceptions.DeepLException as e:
            print(f"Erro na tradução: {e}")
            texto_traduzido = "[Erro ao traduzir esta página]"
