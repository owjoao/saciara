"""
Gerador Autônomo Contínuo de Imagens Gastronômicas via Google Flow (Brave CDP 9222)
Saciara Fitness - Canal @saciara_ / App NutriPlus

Regra: Toda receita deve ter uma imagem individual fiel, vertical 9:16, gerada no Flow ou oficial.
Zero imagens genéricas, zero gatos dormindo, zero fallbacks sem relação com o prato.
"""

import os
import sys
import json
import time

SHARED_TOOLS_DIR = r"f:\Nova pasta\automação redes sociais\shared_tools"
if SHARED_TOOLS_DIR not in sys.path:
    sys.path.append(SHARED_TOOLS_DIR)

from flow_bridge import FlowBridge

OUTPUT_DIR = r"f:\Nova pasta\site\saciara\assets\receitas_flow"
RECEITAS_PATH = r"f:\Nova pasta\site\saciara\receitas.json"
RECEITAS_DATA_JS = r"f:\Nova pasta\site\saciara\js\receitas_data.js"
CONTEUDO_SACIARA_DIR = r"f:\Nova pasta\site\saciara\conteudo-saciara"

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

def construir_prompt_gastronomico(titulo, categoria, descricao=""):
    prompt = (
        f"Professional culinary food photography of Brazilian healthy recipe: '{titulo}'. "
        f"Category: {categoria}. Real food styling, artisanal matte ceramic plate or bowl, "
        f"fresh natural ingredients, subtle warm morning window light, gentle steam rising, "
        f"photorealistic 8k, editorial food magazine aesthetic, zero artificial CGI, "
        f"macro food texture, soft bokeh background f/1.8, vertical 9:16 framing, appetizing presentation."
    )
    return prompt

def executar_geracao_lote(limite=5):
    print("="*60)
    print("INICIANDO GERADOR DE IMAGENS FLOW - NUTRIPLUS SACIARA")
    print("="*60)

    with open(RECEITAS_PATH, 'r', encoding='utf-8') as f:
        recs = json.load(f)

    # Identificar receitas que precisam de imagem
    pendentes = []
    for r in recs:
        capa = r.get('imagem_capa', '')
        # Se é hábito, não precisa de Flow culinário
        tags = [t.lower() for t in r.get('tags', [])]
        if 'mindfulness' in tags or 'estilo de vida' in tags:
            continue
        # Se já tem imagem no assets/receitas_flow
        if 'assets/receitas_flow' in capa and os.path.exists(os.path.join(r"f:\Nova pasta\site\saciara", capa.lstrip('/'))):
            continue
        # Se já tem imagem oficial no conteudo-saciara
        if 'conteudo-saciara' in capa and os.path.exists(os.path.join(r"f:\Nova pasta\site\saciara", capa.lstrip('/'))):
            continue
        pendentes.append(r)

    print(f"Total de receitas no banco: {len(recs)}")
    print(f"Total de receitas que precisam de imagem Flow: {len(pendentes)}")

    if not pendentes:
        print("Todas as receitas culinárias já possuem imagens individuais válidas!")
        return

    bridge = FlowBridge(port=9222)
    lote = pendentes[:limite]
    geradas_com_sucesso = 0

    for i, r in enumerate(lote, 1):
        titulo = r.get('titulo')
        slug = sanitize_slug(titulo)
        out_filename = f"{slug}.png"
        out_path = os.path.join(OUTPUT_DIR, out_filename)
        rel_path = f"assets/receitas_flow/{out_filename}"

        print(f"\n[{i}/{len(lote)}] Gerando Flow para: '{titulo}'...")
        prompt = construir_prompt_gastronomico(titulo, r.get('categoria', ''), r.get('descricao', ''))

        try:
            path_salvo = bridge.generate_image(prompt=prompt, output_path=out_path, aspect_ratio="9:16")
            if path_salvo and os.path.exists(path_salvo) and os.path.getsize(path_salvo) > 10000:
                print(f" -> Sucesso: {out_filename} ({os.path.getsize(path_salvo)//1024} KB)")
                r['imagem_capa'] = rel_path
                geradas_com_sucesso += 1
            else:
                print(f" -> Falha ao salvar {out_filename}")
        except Exception as e:
            print(f" -> Erro na geração: {e}")

        time.sleep(2)

    # Atualiza receitas.json e js/receitas_data.js
    if geradas_com_sucesso > 0:
        with open(RECEITAS_PATH, 'w', encoding='utf-8') as f:
            json.dump(recs, f, indent=2, ensure_ascii=False)

        with open(RECEITAS_DATA_JS, 'w', encoding='utf-8') as f:
            f.write('// Banco de 156 receitas e hábitos do Saciara Fitness\n')
            f.write('window.BANCO_RECEITAS_156 = ')
            json.dump(recs, f, indent=2, ensure_ascii=False)
            f.write(';\n')

        print(f"\n[OK] {geradas_com_sucesso} receitas atualizadas e integradas ao site.")

if __name__ == '__main__':
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    executar_geracao_lote(limite=limite)
