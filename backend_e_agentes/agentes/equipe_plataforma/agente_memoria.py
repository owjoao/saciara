"""Gerenciador da Memória Coletiva e Loop de Automelhoria da Equipe Saciara Nutri.
Garante que todos os agentes compartilhem aprendizados e que erros cometidos sejam
documentados e nunca repetidos.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

MEMORIA_PATH = Path(__file__).resolve().parent / "memoria_equipe.json"


class MemoriaEquipeManager:
    def __init__(self, caminho_arquivo: Path = MEMORIA_PATH):
        self.caminho = caminho_arquivo

    def carregar(self) -> Dict[str, Any]:
        if not self.caminho.exists():
            return {}
        try:
            return json.loads(self.caminho.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error("Erro ao ler memória da equipe: %s", e)
            return {}

    def salvar(self, dados: Dict[str, Any]) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self.caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")

    def registrar_aprendizado(self, modulo: str, erro_detectado: str, causa_raiz: str, correcao_adotada: str, regra_aprendida: str) -> None:
        """Registra um novo erro detectado e a regra aprendida para evitar repetições."""
        dados = self.carregar()
        historico = dados.setdefault("historico_erros_e_licoes", [])
        novo_id = len(historico) + 1
        item = {
            "id": novo_id,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modulo": modulo,
            "erro_detectado": erro_detectado,
            "causa_raiz": causa_raiz,
            "correcao_adotada": correcao_adotada,
            "regra_aprendida": regra_aprendida
        }
        historico.append(item)
        regras = dados.setdefault("regras_de_ouro", [])
        if regra_aprendida not in regras:
            regras.append(regra_aprendida)

        self.salvar(dados)
        logger.info("Nova lição aprendida registrada na memória coletiva [ID #%s]: %s", novo_id, regra_aprendida)

    def obter_regras_de_ouro(self) -> List[str]:
        dados = self.carregar()
        return dados.get("regras_de_ouro", [])

    def atualizar_metricas(self, **kwargs) -> None:
        dados = self.carregar()
        metricas = dados.setdefault("metricas_qualidade", {})
        metricas.update(kwargs)
        self.salvar(dados)
