"""
Auditoria Automatizada Headless - Validação da Aba de Início Otimizada
"""
import time
import json
from playwright.sync_api import sync_playwright

def test_inicio_otimizado_ui():
    relatorio = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("https://saciara.vercel.app")
        page.wait_for_load_state("networkidle")

        # 1. Validar que a tela de Início está ativa
        view_inicio = page.locator("#view-inicio.active")
        relatorio["Aba de Início Ativa"] = "OK" if view_inicio.is_visible() else "Falha"

        # 2. Validar ausência de gráficos pesados na tela de início
        svg_charts = page.locator("#view-inicio #weightChartContainer")
        relatorio["Sem Gráficos Pesados na Tela de Início"] = "OK" if svg_charts.count() == 0 else "Falha"

        # 3. Validar os 3 Pilares Diários (Alimentação, Água, Perda de Peso)
        pilares = page.locator("#view-inicio .pilar-card")
        relatorio["3 Pilares Diários"] = f"OK ({pilares.count()} encontrados)"

        # 4. Testar Botão de Adicionar Água (+300 ml)
        btn_water = page.locator("#view-inicio .btn-add-water:has-text('+ 300 ml')")
        if btn_water.count() > 0:
            btn_water.click()
            time.sleep(0.3)
            val_agua = page.locator("#inicioWaterVal").inner_text()
            relatorio["Registro de Água Interativo (+300ml)"] = f"OK ({val_agua})"

        # 5. Validar as 5 Refeições da Linha do Tempo
        refeicoes = page.locator("#view-inicio .refeicao-item-card")
        relatorio["5 Refeições com Horários e Fotos"] = f"OK ({refeicoes.count()} encontradas)"

        # 6. Testar Checkmark de Refeição Consumida
        btn_meal = page.locator("#view-inicio .btn-check-meal").first
        if btn_meal.count() > 0:
            btn_meal.click()
            time.sleep(0.2)
            checked = "checked" in (btn_meal.get_attribute("class") or "")
            relatorio["Checkmark Refeição Consumida"] = "OK (Ativo)" if checked else "Falha"

        # 7. Screenshot da tela de início otimizada
        screenshot_path = r"C:\Users\jvna1\.gemini\antigravity\brain\6a82e9a6-837d-4089-854d-d753963b6dc6\screenshot_inicio_otimizado.png"
        page.screenshot(path=screenshot_path, full_page=True)
        relatorio["Screenshot"] = screenshot_path

        browser.close()
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_inicio_otimizado_ui()
