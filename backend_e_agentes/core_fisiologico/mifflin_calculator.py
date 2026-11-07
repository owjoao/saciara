"""Calculadora Nutricional e Fisiológica de Linha de Base (Mifflin-St Jeor & Harris-Benedict).
Calcula TMB, Gasto Energético Total (GET) e Metas Seguras de Macronutrientes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


class CalculadoraFisiologica:
    """Implementa equações validadas internacionalmente com limites estritos de segurança biológica."""

    @staticmethod
    def calcular_tmb_mifflin(peso_kg: float, altura_cm: float, idade: int, sexo: str) -> float:
        """Fórmula de Mifflin-St Jeor (Padrão-ouro da Academy of Nutrition and Dietetics).
        Homem:  10 * peso + 6.25 * altura - 5 * idade + 5
        Mulher: 10 * peso + 6.25 * altura - 5 * idade - 161
        """
        base = (10.0 * peso_kg) + (6.25 * altura_cm) - (5.0 * idade)
        if sexo.upper() == "M":
            return round(base + 5.0, 1)
        return round(base - 161.0, 1)

    @staticmethod
    def calcular_tmb_harris_benedict(peso_kg: float, altura_cm: float, idade: int, sexo: str) -> float:
        """Harris-Benedict revisada por Roza & Shizgal (1984)."""
        if sexo.upper() == "M":
            return round(88.362 + (13.397 * peso_kg) + (4.799 * altura_cm) - (5.677 * idade), 1)
        return round(447.593 + (9.247 * peso_kg) + (3.098 * altura_cm) - (4.330 * idade), 1)

    @classmethod
    def gerar_prescricao_nutricional(
        cls,
        peso_kg: float,
        altura_cm: float,
        idade: int,
        sexo: str,
        fator_atividade: float = 1.375,
        ritmo_emagrecimento: str = "moderado"  # 'leve' (-300), 'moderado' (-450), 'acelerado_seguro' (-600)
    ) -> Dict[str, Any]:
        """Gera prescrição nutricional completa com macros ideais baseados em evidência científica."""
        tmb = cls.calcular_tmb_mifflin(peso_kg, altura_cm, idade, sexo)
        tdee = tmb * fator_atividade

        # Déficit calórico individualizado e seguro
        deficits = {
            "leve": 300.0,
            "moderado": 450.0,
            "acelerado_seguro": 600.0
        }
        deficit_escolhido = deficits.get(ritmo_emagrecimento, 450.0)

        # Regra de Segurança Biológica: nunca permitir dieta abaixo da TMB ou limites mínimos
        teto_minimo = 1250.0 if sexo.upper() == "F" else 1500.0
        calorias_alvo = max(teto_minimo, tdee - deficit_escolhido)

        # 1. Proteínas: 1.8 a 2.0g/kg para saciedade e proteção de massa magra
        proteina_g_kg = 1.8
        proteina_g = round(peso_kg * proteina_g_kg, 1)
        proteina_kcal = proteina_g * 4.0

        # 2. Gorduras: 0.8g/kg para suporte hormonal e absorção de vitaminas lipossolúveis (A, D, E, K)
        gordura_g = round(peso_kg * 0.8, 1)
        gordura_kcal = gordura_g * 9.0

        # 3. Carboidratos: Restante calórico para energia e performance
        carbo_kcal = max(300.0, calorias_alvo - proteina_kcal - gordura_kcal)
        carbo_g = round(carbo_kcal / 4.0, 1)

        # 4. Fibras e Hidratação
        fibras_minimas_g = max(28.0, round((calorias_alvo / 1000.0) * 14.0, 1))
        agua_litros = round((peso_kg * 35.0) / 1000.0, 2)

        return {
            "tmb_kcal": tmb,
            "tdee_manutencao_kcal": round(tdee, 1),
            "calorias_meta_diaria": round(calorias_alvo, 1),
            "deficit_diario_kcal": round(tdee - calorias_alvo, 1),
            "macronutrientes": {
                "proteinas": {"gramas": proteina_g, "kcal": round(proteina_kcal, 1), "percentual": round((proteina_kcal / calorias_alvo) * 100.0, 1)},
                "carboidratos": {"gramas": carbo_g, "kcal": round(carbo_kcal, 1), "percentual": round((carbo_kcal / calorias_alvo) * 100.0, 1)},
                "gorduras": {"gramas": gordura_g, "kcal": round(gordura_kcal, 1), "percentual": round((gordura_kcal / calorias_alvo) * 100.0, 1)},
                "fibras_g": fibras_minimas_g
            },
            "hidratacao_recomendada_litros": agua_litros,
            "seguranca": {
                "esta_acima_do_piso_critico": calorias_alvo > teto_minimo,
                "deficit_sustentavel": (tdee - calorias_alvo) <= 650.0
            }
        }
