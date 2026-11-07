"""Módulo Fisiológico Feminino e Variações Transitórias do Ciclo Menstrual.
Evita alarmismo e cortes calóricos desnecessários durante a fase lútea, explicando
cientificamente a retenção hídrica induzida pela progesterona e a alteração da TMB.
"""
from __future__ import annotations

from typing import Any, Dict


class ModuloFisiologiaFeminina:
    """Modela o impacto voluntário das 4 fases hormonais sobre o peso, apetite e gasto calórico."""

    FASES = {
        "folicular": {
            "nome": "Fase Folicular (Pós-Menstruação)",
            "dias_estimados": "Dias 6 a 13",
            "impacto_peso": "Peso mais real e estável da balança (baixa retenção).",
            "metabolismo_basal": "Linha de base padrão.",
            "sensibilidade_insulina": "Alta (ótima tolerância a carboidratos complexos).",
            "ajuste_calorico_recomendado": 0.0,
            "orientacao": "Excelente fase para treinos de força e consolidação do déficit calórico."
        },
        "ovulatoria": {
            "nome": "Fase Ovulatória",
            "dias_estimados": "Dias 14 a 16",
            "impacto_peso": "Leve aumento transitório (0.3 a 0.7 kg) por pico de estrogênio.",
            "metabolismo_basal": "Leve elevação.",
            "sensibilidade_insulina": "Estável.",
            "ajuste_calorico_recomendado": 0.0,
            "orientacao": "Pico de energia física e disposição."
        },
        "lutea": {
            "nome": "Fase Lútea / Pré-Menstrual (TPM)",
            "dias_estimados": "Dias 17 a 28",
            "impacto_peso": "Retenção hídrica natural de 1.0 kg a 2.5 kg mediada por progesterona e aldosterona. NÃO é gordura corporal.",
            "metabolismo_basal": "Aumenta entre 100 e 250 kcal/dia devido ao trabalho do corpo lúteo.",
            "sensibilidade_insulina": "Mais baixa (aumento natural do apetite e vontade de doces/carboidratos).",
            "ajuste_calorico_recomendado": 150.0,  # Aumento seguro de 150 kcal (manutenção funcional)
            "orientacao": "A balança subirá temporariamente. NÃO corte calorias. Aumente magnésio, potássio e hidratação. O peso cai sozinho após a descida da menstruação."
        },
        "menstrual": {
            "nome": "Fase Menstrual",
            "dias_estimados": "Dias 1 a 5",
            "impacto_peso": "Rápida eliminação da água acumulada (queda de 1 a 2 kg nos primeiros 3 dias).",
            "metabolismo_basal": "Retornando à linha de base.",
            "sensibilidade_insulina": "Em recuperação.",
            "ajuste_calorico_recomendado": 0.0,
            "orientacao": "Foco em ferro biodisponível (feijão com limão, carnes magras) e descanso."
        }
    }

    @classmethod
    def diagnosticar_fase(cls, dia_do_ciclo: int) -> Dict[str, Any]:
        """Recebe o dia do ciclo (1 a 28/32) e retorna os dados biológicos correspondentes."""
        dia_norm = max(1, min(35, dia_do_ciclo))
        if 1 <= dia_norm <= 5:
            chave = "menstrual"
        elif 6 <= dia_norm <= 13:
            chave = "folicular"
        elif 14 <= dia_norm <= 16:
            chave = "ovulatoria"
        else:
            chave = "lutea"

        info = cls.FASES[chave]
        return {
            "dia_informado": dia_norm,
            "chave_fase": chave,
            **info
        }
