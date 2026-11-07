"""Modelo Fisiológico Dinâmico de Mudança de Peso Corporal (Hall Body Weight Model).
Baseado em:
  - Hall, K. D. et al. (2011). 'Quantification of the effect of energy imbalance on bodyweight'. The Lancet, 378(9793), 826-837.
  - NIH / NIDDK Body Weight Planner.

Substitui a regra simplista e errônea de '7.700 kcal = 1 kg' por um sistema dinâmico
de equações diferenciais acopladas que considera:
  1. Partição dinâmica de Forbes (perda de gordura vs perda de massa magra baseada no % de gordura inicial).
  2. Adaptação metabólica (queda da TMB conforme o peso e a ingestão caem).
  3. Custo decrescente do movimento (menor massa para deslocar).
  4. Depleção rápida de glicogênio e água nos primeiros dias.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class PerfilFisiologico:
    peso_kg: float
    altura_cm: float
    idade: int
    sexo: str  # 'M' ou 'F'
    bf_percentual: float  # Ex: 25.0 para 25% de gordura
    nivel_atividade: float = 1.4  # Fator PAL (1.2 sedentário, 1.4 moderado, 1.7 ativo)


class HallBodyWeightModel:
    """Implementação determinística do modelo dinâmico de Kevin D. Hall."""

    # Densidades energéticas dos tecidos (kcal / kg)
    RHO_FAT = 9400.0   # Gordura com pequena fração hídrica celular
    RHO_LEAN = 1800.0  # Massa magra (proteína + água intracelular)

    # Coeficientes metabólicos de repouso por tecido (kcal / kg / dia)
    GAMMA_LEAN = 21.6  # Custo metabólico da massa magra (órgãos nobres consomem muito)
    GAMMA_FAT = 3.2    # Custo metabólico do tecido adiposo

    # Constante de partição de Forbes (kg)
    FORBES_C = 10.4

    @classmethod
    def calcular_tmb_inicial(cls, perfil: PerfilFisiologico) -> float:
        """Calcula TMB basal baseada na composição corporal (Katch-McArdle) ou Mifflin-St Jeor."""
        fm = perfil.peso_kg * (perfil.bf_percentual / 100.0)
        ffm = perfil.peso_kg - fm
        # Katch-McArdle calibrado
        tmb = 370.0 + (cls.GAMMA_LEAN * ffm) + (cls.GAMMA_FAT * fm)
        return round(tmb, 1)

    @classmethod
    def calcular_tdee_inicial(cls, perfil: PerfilFisiologico) -> float:
        """Gasto Energético Total de Manutenção Inicial."""
        tmb = cls.calcular_tmb_inicial(perfil)
        # PAL (Physical Activity Level)
        return round(tmb * perfil.nivel_atividade, 1)

    @classmethod
    def particionar_forbes(cls, fm: float) -> float:
        """Calcula a fração p (proporção da alteração que vem da massa magra).
        Quanto maior a massa de gordura inicial (FM), MENOR é a perda de massa magra.
        """
        if fm <= 0.0:
            return 0.5
        p = cls.FORBES_C / (cls.FORBES_C + fm)
        # Limita p entre 5% e 45% em faixas normais de restrição não-extrema
        return max(0.05, min(0.45, p))

    @classmethod
    def simular_trajetoria(
        cls,
        perfil: PerfilFisiologico,
        ingestao_diaria_kcal: float,
        dias: int = 90
    ) -> Dict[str, Any]:
        """Simula a curva de evolução temporal do peso corporal dia a dia."""
        tdee_inicial = cls.calcular_tdee_inicial(perfil)
        rmr_inicial = cls.calcular_tmb_inicial(perfil)
        deficit_inicial = tdee_inicial - ingestao_diaria_kcal

        fm = perfil.peso_kg * (perfil.bf_percentual / 100.0)
        ffm = perfil.peso_kg - fm
        peso_atual = perfil.peso_kg

        # Gasto com atividade física por kg (AEE_0 = 0.90 * TDEE_0 - RMR_0, já que TEF_0 = 0.10 * TDEE_0)
        aee_inicial = max(0.0, (0.90 * tdee_inicial) - rmr_inicial)
        delta_atividade = aee_inicial / perfil.peso_kg

        # Dinâmica de glicogênio e água:
        # Em déficit calórico, o glicogênio cai nos primeiros 4 dias (~300g glicogênio + ~900g água = ~1.2kg)
        agua_glicogenio_perdida = 0.0
        max_agua_glicogenio = min(1.8, max(0.6, 0.015 * perfil.peso_kg)) if deficit_inicial > 0 else 0.0

        trajetoria: List[Dict[str, Any]] = []

        # Adaptação metabólica acumulada
        adaptacao_metabolica = 0.0

        # Simulação por diferenças finitas diárias (Euler 1 dia)
        for dia in range(1, dias + 1):
            # 1. Gasto Energético do dia calibrado
            rmr = 370.0 + (cls.GAMMA_LEAN * ffm) + (cls.GAMMA_FAT * fm)
            tef = 0.10 * ingestao_diaria_kcal  # Efeito térmico dos alimentos (~10%)
            aee = delta_atividade * (fm + ffm) # Custo do movimento cai com a perda de peso

            # Adaptação metabólica aumenta proporcionalmente ao déficit mantido
            if deficit_inicial > 0:
                adaptacao_alvo = 0.14 * deficit_inicial
                # Constante de tempo de resposta da adaptação (~14 dias)
                adaptacao_metabolica += (adaptacao_alvo - adaptacao_metabolica) * (1.0 / 14.0)

            ee_atual = rmr + tef + aee - adaptacao_metabolica
            balanco_energia = ingestao_diaria_kcal - ee_atual  # Negativo em déficit

            # 2. Partição entre Gordura e Massa Magra (Conservação Estrita de Energia)
            p = cls.particionar_forbes(fm)  # Fração de massa que vem da massa magra
            rho_tecido = ((1.0 - p) * cls.RHO_FAT) + (p * cls.RHO_LEAN)
            delta_peso_tecido = balanco_energia / rho_tecido

            delta_fm = (1.0 - p) * delta_peso_tecido
            delta_ffm = p * delta_peso_tecido

            fm = max(2.0, fm + delta_fm)
            ffm = max(10.0, ffm + delta_ffm)

            # 3. Dinâmica hídrica nos primeiros 5 dias
            if dia <= 5 and deficit_inicial > 0:
                queda_dia = (max_agua_glicogenio / 5.0)
                agua_glicogenio_perdida += queda_dia

            peso_calculado = fm + ffm - (agua_glicogenio_perdida if dia <= 5 else max_agua_glicogenio)

            # Modelo ingênuo comparativo (7700 kcal lineares sem adaptação)
            peso_ingenuo = perfil.peso_kg - ((deficit_inicial * dia) / 7700.0)

            trajetoria.append({
                "dia": dia,
                "peso_hall_kg": round(peso_calculado, 2),
                "massa_gordura_kg": round(fm, 2),
                "massa_magra_kg": round(ffm, 2),
                "bf_atual_percent": round((fm / (fm + ffm)) * 100.0, 1),
                "gasto_tdee_atual": round(ee_atual, 1),
                "adaptacao_metabolica_kcal": round(adaptacao_metabolica, 1),
                "peso_modelo_ingenuo_7700": round(peso_ingenuo, 2),
                "diferenca_real_vs_ingenuo": round(peso_calculado - peso_ingenuo, 2)
            })

        return {
            "perfil_inicial": {
                "peso": perfil.peso_kg,
                "tmb": cls.calcular_tmb_inicial(perfil),
                "tdee": tdee_inicial,
                "bf": perfil.bf_percentual
            },
            "parametros_plano": {
                "ingestao_kcal": ingestao_diaria_kcal,
                "deficit_inicial_kcal": round(deficit_inicial, 1),
                "dias": dias
            },
            "resultado_final": {
                "peso_final_hall": trajetoria[-1]["peso_hall_kg"],
                "perda_total_kg": round(perfil.peso_kg - trajetoria[-1]["peso_hall_kg"], 2),
                "gordura_perdida_kg": round((perfil.peso_kg * perfil.bf_percentual / 100.0) - trajetoria[-1]["massa_gordura_kg"], 2),
                "massa_magra_perdida_kg": round((perfil.peso_kg * (1.0 - perfil.bf_percentual / 100.0)) - trajetoria[-1]["massa_magra_kg"], 2),
                "tdee_final": trajetoria[-1]["gasto_tdee_atual"],
                "queda_metabolica_total": round(tdee_inicial - trajetoria[-1]["gasto_tdee_atual"], 1)
            },
            "trajetoria": trajetoria
        }
