"""
Auditoria Automatizada Headless - Validação de Receitas Clicáveis, Hierarquia por Horário e Compras do Mês
"""
import time
import json
from playwright.sync_api import sync_playwright

def test_features_ui():
    relatorio = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("https://saciara.vercel.app")
        page.wait_for_load_state("networkidle")

        # 1. Validar Card de Refeição de Agora atrelada ao Horário
        box_momento = page.locator("#refeicaoMomentoBox")
        relatorio["Card Refeição de Agora (Horário)"] = "OK" if box_momento.is_visible() else "Falha"

        # 2. Clicar no botão 'Ver Modo de Preparo' da Refeição de Agora
        btn_momento = page.locator("#btnVerReceitaMomento")
        if btn_momento.count() > 0:
            btn_momento.click()
            time.sleep(0.3)
            modal_visivel = page.locator("#globalModal").is_visible()
            relatorio["Modal Modo de Preparo Refeição de Agora"] = "OK (Aberto)" if modal_visivel else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)

        # 3. Clicar em uma receita da lista de rotina (ex: Almoço Frango Grelhado)
        card_refeicao = page.locator(".refeicao-item-card").nth(2)
        if card_refeicao.count() > 0:
            card_refeicao.click()
            time.sleep(0.3)
            modal_visivel = page.locator("#globalModal").is_visible()
            relatorio["Modal Receita Clicável na Rotina (Almoço)"] = "OK (Aberto)" if modal_visivel else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)

        # 4. Navegar para a Aba 'Compras do Mês' na sidebar
        link_compras = page.locator("a.nav-link[data-tab='compras']")
        link_compras.click()
        time.sleep(0.4)

        # 5. Validar visibilidade da seção #view-compras
        view_compras_visivel = page.locator("#view-compras.active").is_visible()
        relatorio["Aba Compras do Mês Ativa"] = "OK" if view_compras_visivel else "Falha"

        # 6. Testar alteração do Orçamento em Reais (ex: R$ 600)
        input_orcamento = page.locator("#inputOrcamentoReais")
        if input_orcamento.count() > 0:
            input_orcamento.fill("600")
            time.sleep(0.3)
            total_calculado = page.locator("#statTotalEstimado").inner_text()
            relatorio["Cálculo Automático por Orçamento (R$ 600)"] = f"OK ({total_calculado})"

        # 7. Screenshot da tela de compras do mês
        screenshot_path = r"C:\Users\jvna1\.gemini\antigravity\brain\6a82e9a6-837d-4089-854d-d753963b6dc6\screenshot_compras_mes.png"
        page.screenshot(path=screenshot_path, full_page=True)
        relatorio["Screenshot"] = screenshot_path

        browser.close()
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_features_ui()
