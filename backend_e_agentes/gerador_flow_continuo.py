"""
Gerador Autônomo Contínuo de Imagens Gastronômicas via Google Flow (Brave CDP 9222)
Saciara Fitness - Canal @saciara_ / App NutriPlus

REGRA SOBERANA DO USUÁRIO:
- Não reutilizar capas de post de rede social (conteudo-saciara/01.png).
- Utilizar o scraper do Google Flow para gerar INDIVIDUALMENTE cada imagem para cada receita.
- Imagens verticais 9:16, fotografia culinária profissional, cerâmica artesanal, sem textos ou artes de carrossel.
"""

import os
import sys
import json
import time

SHARED_TOOLS_DIR = r"f:\Nova pasta\automação redes sociais\shared_tools"
if SHARED_TOOLS_DIR not in sys.path:
    sys.path.append(SHARED_TOOLS_DIR)

import flow_bridge

OUTPUT_DIR = r"f:\Nova pasta\site\saciara\assets\receitas_flow"
RECEITAS_PATH = r"f:\Nova pasta\site\saciara\receitas.json"
RECEITAS_DATA_JS = r"f:\Nova pasta\site\saciara\js\receitas_data.js"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_slug(name):
    clean = name.lower()
    for c in " ,/\\-()áàãâéêíóôõúüç":
        if c in "áàãâ": clean = clean.replace(c, 'a')
        elif c in "éê": clean = clean.replace(c, 'e')
        elif c in "í": clean = clean.replace(c, 'i')
        elif c in "óôõ": clean = clean.replace(c, 'o')
        elif c in "úü": clean = clean.replace(c, 'u')
        elif c == "ç": clean = clean.replace(c, 'c')
        elif c in " ,/\\-()": clean = clean.replace(c, '_')
    while '__' in clean:
        clean = clean.replace('__', '_')
    return clean.strip('_')

def construir_prompt_gastronomico(titulo, categoria):
    return (
        f"Professional culinary food magazine photography of Brazilian recipe: '{titulo}'. "
        f"Category: {categoria}. Real food styling, artisanal matte ceramic plate or bowl, "
        f"fresh natural ingredients, subtle warm morning window light, gentle steam rising, "
        f"photorealistic 8k, editorial food magazine aesthetic, zero artificial CGI, "
        f"macro food texture, soft bokeh background f/1.8, vertical 9:16 framing, clean presentation, no text, no words, no graphics."
    )

def executar_geracao_lote(limite=5):
    print("="*60)
    print("INICIANDO GERADOR DE IMAGENS FLOW - NUTRIPLUS SACIARA")
    print("="*60)

    with open(RECEITAS_PATH, 'r', encoding='utf-8') as f:
        recs = json.load(f)

    # Identificar receitas que precisam de imagem do Flow
    pendentes = []
    for r in recs:
        capa = r.get('imagem_capa', '')
        tags = [t.lower() for t in r.get('tags', [])]
        if 'mindfulness' in tags or 'estilo de vida' in tags:
            continue
        # Se já tem Flow puro e o arquivo existe
        if 'assets/receitas_flow' in capa:
            rel = capa.lstrip('/')
            full = os.path.join(r"f:\Nova pasta\site\saciara", rel)
            if os.path.exists(full) and os.path.getsize(full) > 10000:
                continue
        pendentes.append(r)

    print(f"Total de receitas no banco: {len(recs)}")
    print(f"Total que precisam de Flow individual: {len(pendentes)}")

    if not pendentes:
        print("Todas as receitas já possuem imagens individuais geradas no Google Flow!")
        return

    lote = pendentes[:limite]
    geradas_com_sucesso = 0

    for i, r in enumerate(lote, 1):
        titulo = r.get('titulo')
        slug = sanitize_slug(titulo)
        out_filename = slug
        expected_path = os.path.join(OUTPUT_DIR, f"{out_filename}.png")

        print(f"\n[{i}/{len(lote)}] Gerando Flow para: '{titulo}'...")
        prompt = construir_prompt_gastronomico(titulo, r.get('categoria', ''))

        try:
            res = flow_bridge.generate_flow_image(
                prompt=prompt,
                output_dir=OUTPUT_DIR,
                filename=out_filename
            )
            image_path = res.get('imagePath', expected_path)
            if res.get('success') and os.path.exists(image_path) and os.path.getsize(image_path) > 10000:
                print(f" -> SUCESSO: {out_filename}.png ({os.path.getsize(image_path)//1024} KB)")
                r['imagem_capa'] = f"assets/receitas_flow/{out_filename}.png"
                geradas_com_sucesso += 1
                
                # Salva a cada imagem gerada com sucesso
                with open(RECEITAS_PATH, 'w', encoding='utf-8') as f:
                    json.dump(recs, f, indent=2, ensure_ascii=False)

                with open(RECEITAS_DATA_JS, 'w', encoding='utf-8') as f:
                    f.write('// Banco de 156 receitas e hábitos do Saciara Fitness\n')
                    f.write('window.BANCO_RECEITAS_156 = ')
                    json.dump(recs, f, indent=2, ensure_ascii=False)
                    f.write(';\n')
            else:
                print(f" -> Falha: {res.get('error')}")
        except Exception as e:
            print(f" -> Erro na chamada: {e}")

        time.sleep(2)

    print(f"\n[OK] Lote concluído: {geradas_com_sucesso}/{len(lote)} geradas.")

if __name__ == '__main__':
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    executar_geracao_lote(limite=limite)
