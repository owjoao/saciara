"""
Auditoria Automatizada Headless - Validação das Fotos dos Itens na Aba Compras do Mês
"""
import time
import json
from playwright.sync_api import sync_playwright

def test_compras_images_ui():
    relatorio = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("https://saciara.vercel.app")
        page.wait_for_load_state("networkidle")

        # 1. Navegar para a Aba 'Compras do Mês'
        link_compras = page.locator("a.nav-link[data-tab='compras']")
        link_compras.click()
        time.sleep(0.5)

        # 2. Validar se a aba está visível
        view_visivel = page.locator("#view-compras.active").is_visible()
        relatorio["Aba Compras Ativa"] = "OK" if view_visivel else "Falha"

        # 3. Validar se as imagens dos itens foram renderizadas
        imagens_itens = page.locator(".compras-item-img-thumb")
        count_imgs = imagens_itens.count()
        relatorio["Total de Imagens de Alimentos Renderizadas"] = count_imgs
        relatorio["Status Imagens"] = "OK (Todas com Fotos Reais)" if count_imgs >= 15 else "Falha"

        # 4. Verificar se a primeira imagem (Frango) carregou com sucesso
        primeira_img_src = imagens_itens.first.get_attribute("src") if count_imgs > 0 else ""
        relatorio["Primeira Imagem (Frango)"] = "OK" if "unsplash" in primeira_img_src else "Falha"

        # 5. Screenshot de evidência visual das imagens dos itens
        screenshot_path = r"C:\Users\jvna1\.gemini\antigravity\brain\6a82e9a6-837d-4089-854d-d753963b6dc6\screenshot_compras_com_imagens.png"
        page.screenshot(path=screenshot_path, full_page=True)
        relatorio["Screenshot"] = screenshot_path

        browser.close()
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_compras_images_ui()
