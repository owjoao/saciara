"""Filtro de Kalman e Estimativa Adaptativa de TDEE Reverso.
Separa as oscilações hídricas diárias (ruído da balança) da real tendência de tecido adiposo,
calculando o Gasto Energético Total Real (TDEE Reverso) com base no consumo alimentar registrado.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class FiltroKalmanPeso:
    """Filtro de Kalman 1D calibrado para ruído de pesagem corporal humana."""

    def __init__(self, q: float = 0.005, r: float = 0.8):
        """
        q: Variância do processo (mudança fisiológica real máxima por dia em kg^2).
        r: Variância da medição (ruído de água, sódio, fezes, balança em kg^2).
        """
        self.q = q
        self.r = r
        self.x = 0.0  # Estado estimado (peso real)
        self.p = 1.0  # Incerteza da estimativa
        self.inicializado = False

    def atualizar(self, medicao_peso: float) -> Tuple[float, float]:
        """Recebe uma pesagem da balança e retorna (peso_filtrado, incerteza)."""
        if not self.inicializado:
            self.x = medicao_peso
            self.p = self.r
            self.inicializado = True
            return self.x, self.p

        # Etapa de Predição
        x_pred = self.x
        p_pred = self.p + self.q

        # Ganho de Kalman
        k = p_pred / (p_pred + self.r)

        # Etapa de Atualização
        self.x = x_pred + k * (medicao_peso - x_pred)
        self.p = (1.0 - k) * p_pred

        return round(self.x, 2), round(self.p, 3)

    def filtrar_serie(self, serie_pesos: List[float]) -> List[float]:
        """Filtra uma lista histórica completa de pesos diários."""
        self.inicializado = False
        resultado = []
        for p in serie_pesos:
            x_filt, _ = self.atualizar(p)
            resultado.append(x_filt)
        return resultado


class MotorAdaptativoTDEE:
    """Calcula a estimativa adaptativa do TDEE com base na curva de tendência de peso."""

    DENSIDADE_TECIDO_MISTO = 7400.0  # kcal por kg de tecido corporal real perdido na prática

    @classmethod
    def calcular_ema(cls, serie: List[float], alpha: float = 0.15) -> List[float]:
        """Calcula Exponential Moving Average (Média Móvel Exponencial)."""
        if not serie:
            return []
        ema = [serie[0]]
        for val in serie[1:]:
            novo = alpha * val + (1.0 - alpha) * ema[-1]
            ema.append(round(novo, 2))
        return ema

    @classmethod
    def estimar_tdee_reverso(
        cls,
        historico_dias: List[Dict[str, float]],
        janela_dias: int = 14
    ) -> Dict[str, Any]:
        """
        historico_dias: Lista de dicts com {'peso_balanca': float, 'kcal_consumidas': float}
        janela_dias: Mínimo de 14 dias para relevância estatística.
        """
        if len(historico_dias) < 7:
            return {
                "tdee_adaptativo": None,
                "confiabilidade": "baixa",
                "motivo": f"Amostra insuficiente ({len(historico_dias)} dias). Mínimo de 7 a 14 dias necessários."
            }

        recorte = historico_dias[-janela_dias:]
        pesos = [d["peso_balanca"] for d in recorte]
        kcals = [d["kcal_consumidas"] for d in recorte if d.get("kcal_consumidas")]

        if not kcals:
            return {"tdee_adaptativo": None, "confiabilidade": "baixa", "motivo": "Sem dados calóricos"}

        media_ingestao = sum(kcals) / len(kcals)

        # Aplica Kalman para extrair delta de peso real sem ruído
        kalman = FiltroKalmanPeso()
        pesos_filtrados = kalman.filtrar_serie(pesos)

        delta_peso_kg = pesos_filtrados[-1] - pesos_filtrados[0]
        dias_intervalo = max(1, len(pesos) - 1)

        taxa_diaria_kg = delta_peso_kg / dias_intervalo
        deficit_diario_observado = - (taxa_diaria_kg * cls.DENSIDADE_TECIDO_MISTO)

        tdee_calculado = media_ingestao + deficit_diario_observado

        # Limites biológicos de sanidade (entre 1200 e 4000 kcal)
        tdee_sanitizado = max(1200.0, min(4000.0, tdee_calculado))

        # Detecta se houve platô transitório (ruído hídrico)
        variacao_bruta = pesos[-1] - pesos[0]
        eh_ruido_hidrico = abs(variacao_bruta - delta_peso_kg) > 0.4

        return {
            "tdee_adaptativo": round(tdee_sanitizado, 1),
            "media_ingestao_kcal": round(media_ingestao, 1),
            "taxa_perda_semanal_kg": round(-taxa_diaria_kg * 7.0, 2),
            "peso_filtrado_atual": pesos_filtrados[-1],
            "peso_bruto_atual": pesos[-1],
            "diferenca_ruido_hidrico": round(pesos[-1] - pesos_filtrados[-1], 2),
            "alerta_retencao_hidrica": eh_ruido_hidrico,
            "confiabilidade": "alta" if len(recorte) >= 14 else "moderada"
        }
