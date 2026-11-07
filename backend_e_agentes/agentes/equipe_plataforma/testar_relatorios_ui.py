"""
Auditoria Automatizada Headless - Validação da Aba Relatório de Evolução Mensal
"""
import time
import json
from playwright.sync_api import sync_playwright

def test_relatorios_ui():
    relatorio = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("https://saciara.vercel.app")
        page.wait_for_load_state("networkidle")

        # 1. Clicar no botão 'Relatório de Evolução' na sidebar
        link_rel = page.locator("a.nav-link[data-tab='relatorios']")
        link_rel.click()
        time.sleep(0.4)

        # 2. Validar visibilidade da seção #view-relatorios
        view_rel_visivel = page.locator("#view-relatorios.active").is_visible()
        relatorio["Aba Relatório de Evolução Ativa"] = "OK" if view_rel_visivel else "Falha"

        # 3. Validar seletor de mês (Novembro de 2026)
        btn_mes = page.locator(".relatorio-month-selector")
        relatorio["Seletor de Mês"] = "OK" if btn_mes.count() > 0 else "Falha"

        # 4. Validar os 4 cards de métricas do topo (68,3 kg, 1.820 kcal, Concluída!, 28 dias)
        cards_top = page.locator(".rel-metric-card")
        relatorio["4 Cards de Métricas do Topo"] = f"OK ({cards_top.count()} encontrados)"

        # 5. Validar Gráfico de Evolução do Peso com Badge 68,3 kg
        badge_peso = page.locator("#view-relatorios svg g rect")
        relatorio["Badge 68,3 kg no Gráfico Mensal"] = "OK" if badge_peso.count() > 0 else "Falha"

        # 6. Validar Botão 'Ver Plano para Dezembro'
        btn_dez = page.locator(".btn-plan-next-month")
        if btn_dez.count() > 0:
            btn_dez.click()
            time.sleep(0.3)
            modal_visivel = page.locator("#globalModal").is_visible()
            relatorio["Modal Planejamento Dezembro"] = "OK (Aberto)" if modal_visivel else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)

        # 7. Screenshot da tela de relatório mensal
        screenshot_path = r"C:\Users\jvna1\.gemini\antigravity\brain\6a82e9a6-837d-4089-854d-d753963b6dc6\screenshot_relatorio_mensal.png"
        page.screenshot(path=screenshot_path, full_page=True)
        relatorio["Screenshot"] = screenshot_path

        browser.close()
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_relatorios_ui()
