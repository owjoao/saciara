"""Teste Automatizado End-to-End via Playwright (Mobile Viewport 390x844).
Valida os novos recursos móveis:
- Bottom Navigation Dock (Thumb Zone)
- Barra de Ações Rápidas (Quick Actions Bar)
- Modal com Stepper de Registro de Peso
- Menu Hambúrguer e Backdrop
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

CAMINHO_HTML = Path("F:/Nova pasta/site/saciara/index.html").resolve()


async def rodar_teste_mobile():
    resultados = {}
    async with async_playwright() as p:
        # Emula iPhone 12/13/14 (390 x 844)
        browser = await p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()
        await page.goto(f"file:///{CAMINHO_HTML}")
        await page.wait_for_timeout(600)

        # 1. Validar Visibilidade do Bottom Dock
        dock = page.locator("#mobileBottomDock")
        resultados["Bottom Dock Visível no Celular"] = await dock.is_visible()

        # 2. Validar Itens do Dock
        dock_items = await page.locator(".dock-item").count()
        resultados["Total de Itens no Dock"] = dock_items

        # 3. Validar Quick Actions Bar
        quick_bar = page.locator(".quick-actions-bar")
        resultados["Quick Actions Bar Visível"] = await quick_bar.is_visible()

        # 4. Testar Clique no Botão de Registrar Peso Rápido
        btn_peso = page.locator(".btn-peso")
        await btn_peso.click()
        await page.wait_for_timeout(300)
        
        modal_peso = page.locator("#globalModal")
        modal_aberto = await modal_peso.is_visible()
        resultados["Modal de Peso Abre com 1 Toque"] = modal_aberto

        # 5. Testar Stepper do Modal (+0.1kg)
        btn_mais = page.locator("button:has-text('+')")
        if await btn_mais.count():
            await btn_mais.first.click()
            await page.wait_for_timeout(100)
            display_peso = await page.locator("#displayPesoInput").inner_text()
            resultados["Stepper de Peso Funcional"] = display_peso

        # Fechar Modal
        btn_close = page.locator(".modal-close-btn")
        await btn_close.click()
        await page.wait_for_timeout(200)

        # 6. Testar Botão Hambúrguer Mobile
        btn_menu = page.locator(".mobile-menu-toggle")
        await btn_menu.click()
        await page.wait_for_timeout(300)
        
        sidebar = page.locator(".sidebar")
        classes_sidebar = await sidebar.get_attribute("class")
        resultados["Menu Hambúrguer Abre Sidebar"] = "open" in classes_sidebar

        # Fechar pelo backdrop
        backdrop = page.locator("#sidebarBackdrop")
        await backdrop.click(force=True)
        await page.wait_for_timeout(300)
        classes_pos_close = await sidebar.get_attribute("class")
        resultados["Backdrop Fecha Sidebar"] = "open" not in classes_pos_close

        # 7. Testar Navegação pelo Bottom Dock (Troca para Compras/Mercado)
        dock_mercado = page.locator("button[data-dock='compras']")
        await dock_mercado.click()
        await page.wait_for_timeout(400)
        view_compras = page.locator("#view-compras")
        resultados["Navegação para Compras via Dock"] = "active" in await view_compras.get_attribute("class")

        await browser.close()

    print(json.dumps(resultados, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(rodar_teste_mobile())
