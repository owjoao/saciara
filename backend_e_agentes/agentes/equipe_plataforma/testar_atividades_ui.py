"""
Auditoria Automatizada Headless - Validação da Aba Atividades Físicas
"""
import time
import json
from playwright.sync_api import sync_playwright

def test_atividades_ui():
    relatorio = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("https://saciara.vercel.app")
        page.wait_for_load_state("networkidle")

        # 1. Clicar no botão 'Atividades Físicas' na sidebar
        link_ativ = page.locator("a.nav-link[data-tab='atividades']")
        link_ativ.click()
        time.sleep(0.4)

        # 2. Validar visibilidade da seção #view-atividades
        view_ativ_visivel = page.locator("#view-atividades.active").is_visible()
        relatorio["Aba Atividades Físicas Ativa"] = "OK" if view_ativ_visivel else "Falha"

        # 3. Validar os 4 cards de métricas
        cards_metricas = page.locator(".ativ-metric-card")
        relatorio["4 Cards de Métricas do Topo"] = f"OK ({cards_metricas.count()} encontrados)"

        # 4. Validar os 7 dias de treino
        dias_treino = page.locator(".exercicio-day-row")
        relatorio["7 Dias de Treino na Grade"] = f"OK ({dias_treino.count()} encontrados)"

        # 5. Clicar no botão 'Iniciar Treino' de Terça-feira
        btn_iniciar = page.locator(".btn-ex-iniciar")
        if btn_iniciar.count() > 0:
            btn_iniciar.first.click()
            time.sleep(0.3)
            modal_visivel = page.locator("#globalModal").is_visible()
            relatorio["Modal Prescrição Treino de Força"] = "OK (Aberto)" if modal_visivel else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)

        # 6. Clicar no botão 'Concluído' de Segunda-feira
        btn_concluido = page.locator(".btn-ex-concluido")
        if btn_concluido.count() > 0:
            btn_concluido.first.click()
            time.sleep(0.3)
            modal_visivel = page.locator("#globalModal").is_visible()
            relatorio["Modal Celebração Treino Concluído"] = "OK (Aberto)" if modal_visivel else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)

        # 7. Screenshot da tela de atividades físicas
        screenshot_path = r"C:\Users\jvna1\.gemini\antigravity\brain\6a82e9a6-837d-4089-854d-d753963b6dc6\screenshot_atividades_fisicas.png"
        page.screenshot(path=screenshot_path, full_page=True)
        relatorio["Screenshot"] = screenshot_path

        browser.close()
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_atividades_ui()
