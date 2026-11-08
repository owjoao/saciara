"""
Robô Mestre Autônomo de Geração Culinária 8K via Google Flow (Brave CDP 9222)
Gera individualmente a fotografia gastronômica para TODAS as 130 receitas pendentes.
Atualiza receitas.json e js/receitas_data.js progressivamente a cada item gerado.
Faz commit e deploy a cada bloco de 5 receitas para que o progresso seja contínuo e persistido.
"""

import os
import sys
import json
import time
import subprocess

SHARED_TOOLS_DIR = r"f:\Nova pasta\automação redes sociais\shared_tools"
if SHARED_TOOLS_DIR not in sys.path:
    sys.path.append(SHARED_TOOLS_DIR)

import flow_bridge

OUTPUT_DIR = r"f:\Nova pasta\site\saciara\assets\receitas_flow"
RECEITAS_PATH = r"f:\Nova pasta\site\saciara\receitas.json"
RECEITAS_DATA_JS = r"f:\Nova pasta\site\saciara\js\receitas_data.js"
ROOT_DIR = r"f:\Nova pasta\site\saciara"

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
    # Traduz categorias para direcionamento visual gastronômico perfeito
    cat_lower = (categoria or '').lower()
    if 'café' in cat_lower:
        tipo = "Brazilian healthy breakfast"
    elif 'almoço' in cat_lower or 'jantar' in cat_lower:
        tipo = "Brazilian nutritious savory meal"
    elif 'sobremesa' in cat_lower or 'doce' in cat_lower:
        tipo = "Brazilian guilt-free fit dessert"
    else:
        tipo = "Brazilian wholesome healthy snack"

    prompt = (
        f"Gourmet culinary photography of {tipo}: '{titulo}'. "
        f"Real food styling, plated on rustic artisan dark ceramic tableware, "
        f"fresh natural ingredients visible, soft morning window light from the side, gentle steam, "
        f"mouth-watering natural texture, cinematic shallow depth of field f/1.8, bokeh background, "
        f"photorealistic 8k, Bon Appétit food magazine editorial, vertical 9:16 framing, clean food only, absolutely zero text, no graphic design."
    )
    return prompt

def salvar_banco(recs):
    with open(RECEITAS_PATH, 'w', encoding='utf-8') as f:
        json.dump(recs, f, indent=2, ensure_ascii=False)

    with open(RECEITAS_DATA_JS, 'w', encoding='utf-8') as f:
        f.write('// Banco de 156 receitas e hábitos do Saciara Fitness\n')
        f.write('window.BANCO_RECEITAS_156 = ')
        json.dump(recs, f, indent=2, ensure_ascii=False)
        f.write(';\n')

def realizar_deploy_bloco(qtd_novas):
    try:
        print(f"\n[Git & Vercel] Realizando deploy automático de bloco (+{qtd_novas} receitas)...")
        subprocess.run(["git", "add", "assets/receitas_flow/", "receitas.json", "js/receitas_data.js"], cwd=ROOT_DIR, check=False)
        subprocess.run(["git", "commit", "-m", f"feat(flow-scraping): lote de {qtd_novas} receitas individuais 8k via Flow"], cwd=ROOT_DIR, check=False)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT_DIR, check=False)
        subprocess.run("cmd /c \"npx.cmd vercel --prod --yes\"", shell=True, cwd=ROOT_DIR, check=False)
        print("[Git & Vercel] Deploy de bloco concluído com sucesso!")
    except Exception as e:
        print(f"[Git & Vercel] Aviso no deploy de bloco: {e}")

def executar_geracao_todas():
    print("="*65)
    print("INICIANDO GERAÇÃO INTEGRAL DE TODAS AS RECEITAS NO GOOGLE FLOW")
    print("="*65)

    with open(RECEITAS_PATH, 'r', encoding='utf-8') as f:
        recs = json.load(f)

    # Identificar todas as receitas culinárias que ainda não têm imagem individual do Flow
    pendentes = []
    for r in recs:
        tags = [t.lower() for t in r.get('tags', [])]
        if 'mindfulness' in tags or 'estilo de vida' in tags:
            continue
        capa = r.get('imagem_capa', '')
        if 'assets/receitas_flow' in capa:
            rel = capa.lstrip('/')
            full = os.path.join(ROOT_DIR, rel)
            if os.path.exists(full) and os.path.getsize(full) > 10000:
                continue
        pendentes.append(r)

    total_pendentes = len(pendentes)
    print(f"Total de receitas culinárias pendentes de geração Flow: {total_pendentes}")

    if total_pendentes == 0:
        print("Todas as receitas já possuem imagens individuais no Google Flow!")
        return

    sucessos_totais = 0
    bloco_atual = 0

    for idx, r in enumerate(pendentes, 1):
        titulo = r.get('titulo')
        slug = sanitize_slug(titulo)
        out_filename = slug
        expected_path = os.path.join(OUTPUT_DIR, f"{out_filename}.png")

        print(f"\n[{idx}/{total_pendentes}] Gerando imagem no Flow para: '{titulo}'...")
        prompt = construir_prompt_gastronomico(titulo, r.get('categoria', ''), r.get('descricao', ''))

        tentativas = 0
        conseguiu = False
        while tentativas < 2 and not conseguiu:
            tentativas += 1
            try:
                res = flow_bridge.generate_flow_image(
                    prompt=prompt,
                    output_dir=OUTPUT_DIR,
                    filename=out_filename
                )
                image_path = res.get('imagePath', expected_path)
                if res.get('success') and os.path.exists(image_path) and os.path.getsize(image_path) > 10000:
                    tamanho_kb = os.path.getsize(image_path) // 1024
                    print(f" -> [SUCESSO] {out_filename}.png ({tamanho_kb} KB)")
                    r['imagem_capa'] = f"assets/receitas_flow/{out_filename}.png"
                    salvar_banco(recs)
                    sucessos_totais += 1
                    bloco_atual += 1
                    conseguiu = True
                else:
                    print(f" -> [Aviso tentativa {tentativas}] Falha ao gerar: {res.get('error')}")
                    time.sleep(3)
            except Exception as e:
                print(f" -> [Erro tentativa {tentativas}]: {e}")
                time.sleep(3)

        # A cada 5 receitas concluídas, faz deploy automático para manter a produção atualizada
        if bloco_atual >= 5:
            realizar_deploy_bloco(bloco_atual)
            bloco_atual = 0

        time.sleep(2)

    # Deploy dos itens restantes
    if bloco_atual > 0:
        realizar_deploy_bloco(bloco_atual)

    print("\n" + "="*65)
    print(f"PIPELINE INTEGRAL CONCLUÍDO! Total de receitas geradas no Flow: {sucessos_totais}/{total_pendentes}")
    print("="*65)

if __name__ == '__main__':
    executar_geracao_todas()
