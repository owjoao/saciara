"""Agente Autônomo de DevOps e Deploy da Equipe Saciara.
Orquestra, versiona e publica a plataforma no GitHub (owjoao) e na Vercel (vibes-br)
utilizando o pipeline oficial de deploy.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

SITE_DIR = Path("F:/Nova pasta/site")
DEPLOY_SCRIPT = SITE_DIR / "scripts" / "deploy_site.py"
SACIARA_DIR = SITE_DIR / "saciara"


class AgenteDevopsSaciara:
    def __init__(self):
        self.site_dir = SITE_DIR
        self.saciara_dir = SACIARA_DIR
        self.deploy_script = DEPLOY_SCRIPT

    def executar_deploy_producao(self) -> Dict[str, Any]:
        """Executa o pipeline oficial de publicação (GitHub + Vercel)."""
        print("\n" + "=" * 65)
        print(" 🚀 AGENTE DEVOPS: Iniciando Deploy Oficial para Vercel & GitHub")
        print("=" * 65)

        if not self.saciara_dir.exists():
            return {"status": "ERRO", "motivo": "Diretório saciara não localizado"}

        cmd = [sys.executable, str(self.deploy_script), "saciara"]
        print(f"Executando: {' '.join(cmd)}...\n")

        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            res = subprocess.run(
                cmd,
                cwd=str(self.site_dir),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=flags
            )
            print(res.stdout)
            if res.stderr:
                print("STDERR:", res.stderr)

            # Analisa se houve sucesso
            sucesso = res.returncode == 0 and ("Deploy com sucesso" in res.stdout or "HTTP 200" in res.stdout or "https://" in res.stdout)
            
            # Extrai URL se disponível
            url_encontrada = None
            import re
            urls = re.findall(r"https://[a-zA-Z0-9\-\.]+\.vercel\.app", res.stdout)
            if urls:
                url_encontrada = urls[-1]

            return {
                "status": "SUCESSO" if sucesso else "FALHA",
                "codigo_retorno": res.returncode,
                "url": url_encontrada or "https://saciara.vercel.app",
                "log": res.stdout[-500:] if res.stdout else ""
            }
        except Exception as e:
            logger.error("Erro durante o deploy: %s", e)
            return {"status": "ERRO", "erro": str(e)}


if __name__ == "__main__":
    dev = AgenteDevopsSaciara()
    resultado = dev.executar_deploy_producao()
    print("Resultado:", resultado)
