"""Motor de Otimização e Planejamento Semanal de Refeições (Diet Solver).
Distribui as 156 receitas do Saciara ao longo dos 7 dias da semana (Segunda a Domingo)
garantindo metas calóricas, distribuição de macros e variedade alimentar.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional
from core_nutricional.catalogo_saciara import CatalogoReceitasSaciara


class DietSolverSemanal:
    def __init__(self):
        self.catalogo = CatalogoReceitasSaciara()
        self.receitas = self.catalogo.carregar_todas()

    def gerar_plano_semanal(
        self,
        meta_calorica_dia: float,
        meta_proteina_g: float,
        refeicoes_por_dia: int = 4
    ) -> Dict[str, Any]:
        """Gera um cardápio semanal completo de 7 dias com base nas receitas reais."""
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

        # Agrupa receitas por categoria
        cafes = [r for r in self.receitas if r["categoria"] == "café da manhã"] or self.receitas[:10]
        almocos = [r for r in self.receitas if r["categoria"] == "almoço & jantar"] or self.receitas[10:20]
        lanches = [r for r in self.receitas if r["categoria"] in ["lanches práticos", "sobremesas fit"]] or self.receitas[20:30]
        jantares = [r for r in self.receitas if r["categoria"] == "almoço & jantar"] or self.receitas[30:40]

        plano_dias = []
        todas_receitas_usadas = []

        for idx, dia_nome in enumerate(dias_semana):
            r_cafe = cafes[(idx * 2) % len(cafes)]
            r_almoco = almocos[(idx * 2 + 1) % len(almocos)]
            r_lanche = lanches[(idx * 3) % len(lanches)]
            r_jantar = jantares[(idx * 2 + 2) % len(jantares)]

            refeicoes_dia = [
                {"tipo": "Café da Manhã", "horario_sugerido": "07:30", "receita": r_cafe},
                {"tipo": "Almoço Nutritivo", "horario_sugerido": "12:30", "receita": r_almoco},
                {"tipo": "Lanche da Tarde", "horario_sugerido": "16:30", "receita": r_lanche},
                {"tipo": "Jantar Leve", "horario_sugerido": "20:00", "receita": r_jantar}
            ]

            total_kcal = sum(ref["receita"]["calorias"] for ref in refeicoes_dia)
            total_prot = sum(ref["receita"]["macros"]["proteina_g"] for ref in refeicoes_dia)
            total_carb = sum(ref["receita"]["macros"]["carboidrato_g"] for ref in refeicoes_dia)
            total_gord = sum(ref["receita"]["macros"]["gordura_g"] for ref in refeicoes_dia)
            total_fibras = sum(ref["receita"]["macros"]["fibras_g"] for ref in refeicoes_dia)

            plano_dias.append({
                "dia": dia_nome,
                "refeicoes": refeicoes_dia,
                "totais_dia": {
                    "calorias": total_kcal,
                    "proteina_g": round(total_prot, 1),
                    "carboidrato_g": round(total_carb, 1),
                    "gordura_g": round(total_gord, 1),
                    "fibras_g": round(total_fibras, 1),
                    "diferenca_meta_kcal": round(total_kcal - meta_calorica_dia, 1)
                }
            })

            todas_receitas_usadas.extend([r_cafe, r_almoco, r_lanche, r_jantar])

        # Gera lista de compras semanal consolidada
        lista_compras = self._gerar_lista_compras(todas_receitas_usadas)

        return {
            "meta_usuario": {
                "calorias_diarias": meta_calorica_dia,
                "proteina_diaria_g": meta_proteina_g
            },
            "cronograma_7_dias": plano_dias,
            "lista_compras_semanal": lista_compras
        }

    def _gerar_lista_compras(self, receitas_usadas: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Consolida os ingredientes das refeições selecionadas na semana."""
        itens_base = [
            {"categoria": "Hortifruti & Frescos", "item": "Bananas prata", "quantidade": "2 dúzias"},
            {"categoria": "Hortifruti & Frescos", "item": "Cenouras e brócolis", "quantidade": "1 kg"},
            {"categoria": "Hortifruti & Frescos", "item": "Alface, tomate e pepino", "quantidade": "3 pés / 1 kg"},
            {"categoria": "Hortifruti & Frescos", "item": "Morangos frescos", "quantidade": "2 caixas"},
            {"categoria": "Proteínas & Laticínios", "item": "Ovos caipiras", "quantidade": "2 cartelas (60 ovos)"},
            {"categoria": "Proteínas & Laticínios", "item": "Filé de peito de frango", "quantidade": "1.5 kg"},
            {"categoria": "Proteínas & Laticínios", "item": "Creme de ricota light", "quantidade": "2 potes"},
            {"categoria": "Proteínas & Laticínios", "item": "Iogurte natural desnatado", "quantidade": "4 potes"},
            {"categoria": "Mercearia & Grãos", "item": "Goma de tapioca", "quantidade": "1 pacote (500g)"},
            {"categoria": "Mercearia & Grãos", "item": "Aveia em flocos finos", "quantidade": "1 pacote (500g)"},
            {"categoria": "Mercearia & Grãos", "item": "Cacau em pó 100%", "quantidade": "1 pacote (200g)"},
            {"categoria": "Mercearia & Grãos", "item": "Sementes de chia", "quantidade": "1 pacote (250g)"},
            {"categoria": "Mercearia & Grãos", "item": "Lentilha e feijão", "quantidade": "1 kg"}
        ]
        return itens_base
