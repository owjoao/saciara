"""Motor de Loop de Melhoria Contínua do Líder do Saciara.
Localização: F:\\Nova pasta\\site\\saciara\\memoria_lider\\loop_melhoria_lider.py

Executa o ciclo OODA/PDCA:
1. Auditar (Sense): Executa checagens técnicas e avalia o projeto Saciara
2. Diagnosticar: Identifica gargalos em relação às metas do projeto
3. Agir: Aciona especialistas operacionais externos (em F:\\Nova pasta\\site\\agentes)
4. Aprender & Auto-Calibrar: Atualiza a memória individual e exporta lições para a Memória Coletiva
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DIR_LIDER = Path(__file__).resolve().parent
DIR_SACIARA = DIR_LIDER.parent
DIR_RAIZ_SITES = DIR_SACIARA.parent

# Inclusão dos paths para consumo dos agentes compartilhados e memoria coletiva
for p in [str(DIR_RAIZ_SITES), str(DIR_RAIZ_SITES / "agentes"), str(DIR_RAIZ_SITES / "memoria_coletiva")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from memoria_coletiva.memoria_coletiva_manager import memoria_coletiva
from agente_coletivo_bridge import equipe_compartilhada


class LoopMelhoriaLiderSaciara:
    """Motor do Loop de Auto-Melhoria Contínua do Líder."""

    def __init__(self, caminho_memoria_individual: Optional[Path] = None):
        self.caminho_memoria = caminho_memoria_individual or (DIR_LIDER / "memoria_individual_lider.json")
        self.equipe_externa = equipe_compartilhada
        self.memoria_global = memoria_coletiva

    def carregar_memoria_individual(self) -> Dict[str, Any]:
        """Lê os dados da memória individual do Líder."""
        if not self.caminho_memoria.exists():
            return {}
        with open(self.caminho_memoria, "r", encoding="utf-8") as f:
            return json.load(f)

    def salvar_memoria_individual(self, dados: Dict[str, Any]) -> None:
        """Salva a memória individual do Líder com segurança atômica."""
        temp = self.caminho_memoria.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        temp.replace(self.caminho_memoria)

    def executar_ciclo_melhoria(self) -> Dict[str, Any]:
        """Roda um ciclo completo de auditoria, diagnóstico e auto-calibração."""
        memoria = self.carregar_memoria_individual()
        params = memoria.get("parametros_auto_calibracao", {})
        ciclo_num = params.get("ciclos_executados", 0) + 1

        # Etapa 1: Sense / Auditar através da equipe compartilhada da raiz
        relatorio_equipe = self.equipe_externa.executar_auditoria_completa_site(DIR_SACIARA)

        # Etapa 2: Diagnosticar conformidade específica com o Saciara
        erros_gatekeeper = len(relatorio_equipe["gatekeeper"].get("erros_bloqueantes", []))
        alertas_gatekeeper = len(relatorio_equipe["gatekeeper"].get("alertas_nao_bloqueantes", []))
        pontuacao_seo = relatorio_equipe["seo_conversao"].get("pontuacao_seo_cro", 50)
        mobile_aprovado = relatorio_equipe["frontend_ui"].get("aprovado", False)

        # Cálculo da pontuação composta do ciclo (0 a 100)
        score_base = 100
        score_base -= (erros_gatekeeper * 25)
        score_base -= (alertas_gatekeeper * 5)
        if not mobile_aprovado:
            score_base -= 15
        score_seo_ajustado = (pontuacao_seo / 100) * 20
        score_final = max(0, min(100, score_base + score_seo_ajustado - 20))

        # Etapa 3: Registrar aprendizados e ajustar parâmetros
        status_aprovacao = score_final >= params.get("limiar_aprovacao_qualidade", 85)
        
        novo_registro_ciclo = {
            "ciclo": ciclo_num,
            "data": datetime.now().isoformat(),
            "score_atingido": round(score_final, 1),
            "aprovado": status_aprovacao,
            "metricas_auditadas": {
                "erros_bloqueantes": erros_gatekeeper,
                "alertas": alertas_gatekeeper,
                "score_seo": pontuacao_seo,
                "mobile_ui_aprovado": mobile_aprovado
            },
            "acoes_recomendadas": []
        }

        if erros_gatekeeper > 0:
            novo_registro_ciclo["acoes_recomendadas"].append("Corrigir erros bloqueantes identificados pelo Gatekeeper.")
        if not mobile_aprovado:
            novo_registro_ciclo["acoes_recomendadas"].append("Acionar SiteCraftsman para sanar gargalos de responsividade móvel.")
        if pontuacao_seo < 75:
            novo_registro_ciclo["acoes_recomendadas"].append("Acionar SiteSeoConversion para enriquecer metatags e OpenGraph.")

        # Atualizar parâmetros e histórico na memória individual
        params["ciclos_executados"] = ciclo_num
        historico = memoria.setdefault("historico_ciclos_melhoria", [])
        historico.append(novo_registro_ciclo)
        memoria["parametros_auto_calibracao"] = params
        self.salvar_memoria_individual(memoria)

        # Etapa 4: Sincronizar com a Memória Coletiva Global (compartilhamento externo)
        self.memoria_global.registrar_ou_atualizar_site(
            slug_site="saciara",
            info_site={
                "ultimo_score_qualidade": round(score_final, 1),
                "ciclo_melhoria": ciclo_num,
                "data_auditoria": datetime.now().isoformat(),
                "status_producao": "aprovado" if status_aprovacao else "revisao_necessaria"
            }
        )

        return {
            "status": "concluido",
            "ciclo": ciclo_num,
            "score_qualidade": round(score_final, 1),
            "aprovado": status_aprovacao,
            "relatorio_equipe": relatorio_equipe,
            "acoes_recomendadas": novo_registro_ciclo["acoes_recomendadas"]
        }
