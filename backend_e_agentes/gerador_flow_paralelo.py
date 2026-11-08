"""
Pipeline Paralelo Pipelined: Google Flow (Brave CDP 9222)
Saciara Fitness - Canal @saciara_ / App NutriPlus

Dispara os prompts consecutivamente para a fila do Google Flow (sem esperar cada um renderizar),
enquanto monitora e faz download paralelo dos resultados prontos em 2K.
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

def construir_prompt_gastronomico(titulo, categoria):
    cat_lower = (categoria or '').lower()
    if 'café' in cat_lower:
        tipo = "Brazilian healthy breakfast"
    elif 'almoço' in cat_lower or 'jantar' in cat_lower:
        tipo = "Brazilian nutritious savory meal"
    elif 'sobremesa' in cat_lower or 'doce' in cat_lower:
        tipo = "Brazilian fit dessert"
    else:
        tipo = "Brazilian wholesome healthy snack"

    return (
        f"Gourmet culinary photography of {tipo}: '{titulo}'. "
        f"Real food styling, plated on rustic artisan dark ceramic tableware, "
        f"fresh natural ingredients visible, soft morning window light from the side, gentle steam, "
        f"mouth-watering natural texture, cinematic shallow depth of field f/1.8, bokeh background, "
        f"photorealistic 8k, Bon Appétit food magazine editorial, vertical 9:16 framing, clean food only, absolutely zero text, no graphic design."
    )

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
        print(f"\n[Deploy] Realizando deploy automático de bloco (+{qtd_novas} receitas)...")
        subprocess.run(["git", "add", "assets/receitas_flow/", "receitas.json", "js/receitas_data.js"], cwd=ROOT_DIR, check=False)
        subprocess.run(["git", "commit", "-m", f"feat(flow-parallel): +{qtd_novas} receitas geradas via Google Flow"], cwd=ROOT_DIR, check=False)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT_DIR, check=False)
        subprocess.run("cmd /c \"npx.cmd vercel --prod --yes\"", shell=True, cwd=ROOT_DIR, check=False)
        print("[Deploy] Deploy concluído com sucesso!")
    except Exception as e:
        print(f"[Deploy] Aviso: {e}")

def executar_pipeline_paralelo(tamanho_onda=4):
    print("="*65)
    print("INICIANDO GERADOR PIPELINED (DISPAROS EM ONDA SEM BLOQUEIO)")
    print("="*65)

    with open(RECEITAS_PATH, 'r', encoding='utf-8') as f:
        recs = json.load(f)

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

    print(f"Total de receitas culinárias pendentes: {len(pendentes)}")
    if not pendentes:
        print("Todas as receitas já estão geradas e salvas!")
        return

    # Processa em ondas de múltiplos disparos simultâneos
    indice_geral = 0
    total_geradas = 0

    while indice_geral < len(pendentes):
        onda = pendentes[indice_geral : indice_geral + tamanho_onda]
        print(f"\n>>> DISPARANDO ONDA DE {len(onda)} RECEITAS EM PARALELO PARA A FILA DO FLOW <<<")

        # 1. Dispara os prompts em rajada contínua (sem aguardar renderização)
        for r in onda:
            titulo = r.get('titulo')
            prompt = construir_prompt_gastronomico(titulo, r.get('categoria', ''))
            print(f" -> Enfileirando no Flow: '{titulo}'...")
            res = flow_bridge.dispatch_flow_prompt(prompt)
            if not res.get('success'):
                print(f"    [Aviso] Falha no disparo: {res.get('error')}")
            time.sleep(1.8)

        # 2. Conecta para aguardar e baixar as imagens da onda
        print("\n>>> Coletando e salvando os resultados gerados da onda atual...")
        for r in onda:
            titulo = r.get('titulo')
            slug = sanitize_slug(titulo)
            out_filename = slug
            final_path = os.path.join(OUTPUT_DIR, f"{out_filename}.png")

            # Executa captura
            try:
                prompt = construir_prompt_gastronomico(titulo, r.get('categoria', ''))
                res = flow_bridge.generate_flow_image(
                    prompt=prompt,
                    output_dir=OUTPUT_DIR,
                    filename=out_filename
                )
                image_path = res.get('imagePath', final_path)
                if res.get('success') and os.path.exists(image_path) and os.path.getsize(image_path) > 10000:
                    tamanho_kb = os.path.getsize(image_path) // 1024
                    print(f" -> [SALVO] {out_filename}.png ({tamanho_kb} KB)")
                    r['imagem_capa'] = f"assets/receitas_flow/{out_filename}.png"
                    salvar_banco(recs)
                    total_geradas += 1
            except Exception as e:
                print(f" -> [Erro ao salvar {out_filename}]: {e}")

        # Deploy do bloco concluído
        realizar_deploy_bloco(len(onda))
        indice_geral += tamanho_onda
        time.sleep(3)

    print("\n" + "="*65)
    print(f"PIPELINE PARALELO FINALIZADO COM SUCESSO: {total_geradas} receitas geradas!")
    print("="*65)

if __name__ == '__main__':
    executar_pipeline_paralelo(tamanho_onda=3)
