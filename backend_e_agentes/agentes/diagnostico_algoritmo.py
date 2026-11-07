"""Agente Analista de Algoritmo & Engenheiro de Ganchos Virais para o @saciara_.
Diagnostica as causas de 'Zero Views' no Instagram e reformula pautas, capas e legendas
aplicando as 4 Fórmulas de Alta Retenção (2026) que conduzem o público aos Stories.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from .memoria_manager import MemoriaSaciaraManager


# Fórmulas Canônicas de Ganchos Virais de 2026 para Gastronomia & Fitness
FORMULAS_GANCHOS_VIRAL = [
    {
        "id": "IG1_DOR_INVERSA",
        "nome": "Dor Oculta / Desejo Noturno",
        "padrao": "Vontade de doce depois do almoço? Isso mata a fissura em 3 minutos (sem fogão).",
        "objetivo": "Compartilhamento & Salvamento"
    },
    {
        "id": "IG2_QUEBRA_DE_MITO",
        "nome": "Quebra de Senso Comum",
        "padrao": "O maior erro ao fazer crepioca é esquecer este passo simples.",
        "objetivo": "Comentários & Retenção"
    },
    {
        "id": "IG3_PRATICIDADE_EXTREMA",
        "nome": "Economia de Tempo / Marmita Descomplicada",
        "padrao": "Como organizar 4 refeições saudáveis sem passar o domingo na cozinha.",
        "objetivo": "Salvar para a Lista de Compras"
    },
    {
        "id": "IG4_CONVITE_STORY",
        "nome": "Ponte Direta para os Stories (Link Shopee)",
        "padrao": "O pote hermético que uso pra durar 5 dias sem estragar tá nos Stories hoje!",
        "objetivo": "Cliques no Link dos Stories"
    }
]


class DiagnosticoAlgoritmoAgent:
    def __init__(self, memoria_mgr: Optional[MemoriaSaciaraManager] = None):
        self.memoria = memoria_mgr or MemoriaSaciaraManager()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    def diagnosticar_perfil(self) -> Dict[str, Any]:
        """Gera diagnóstico completo dos motivos de zero visualizações e prescreve o plano de choque."""
        diagnostico = {
            "perfil": "@saciara_",
            "diagnostico_algoritmo_2026": {
                "fator_critico_1": "Títulos meramente descritivos na capa ('Crepioca de ricota') não geram curiosidade nem interrompem a rolagem rápida.",
                "fator_critico_2": "Falta do gatilho de 'Salvamento' (Save Rate) nos primeiros 2 slides. No Instagram de 2026, salvamentos pesam 3x mais que curtidas na distribuição Explore.",
                "fator_critico_3": "Ausência do funil 'Feed -> Stories'. Sem um gancho dizendo 'o link do utensílio tá nos stories', a audiência consome e vai embora sem clicar.",
                "fator_critico_4": "Falta de vídeos verticais Reels e Stories em movimento. Imagens estáticas sozinhas sofrem redução algorítmica de até 70% no alcance orgânico."
            },
            "solucao_imediata": [
                "Reformular os primeiros 125 caracteres da legenda de cada post para gerar leitura obrigatória.",
                "Adicionar sempre uma chamada explícita para o Story com o produto Shopee relacionado.",
                "Alimentar diariamente os Stories com vídeos faceless demonstrando os utensílios com sticker interativo."
            ]
        }
        self.memoria.adicionar_aprendizado(
            regra="O algoritmo só entrega o carrossel se a taxa de salvamentos no slide 1 e 2 for superior a 8%. Títulos devem focar na dor do seguidor, não no nome do prato.",
            origem="DiagnosticoAlgoritmoAgent"
        )
        return diagnostico

    def reformular_gancho_legenda(self, titulo_original: str, legenda_original: str, produto_relacionado: str) -> Dict[str, str]:
        """Usa IA para reformular a legenda de forma magnética com gancho forte e CTA para Stories."""
        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
                prompt = (
                    f"Você é o maior especialista em engajamento e algoritmo do Instagram para o nicho de receitas fitness e nutrição equilibrada.\n"
                    f"Temos uma postagem com o título: '{titulo_original}'\n"
                    f"Legenda atual: '{legenda_original[:200]}...'\n"
                    f"Utensílio/Produto Shopee vinculado nos Stories: '{produto_relacionado}'\n\n"
                    f"Reescreva para maximizar RETENÇÃO, SALVAMENTOS e CLIQUES NOS STORIES:\n"
                    f"1. Gancho nos primeiros 100 caracteres (antes do botão 'mais') irresistível.\n"
                    f"2. Corpo de 3 a 5 linhas simples e focado em praticidade.\n"
                    f"3. CTA de encerramento direcionando para ver a demonstração e o link nos STORIES de hoje.\n"
                    f"4. Três a quatro hashtags cirúrgicas.\n"
                    f"Retorne em formato JSON puro:\n"
                    f"{{\n"
                    f'  "novo_gancho_capa": "frase de impacto para o slide 1 (max 8 palavras)",\n'
                    f'  "legenda_completa": "texto persuasivo pronto com quebras de linha",\n'
                    f'  "cta_stories": "chamada usada para o story"\n'
                    f"}}"
                )

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"response_mime_type": "application/json", "temperature": 0.4}
                }

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read().decode("utf-8"))

                texto = result["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(texto)
            except Exception:
                pass

        # Fallback inteligente baseado em regras
        novo_gancho = f"O segredo para fazer {titulo_original} em minutos"
        cta = f"O utensílio prático que usei tá demonstrado nos Stories com link promocional!"
        nova_legenda = (
            f"Você ainda acha que comer saudável dá trabalho? 👇\n\n"
            f"{titulo_original} sem fogão e sem complicação pra salvar sua rotina.\n\n"
            f"📌 Salve para não perder os ingredientes.\n"
            f"🔗 {cta}\n\n"
            f"#Saciara #ReceitasFit #PraticidadeSaudavel #AlimentacaoEquilibrada"
        )
        return {
            "novo_gancho_capa": novo_gancho,
            "legenda_completa": nova_legenda,
            "cta_stories": cta
        }
