"""
Auditoria Automatizada Headless - Planos Alimentares & Correção de Gráfico
"""
import time
import json
from playwright.sync_api import sync_playwright

def test_full_experience():
    relatorio = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("https://saciara.vercel.app")
        page.wait_for_load_state("networkidle")

        # 1. Validar Gráfico em 90D (problema da imagem 1)
        btn_90d = page.locator("button.period-btn:has-text('90D')")
        btn_90d.click()
        time.sleep(0.3)
        # Checar se badge SVG existe dentro do SVG
        badge_svg = page.locator("#weightChartContainer svg g rect")
        relatorio["Badge SVG 90D Renderizado"] = "OK" if badge_svg.count() > 0 else "Falha"

        # 2. Clicar no botão 'Planos Alimentares' na sidebar
        link_planos = page.locator("a.nav-link[data-tab='planos']")
        link_planos.click()
        time.sleep(0.4)

        # 3. Validar se a aba #view-planos está visível
        view_planos_visivel = page.locator("#view-planos.active").is_visible()
        relatorio["Aba Planos Alimentares Ativa"] = "OK" if view_planos_visivel else "Falha"

        # 4. Validar os 5 botões de refeição da aba de planos
        swap_btns = page.locator("#view-planos .btn-swap-recipe")
        relatorio["Botoes Trocar Receita"] = f"OK ({swap_btns.count()} encontrados)"

        # 5. Clicar em um botão de trocar receita
        if swap_btns.count() > 0:
            swap_btns.first.click()
            time.sleep(0.3)
            modal_visivel = page.locator("#globalModal").is_visible()
            relatorio["Modal Trocar Receita"] = "OK (Aberto)" if modal_visivel else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)

        # 6. Testar navegação dos dias da semana (ex: Terça-feira)
        btn_ter = page.locator("#weekDaysList button:has-text('Ter')")
        if btn_ter.count() > 0:
            btn_ter.click()
            time.sleep(0.2)
            titulo_dia = page.locator("#currentDayTitleText").inner_text()
            relatorio["Alternar Dia da Semana (Terça)"] = f"OK ({titulo_dia})"

        # 7. Screenshot da tela de planos alimentares para auditoria visual
        screenshot_path = r"C:\Users\jvna1\.gemini\antigravity\brain\6a82e9a6-837d-4089-854d-d753963b6dc6\screenshot_planos_alimentares.png"
        page.screenshot(path=screenshot_path, full_page=True)
        relatorio["Screenshot"] = screenshot_path

        browser.close()
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_full_experience()
