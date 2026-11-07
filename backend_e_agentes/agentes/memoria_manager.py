"""Gerenciador do Cofre de Memória Compartilhada e Isolada do Saciara Fitness.
Garante que todo aprendizado, catálogo de produtos e métricas fiquem 100% fechados nesta pasta.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

MEMORIA_PATH = Path(__file__).resolve().parent.parent / "memoria" / "memoria_saciara.json"


class MemoriaSaciaraManager:
    def __init__(self, path: Path = MEMORIA_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._criar_memoria_padrao()

    def carregar(self) -> Dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return self._criar_memoria_padrao()

    def salvar(self, dados: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    def registrar_story_publicado(self, item: Dict[str, Any]) -> None:
        dados = self.carregar()
        item["timestamp"] = datetime.now().isoformat()
        dados.setdefault("stories_publicados", []).append(item)
        dados["metricas_globais"]["total_stories_afiliados"] = len(dados["stories_publicados"])
        self.salvar(dados)

    def registrar_produto(self, produto: Dict[str, Any]) -> None:
        dados = self.carregar()
        produtos = dados.setdefault("produtos_catalogados", [])
        # Evita duplicatas pelo item_id ou link
        if not any(p.get("item_id") == produto.get("item_id") for p in produtos):
            produto["data_catalogado"] = datetime.now().isoformat()
            produtos.append(produto)
            dados["metricas_globais"]["total_produtos_garimpados"] = len(produtos)
            self.salvar(dados)

    def adicionar_aprendizado(self, regra: str, origem: str) -> None:
        dados = self.carregar()
        aprendizados = dados.setdefault("aprendizados_continuos", [])
        aprendizados.append({
            "data": datetime.now().strftime("%Y-%m-%d"),
            "regra": regra,
            "origem": origem
        })
        dados["metricas_globais"]["ciclos_automelhoria"] = len(aprendizados)
        self.salvar(dados)

    def obter_regras_aprendidas(self) -> List[Dict[str, str]]:
        return self.carregar().get("aprendizados_continuos", [])

    def _criar_memoria_padrao(self) -> Dict[str, Any]:
        padrao = {
            "versao": "1.0.0",
            "meta_soberana": "quero mais cliques no meu link",
            "canal": "@saciara_",
            "produtos_catalogados": [],
            "stories_publicados": [],
            "aprendizados_continuos": [],
            "metricas_globais": {
                "total_stories_afiliados": 0,
                "total_cliques_estimados": 0,
                "total_produtos_garimpados": 0,
                "ciclos_automelhoria": 0
            }
        }
        self.salvar(padrao)
        return padrao
