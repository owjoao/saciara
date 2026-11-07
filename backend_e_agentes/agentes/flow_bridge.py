"""Ponte de Integração com Google Flow (via F:\Nova pasta\scraping).
Permite upscale de imagens de produtos Shopee e geração de variações 2K/4K de estúdio.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

SCRAPING_DIR = Path("F:/Nova pasta/scraping")


class FlowBridge:
    def __init__(self, cdp_port: int = 9222):
        self.cdp_port = cdp_port
        self.scraping_dir = SCRAPING_DIR

    def is_cdp_online(self) -> bool:
        """Verifica se o navegador Brave com Google Flow está aberto na porta CDP 9222."""
        try:
            url = f"http://127.0.0.1:{self.cdp_port}/json/version"
            with urllib.request.urlopen(url, timeout=1.5) as r:
                return r.status == 200
        except Exception:
            return False

    def upscale_ou_gerar_estudio(
        self,
        imagem_referencia: Path,
        prompt: str,
        output_path: Path
    ) -> bool:
        """Envia imagem de referência da Shopee para o Google Flow e gera variação de estúdio 9:16."""
        if not self.is_cdp_online():
            logger.info("Brave com CDP 9222 não detectado. Usando imagem oficial direta do catálogo Shopee.")
            return False

        sys.path.insert(0, str(self.scraping_dir))
        try:
            import asyncio
            from generate_flow_image import generate
            print(f"[Flow Bridge] Conectando ao Flow para upscale/estúdio: {imagem_referencia.name}")
            sucesso = asyncio.run(generate(prompt_text=prompt, output_path=str(output_path), reference_path=str(imagem_referencia)))
            return sucesso
        except Exception as e:
            logger.warning("Falha na ponte do Google Flow: %s", e)
            return False
