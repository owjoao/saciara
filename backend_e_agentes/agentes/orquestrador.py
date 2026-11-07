"""Orquestrador Central e CLI do Líder Soberano - Saciara Fitness (@saciara_).
Meta Soberana: 'QUERO MAIS CLIQUES NO MEU LINK'.

Uso:
    python agentes/orquestrador.py --status                 # Painel geral de telemetria e agentes
    python agentes/orquestrador.py --diagnostico            # Análise algorítmica de 0 views e plano de choque
    python agentes/orquestrador.py --otimizar-pauta         # Reformula ganchos da fila com fórmulas 2026
    python agentes/orquestrador.py --story "crepioca"       # Executa o pipeline de Story (Shopee -> Vídeo Faceless -> Story)
    python agentes/orquestrador.py --story-simulado "balança" # Simula a esteira completa sem postar no IG
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Carrega .env
env_file = ROOT_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

from agentes.hierarquia import LeaderSaciara
from agentes.memoria_manager import MemoriaSaciaraManager


def _agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def cmd_status():
    lider = LeaderSaciara()
    dados = lider.executar_diagnostico_geral()
    memoria = lider.memoria.carregar()

    print("\n" + "=" * 65)
    print(" 🏛️ SACIARA FITNESS - HIERARQUIA DE AGENTES AUTÔNOMOS")
    print("=" * 65)
    print(f" Data e Hora: {_agora()}")
    print(f" Meta Soberana: 🎯 '{dados['meta_soberana']}'")
    print(f" Canal:         {memoria.get('canal', '@saciara_')}")
    print(f" Nicho:         {memoria.get('nicho')}")
    print("-" * 65)
    print(" 👥 CENSO OFICIAL DE AGENTES RESIDENTES:")
    for ag in dados["censo"]:
        nivel_badge = "🥇 [Nível 1]" if ag["nivel"] == 1 else ("🥈 [Nível 2]" if ag["nivel"] == 2 else "🥉 [Nível 3]")
        print(f"   • {nivel_badge} {ag['nome']} ({ag['id']})")
        print(f"     Papel: {ag['papel']}")
        print(f"     Meta:  {ag['meta']}\n")

    print("-" * 65)
    print(" 📊 TELEMETRIA DO COFRE DE MEMÓRIA FECHADO:")
    globais = dados["metricas_globais"]
    print(f"   • Stories com Afiliados Produzidos: {globais.get('total_stories_afiliados', 0)}")
    print(f"   • Produtos Shopee Catalogados:      {globais.get('total_produtos_garimpados', 0)}")
    print(f"   • Ciclos de Automelhoria:           {globais.get('ciclos_automelhoria', 0)}")
    print(f"   • Regras Aprendidas no Cofre:       {dados['regras_aprendidas']}")
    print("=" * 65 + "\n")


def cmd_diagnostico():
    lider = LeaderSaciara()
    diag = lider.agente_algoritmo.diagnosticar_perfil()
    print("\n" + "=" * 65)
    print(" 🔬 DIAGNÓSTICO DE 'ZERO VIEWS' & ENGENHARIA DO ALGORITMO")
    print("=" * 65)
    print(" ⚠️ CAUSAS RAIZ IDENTIFICADAS:")
    for k, v in diag["diagnostico_algoritmo_2026"].items():
        print(f"   • {v}")

    print("\n 🚀 PLANO DE CHOQUE PARA CLIQUES NO LINK:")
    for acao in diag["solucao_imediata"]:
        print(f"   [✓] {acao}")
    print("=" * 65 + "\n")


def cmd_otimizar_pauta():
    print(f"\n[{_agora()}] Otimizando próximas pautas da fila para retenção...")
    fila_path = ROOT_DIR / "fila-postagem.json"
    if not fila_path.exists():
        print("  ❌ Fila não encontrada.")
        return

    fila = json.loads(fila_path.read_text(encoding="utf-8"))
    pendentes = [f for f in fila if f.get("status") == "pendente"]

    if not pendentes:
        print("  ⚠️ Nenhuma pauta pendente para otimizar.")
        return

    proximo = pendentes[0]
    pasta_pauta = ROOT_DIR / "conteudo-saciara" / proximo["pasta"]
    desc_file = pasta_pauta / "descricao.txt"

    texto_antigo = desc_file.read_text(encoding="utf-8") if desc_file.exists() else ""
    lider = LeaderSaciara()

    # Identifica produto para a ponte dos stories
    sugestoes = lider.agente_shopee.sugerir_por_tema(proximo["pasta"])
    nome_prod = sugestoes[0].name if sugestoes else "balança digital de cozinha"

    resultado = lider.agente_algoritmo.reformular_gancho_legenda(
        titulo_original=proximo["pasta"],
        legenda_original=texto_antigo,
        produto_relacionado=nome_prod
    )

    print("\n" + "=" * 65)
    print(f" 🎯 PAUTA OTIMIZADA: {proximo['pasta']}")
    print("=" * 65)
    print(f" 🪝 NOVO GANCHO DA CAPA: {resultado['novo_gancho_capa']}")
    print(f" 🔗 PONTE PARA STORIES:  {resultado['cta_stories']}")
    print("-" * 65)
    print(" 📝 NOVA LEGENDA MAGNÉTICA:")
    print(resultado["legenda_completa"])
    print("=" * 65 + "\n")


def cmd_story(tema_ou_url: str, simular: bool = False):
    lider = LeaderSaciara()
    lider.gerar_story_afiliado_para_receita(tema_receita=tema_ou_url, simular=simular)


def cmd_listar_ugc():
    from agentes.roteiros_ugc import VARIASCOES_UGC_SACIARA
    print("\n" + "=" * 75)
    print(" 🎬 CATÁLOGO DE 10 VARIAÇÕES UGC EM VÍDEO (ESTILO AMIGO RECOMENDANDO)")
    print(" 🎯 ORDEM MÁXIMA: 'QUERO MAIS CLIQUES NO MEU LINK'")
    print("=" * 75)
    for v in VARIASCOES_UGC_SACIARA:
        print(f" [#{v.id}] {v.produto_foco}")
        print(f"      Ângulo:   {v.angulo_psicologico}")
        print(f"      Topo:     '{v.frase_topo_story}'")
        print(f"      Sticker:  [ 🔗 {v.texto_sticker} ] (Thumb Zone Y=82.7%)")
        print(f"      Busca:    {v.termo_busca_video}")
        print(f"      Conversão: {v.motivo_conversao}\n")
    print("=" * 75 + "\n")


def cmd_executar_ugc(variacao_id: int, simular: bool = False):
    from agentes.pipeline_ugc_video import PipelineUGCVideoStories
    pipe = PipelineUGCVideoStories()
    return pipe.processar_variacao_ugc(variacao_id=variacao_id, simular=simular)


def main():
    parser = argparse.ArgumentParser(description="Orquestrador Soberano - Saciara Fitness")
    parser.add_argument("--status", action="store_true", help="Status da hierarquia e telemetria da memória")
    parser.add_argument("--diagnostico", action="store_true", help="Diagnóstico do algoritmo para zero views")
    parser.add_argument("--otimizar-pauta", action="store_true", help="Otimiza a próxima pauta da fila com ganchos virais")
    parser.add_argument("--story", type=str, help="Executa o pipeline de Story para um tema ou link")
    parser.add_argument("--story-simulado", type=str, help="Simula o pipeline de Story sem postar no Instagram")
    parser.add_argument("--listar-ugc", action="store_true", help="Lista as 10 variações de vídeos UGC amigos")
    parser.add_argument("--ugc-variacao", type=int, help="Dispara uma variação UGC ao vivo (1 a 10)")
    parser.add_argument("--ugc-simular", type=int, help="Simula uma variação UGC sem postar (1 a 10)")
    args = parser.parse_args()

    if args.status:
        cmd_status()
    elif args.diagnostico:
        cmd_diagnostico()
    elif args.otimizar_pauta:
        cmd_otimizar_pauta()
    elif args.story:
        cmd_story(args.story, simular=False)
    elif args.story_simulado:
        cmd_story(args.story_simulado, simular=True)
    elif args.listar_ugc:
        cmd_listar_ugc()
    elif args.ugc_variacao:
        cmd_executar_ugc(args.ugc_variacao, simular=False)
    elif args.ugc_simular:
        cmd_executar_ugc(args.ugc_simular, simular=True)
    else:
        cmd_status()


if __name__ == "__main__":
    main()
