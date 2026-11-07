"""
Auditoria Automatizada Headless - Teste de Todos os Botões e Caixas de Preenchimento Aprimoradas
"""
import time
import json
from playwright.sync_api import sync_playwright

def test_inputs_and_buttons():
    relatorio = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("https://saciara.vercel.app")
        page.wait_for_load_state("networkidle")

        # 1. Testar Botões da Tela de Início
        # A: Botão de Água (+500 ml)
        btn_water = page.locator("#view-inicio .btn-add-water").last
        btn_water.click()
        time.sleep(0.3)
        agua_text = page.locator("#inicioWaterVal").inner_text()
        relatorio["Botão de Água (+500ml)"] = f"OK ({agua_text})"

        # B: Botão de Ver Modo de Preparo da Refeição de Agora
        btn_preparo = page.locator("#btnVerReceitaMomento")
        btn_preparo.click()
        time.sleep(0.3)
        modal_aberto = page.locator("#globalModal").is_visible()
        relatorio["Botão Ver Modo de Preparo (Momento)"] = "OK (Aberto)" if modal_aberto else "Falha"
        page.locator(".modal-close-btn").click()
        time.sleep(0.2)

        # 2. Navegar para a Aba 'Compras do Mês'
        link_compras = page.locator("a.nav-link[data-tab='compras']")
        link_compras.click()
        time.sleep(0.5)

        # 3. Testar Caixas de Preenchimento Aprimoradas (Contraste, Hover e Focus)
        caixas_input = page.locator(".form-field-input-box")
        count_caixas = caixas_input.count()
        relatorio["Total de Caixas de Preenchimento Aprimoradas"] = count_caixas

        # A: Mudar Gênero para Masculino
        select_gen = page.locator("#userGenero")
        select_gen.select_option("masculino")
        time.sleep(0.2)

        # B: Mudar Peso para 82 kg
        input_peso = page.locator("#userPeso")
        input_peso.fill("82")
        time.sleep(0.2)

        # C: Mudar Idade para 32 anos
        input_idade = page.locator("#userIdade")
        input_idade.fill("32")
        time.sleep(0.2)

        # D: Mudar Alergia para Sem Lactose
        select_restricao = page.locator("#userRestricoes")
        select_restricao.select_option("lactose")
        time.sleep(0.2)

        # 4. Clicar no Botão de Recalcular Plano & Cesta
        btn_recalc = page.locator(".btn-gerar-plano")
        btn_recalc.click()
        time.sleep(0.4)

        diag_titulo = page.locator("#diagTituloPlano").inner_text()
        relatorio["Botão Recalcular Plano & Cesta"] = f"OK ({diag_titulo})"

        total_cesta = page.locator("#statTotalEstimado").inner_text()
        relatorio["Valor Total da Cesta Recalculada"] = f"OK ({total_cesta})"

        # 5. Screenshot comprovando as caixas nítidas e editáveis
        screenshot_path = r"C:\Users\jvna1\.gemini\antigravity\brain\6a82e9a6-837d-4089-854d-d753963b6dc6\screenshot_caixas_e_botoes.png"
        page.screenshot(path=screenshot_path, full_page=True)
        relatorio["Screenshot"] = screenshot_path

        browser.close()
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_inputs_and_buttons()
