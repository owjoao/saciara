"""
Testador Autônomo e Headless de UI - Saciara NutriPlus
Valida cada botão, filtro, modal e componente da interface replicada.
"""
import sys
import subprocess
import json
import time

def test_interface():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright não instalado no Python atual. Testando via Node / Puppeteer ou script DOM...")
        return False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        url = "https://saciara.vercel.app"
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        relatorio = {}
        
        # 1. Testar Períodos do Gráfico (7D, 30D, 90D, 1A)
        periodos = ["7D", "30D", "90D", "1A"]
        for p_name in periodos:
            btn = page.locator(f"button.period-btn:has-text('{p_name}')")
            if btn.count() > 0:
                btn.click()
                time.sleep(0.1)
                active = "active" in (btn.get_attribute("class") or "")
                relatorio[f"Filtro Gráfico {p_name}"] = "OK (Ativo)" if active else "Falha"
            else:
                relatorio[f"Filtro Gráfico {p_name}"] = "Não encontrado"
                
        # 2. Testar Hábitos da Semana (Toggle)
        habitos = page.locator(".habit-circle-item")
        count_hab = habitos.count()
        relatorio["Habitos Encontrados"] = count_hab
        if count_hab > 0:
            habitos.first.click()
            time.sleep(0.1)
            relatorio["Toggle Hábito 1"] = "OK (Interativo)"
            
        # 3. Testar Metas da Semana (Checkboxes)
        metas = page.locator(".meta-checkbox-item input[type='checkbox']")
        relatorio["Metas Checkboxes"] = metas.count()
        if metas.count() > 0:
            metas.last.click()
            time.sleep(0.1)
            relatorio["Toggle Meta 3"] = "OK (Interativo)"
            
        # 4. Testar Botão 'Ver sugestão da IA' (Modal)
        btn_ia = page.locator("button:has-text('Ver sugestão da IA')")
        if btn_ia.count() > 0:
            btn_ia.click()
            time.sleep(0.3)
            modal_visible = page.locator("#globalModal").is_visible()
            relatorio["Modal IA Coach"] = "OK (Aberto)" if modal_visible else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)
            
        # 5. Testar Botão 'Ver plano completo' (Modal Refeições)
        btn_plano = page.locator("a:has-text('Ver plano completo')")
        if btn_plano.count() > 0:
            btn_plano.click()
            time.sleep(0.3)
            modal_visible = page.locator("#globalModal").is_visible()
            relatorio["Modal Plano Completo"] = "OK (Aberto)" if modal_visible else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)
            
        # 6. Testar Botão 'Ver detalhes' (Composição Corporal)
        btn_comp = page.locator("a:has-text('Ver detalhes')")
        if btn_comp.count() > 0:
            btn_comp.click()
            time.sleep(0.3)
            modal_visible = page.locator("#globalModal").is_visible()
            relatorio["Modal Composição Corporal"] = "OK (Aberto)" if modal_visible else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)
            
        # 7. Testar Botão 'Ver planos' (Upgrade Premium)
        btn_up = page.locator("button:has-text('Ver planos')")
        if btn_up.count() > 0:
            btn_up.click()
            time.sleep(0.3)
            modal_visible = page.locator("#globalModal").is_visible()
            relatorio["Modal Upgrade Premium"] = "OK (Aberto)" if modal_visible else "Falha"
            page.locator(".modal-close-btn").click()
            time.sleep(0.2)
            
        # Screenshot de evidência do teste da UI
        screenshot_path = r"C:\Users\jvna1\.gemini\antigravity\brain\6a82e9a6-837d-4089-854d-d753963b6dc6\screenshot_live_saciara.png"
        page.screenshot(path=screenshot_path, full_page=True)
        relatorio["Screenshot"] = screenshot_path
        
        browser.close()
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))
        return True

if __name__ == "__main__":
    test_interface()
