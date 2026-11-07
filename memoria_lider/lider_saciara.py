"""Líder Especializado do Projeto Saciara Nutri & Fitness.
Localização: F:\\Nova pasta\\site\\saciara\\memoria_lider\\lider_saciara.py

Comanda o projeto Saciara com especialização absoluta no nicho fitness/fisiológico,
governando sua memória individual, ciclo de auto-melhoria contínua e acionando
a equipe de especialistas da raiz (F:\\Nova pasta\\site\\agentes).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

DIR_LIDER = Path(__file__).resolve().parent
DIR_SACIARA = DIR_LIDER.parent
DIR_RAIZ_SITES = DIR_SACIARA.parent

# Inclusão de caminhos
for p in [str(DIR_RAIZ_SITES), str(DIR_RAIZ_SITES / "agentes"), str(DIR_RAIZ_SITES / "memoria_coletiva")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from loop_melhoria_lider import LoopMelhoriaLiderSaciara
from agente_coletivo_bridge import equipe_compartilhada
from memoria_coletiva.memoria_coletiva_manager import memoria_coletiva


class LiderSaciara:
    """Líder Soberano do Projeto Saciara."""

    def __init__(self):
        self.nome = "LiderSaciara"
        self.papel = "Líder Soberano do Projeto Saciara (Fisiologia & Nutrição)"
        self.loop_melhoria = LoopMelhoriaLiderSaciara()
        self.equipe_externa = equipe_compartilhada
        self.memoria_coletiva = memoria_coletiva

    def obter_status_lideranca(self) -> Dict[str, Any]:
        """Retorna o estado da liderança, regras de ouro e última rodada de melhoria."""
        memoria = self.loop_melhoria.carregar_memoria_individual()
        return {
            "lider": self.nome,
            "projeto": "saciara",
            "meta_soberana": memoria.get("meta_soberana", ""),
            "parametros": memoria.get("parametros_auto_calibracao", {}),
            "regras_de_ouro": memoria.get("regras_de_ouro_individuais", []),
            "total_licoes_individuais": len(memoria.get("licoes_aprendidas_individuais", [])),
            "total_ciclos_realizados": len(memoria.get("historico_ciclos_melhoria", []))
        }

    def rodar_auto_melhoria(self) -> Dict[str, Any]:
        """Dispara uma iteração do loop de auto-melhoria contínua."""
        return self.loop_melhoria.executar_ciclo_melhoria()

    def delegar_para_especialista(self, especialista: str, acao: str, **kwargs) -> Any:
        """Delega demandas pontuais para os agentes que residem na pasta F:\\Nova pasta\\site\\agentes."""
        if especialista == "craftsman":
            return getattr(self.equipe_externa.craftsman, acao)(**kwargs)
        elif especialista == "devops":
            return getattr(self.equipe_externa.devops, acao)(**kwargs)
        elif especialista == "gatekeeper":
            return getattr(self.equipe_externa.gatekeeper, acao)(**kwargs)
        elif especialista == "seo":
            return getattr(self.equipe_externa.seo, acao)(**kwargs)
        elif especialista == "media":
            return getattr(self.equipe_externa.media, acao)(**kwargs)
        elif especialista == "visual":
            return getattr(self.equipe_externa.visual, acao)(**kwargs)
        elif especialista == "flow_scraping":
            return getattr(self.equipe_externa.flow_scraping, acao)(**kwargs)
        else:
            raise ValueError(f"Especialista '{especialista}' não encontrado na pasta F:\\Nova pasta\\site\\agentes")


if __name__ == "__main__":
    lider = LiderSaciara()
    print(f"--- [Iniciando {lider.nome}] ---")
    resultado = lider.rodar_auto_melhoria()
    print(f"Resultado do Ciclo de Auto-Melhoria: Score {resultado['score_qualidade']} | Aprovado: {resultado['aprovado']}")
