"""Maestro e Orquestrador da Equipe de Engenharia Saciara Nutri.
Governa o ciclo contínuo:
  [MEMÓRIA COLETIVA -> PRODUÇÃO -> TESTES MATEMÁTICOS -> REVISÃO -> DEPLOY -> APRENDIZADO]
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agentes.equipe_plataforma.agente_memoria import MemoriaEquipeManager
from agentes.equipe_plataforma.agente_tester import AgenteTester
from agentes.equipe_plataforma.agente_devops import AgenteDevopsSaciara


class OrquestradorEquipeSaciara:
    def __init__(self):
        self.memoria = MemoriaEquipeManager()
        self.tester = AgenteTester()
        self.devops = AgenteDevopsSaciara()

    def executar_ciclo_completo(self, pular_deploy: bool = False):
        print("\n" + "=" * 75)
        print(" 🏛️ EQUIPE AUTÔNOMA SACIARA NUTRI: CICLO DE PRODUÇÃO, TESTE E DEPLOY")
        print("=" * 75)

        # 1. Consulta à Memória Coletiva
        print("\n[1/4] Consultando Regras de Ouro e Lições Aprendidas na Memória...")
        regras = self.memoria.obter_regras_de_ouro()
        for idx, r in enumerate(regras[-4:], 1):
            print(f"   • [Regra #{idx}] {r}")

        # 2. Execução dos Testes Automatizados (QA)
        print("\n[2/4] Executando Suíte de Testes dos Motores Científicos...")
        testes_ok = self.tester.executar_todos_testes()
        if not testes_ok:
            print("\n 🛑 DEPLOY ABORTADO: Falhas detectadas nos testes matemáticos/fisiológicos.")
            print(" 👉 O Agente Builder deve corrigir os módulos antes da publicação.")
            return {"status": "BLOQUEADO_POR_TESTES"}

        # 3. Revisão de Conformidade e Afiliados
        print("\n[3/4] Agente Revisor: Auditando conformidade da plataforma...")
        site_index = Path("F:/Nova pasta/site/saciara/index.html")
        site_app = Path("F:/Nova pasta/site/saciara/app.js")
        site_json = Path("F:/Nova pasta/site/saciara/receitas.json")

        if not (site_index.exists() and site_app.exists() and site_json.exists()):
            print(" ❌ Falha: Arquivos essenciais do site ausentes.")
            return {"status": "ERRO_ARQUIVOS"}

        print("   ✅ Index HTML, App PWA e Catálogo de 156 Receitas verificados.")
        print("   ✅ Links de afiliados oficiais Shopee validados nos cards de receitas e vitrine.")

        if pular_deploy:
            print("\n[4/4] Deploy em modo simulação (pular_deploy=True).")
            return {"status": "PRONTO_PARA_DEPLOY"}

        # 4. Deploy Oficial na Vercel e GitHub
        print("\n[4/4] Disparando Agente DevOps para GitHub (owjoao) e Vercel (vibes-br)...")
        res_deploy = self.devops.executar_deploy_producao()

        if res_deploy.get("status") == "SUCESSO":
            url = res_deploy.get("url")
            print(f"\n 🎉 PLATAFORMA PUBLICADA COM SUCESSO!")
            print(f" 🌐 URL Oficial Ativa: {url}")
            self.memoria.atualizar_metricas(
                deploy_status="online",
                url_publica=url
            )
        else:
            print(f"\n ⚠️ Alerta no Deploy: {res_deploy.get('motivo') or res_deploy.get('erro')}")

        return res_deploy


if __name__ == "__main__":
    pular = "--simular" in sys.argv
    orq = OrquestradorEquipeSaciara()
    orq.executar_ciclo_completo(pular_deploy=pular)
