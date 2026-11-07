"""Hierarquia Oficial de Agentes Autônomos do Saciara Fitness (@saciara_).
Meta Soberana: 'QUERO MAIS CLIQUES NO MEU LINK'.

Estrutura:
  Nível 1 (Líder Soberano):
    - LeaderSaciara: Orquestrador da Meta 'Mais Cliques no Link'
  Nível 2 (Especialistas de Algoritmo & Conversão):
    - AgenteDiagnosticoAlgoritmo: Analista do Algoritmo IG 2026 e Engenheiro de Retenção
    - AgenteHunterShopee: Curadoria de Achados com Alta Comissão e Impulso
    - AgenteHunterFaceless: Mineração e Auditoria IA de Vídeos Sem Rosto (POV/Mãos)
    - AgenteStoriesPublisher: Publicador Canônico de Stories com Sticker na Thumb Zone
  Nível 3 (Governança & Aprendizado):
    - AgenteAutoMelhoria: Loop Fechado de Aprendizado e Memória Contínua
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .memoria_manager import MemoriaSaciaraManager
from .diagnostico_algoritmo import DiagnosticoAlgoritmoAgent
from .hunter_faceless import HunterFacelessAgent
from .pipeline_stories import PipelineStoriesAfiliados
from afiliados_shopee import AgenteAfiliadosShopeeFitness


@dataclass
class AgenteInfo:
    id: str
    nome: str
    papel: str
    nivel: int
    meta: str


class LeaderSaciara:
    """Líder Soberano do Canal Saciara Fitness.
    Ordem Máxima: 'QUERO MAIS CLIQUES NO MEU LINK'
    """
    def __init__(self):
        self.memoria = MemoriaSaciaraManager()
        self.agente_algoritmo = DiagnosticoAlgoritmoAgent(self.memoria)
        self.agente_shopee = AgenteAfiliadosShopeeFitness()
        self.agente_faceless = HunterFacelessAgent()
        self.pipeline_stories = PipelineStoriesAfiliados()

    def censo_agentes(self) -> List[AgenteInfo]:
        return [
            AgenteInfo(
                id="leader_saciara",
                nome="Líder Soberano Saciara",
                papel="Maestro Central da Operação e Guardião da Meta de Cliques",
                nivel=1,
                meta="Maximizar visualizações no Feed/Reels e convertê-las em cliques nos Stories"
            ),
            AgenteInfo(
                id="agente_algoritmo",
                nome="Analista de Algoritmo & Retenção 2026",
                papel="Auditoria de Zero Views e Engenharia de Ganchos Virais",
                nivel=2,
                meta="Aumentar taxa de salvamento (>8%) e retenção nos primeiros 3s"
            ),
            AgenteInfo(
                id="agente_hunter_shopee",
                nome="Curador de Achados Shopee Fitness",
                papel="Seleção de Utensílios de Alta Comissão e Geração de Links Rastreáveis",
                nivel=2,
                meta="Identificar produtos com comissões de até 70% compatíveis com a receita"
            ),
            AgenteInfo(
                id="agente_hunter_faceless",
                nome="Minerador & Auditor de Vídeos Faceless",
                papel="Garimpo de Vídeos Demonstrativos POV/Mãos e Bloqueio de Rostos",
                nivel=2,
                meta="Garantir mídias dinâmicas sem cabeça falante, apenas demonstração prática"
            ),
            AgenteInfo(
                id="agente_stories_publisher",
                nome="Operador de Stories & Stickers Interativos",
                papel="Composição Visual 9:16 e Posicionamento de Stickers na Thumb Zone (Y=82.7%)",
                nivel=2,
                meta="Garantir o menor atrito possível para o toque e clique do seguidor"
            ),
            AgenteInfo(
                id="agente_automelhoria",
                nome="Guardião do Loop de Memória Fechada",
                papel="Telemetria e Registro de Aprendizado Isolado na Pasta",
                nivel=3,
                meta="Impedir contaminação cruzada de dados e refinar as próximas postagens"
            ),
        ]

    def executar_diagnostico_geral(self) -> Dict[str, Any]:
        """Audita a esteira atual, identifica gargalos e prescreve o plano de choque."""
        censo = [a.__dict__ for a in self.censo_agentes()]
        diag_algo = self.agente_algoritmo.diagnosticar_perfil()
        memoria_dados = self.memoria.carregar()

        return {
            "meta_soberana": "QUERO MAIS CLIQUES NO MEU LINK",
            "agentes_ativos": len(censo),
            "censo": censo,
            "diagnostico_algoritmo": diag_algo,
            "metricas_globais": memoria_dados.get("metricas_globais", {}),
            "regras_aprendidas": len(memoria_dados.get("aprendizados_continuos", []))
        }

    def gerar_story_afiliado_para_receita(self, tema_receita: str, simular: bool = False) -> Dict[str, Any]:
        """Executa a ponte: Receita -> Utensílio Shopee -> Link -> Vídeo Faceless -> Story."""
        print(f"\n[LÍDER] Identificando melhor oportunidade de produto para o tema: '{tema_receita}'...")
        sugestoes = self.agente_shopee.sugerir_por_tema(tema_receita)
        if not sugestoes:
            # Fallback para busca geral de utensílios
            sugestoes = self.agente_shopee.buscar_achados("balanca digital cozinha", limit=1)

        produto_escolhido = sugestoes[0]
        print(f"[LÍDER] Produto Selecionado: {produto_escolhido.name[:45]} (Comissão: R$ {produto_escolhido.commission:.2f})")

        resultado = self.pipeline_stories.executar(
            termo_ou_url=produto_escolhido.offer_link or produto_escolhido.name,
            texto_sticker="ONDE COMPREI",
            estilo_sticker="sunset",
            publicar_agora=not simular
        )

        self.memoria.adicionar_aprendizado(
            regra=f"Story gerado para o tema '{tema_receita}' vinculado a '{produto_escolhido.name[:30]}'.",
            origem="LeaderSaciara"
        )
        return resultado
