"""Renderizador de Alta Resolução de Stories (1080x1920) via Playwright + HTML5/CSS3.
Garante tipografia profissional (Inter / Plus Jakarta Sans), proporções perfeitas,
sombras orgânicas e fidelidade visual absoluta ao anúncio da Shopee.
"""
from __future__ import annotations

import base64
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
ARM_DIR = Path("F:/Nova pasta/instagram-agent-arm")

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ARM_DIR) not in sys.path:
    sys.path.insert(0, str(ARM_DIR))

from core.media import STICKER_STYLES


def renderizar_story_premium(
    produto_img_path: Path,
    output_path: Path,
    gancho_principal: str = "Quem me perguntou onde achei isso...",
    detalhe_utilidade: str = "Pesa direto no prato e não ocupa espaço na bancada",
    nome_produto_real: str = "Balança Digital de Precisão SF-400",
    badge_topo: str = "ACHADINHO DE ROTINA",
    texto_sticker: str = "ONDE COMPREI",
    link_url: str = "https://s.shopee.com.br/50aQ9uF7fX",
    incluir_sticker: bool = True
) -> Path:
    """Renderiza um Story 1080x1920 com padrão de agência profissional e tipografia vetorial nítida."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Converte imagens para base64
    with open(produto_img_path, "rb") as f:
        prod_b64 = base64.b64encode(f.read()).decode("utf-8")

    logo_path = ROOT_DIR / "assets" / "logo_saciara.png"
    logo_b64 = ""
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Configuração do sticker
    style_cfg = STICKER_STYLES.get("sunset", STICKER_STYLES["default"])

    sticker_html = ""
    if incluir_sticker:
        sticker_html = f"""
        <div class="sticker-thumb-zone">
            <div class="sticker-link">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.7076 18.3639L11.2933 19.7781C9.34072 21.7308 6.1749 21.7308 4.22228 19.7781C2.26966 17.8255 2.26966 14.6597 4.22228 12.7071L5.63649 11.2929M18.3644 12.7071L19.7786 11.2929C21.7312 9.34024 21.7312 6.17441 19.7786 4.22179C17.826 2.26917 14.6602 2.26917 12.7076 4.22179L11.2933 5.636M8.50045 15.4999L15.5005 8.49994"
                          stroke="{style_cfg['icon_color']}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>{texto_sticker}</span>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-font-smoothing: antialiased;
  }}

  body {{
    width: 1080px;
    height: 1920px;
    background-color: #FBF8F3;
    background-image: 
      radial-gradient(at 0% 0%, rgba(226, 131, 89, 0.08) 0px, transparent 50%),
      radial-gradient(at 100% 100%, rgba(45, 76, 58, 0.08) 0px, transparent 50%);
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}

  /* Safe zone superior */
  .header {{
    width: 100%;
    margin-top: 130px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }}

  .logo-box {{
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: #FFFFFF;
    box-shadow: 0 10px 25px rgba(45, 76, 58, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12px;
  }}

  .logo-box img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
  }}

  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 24px;
    border-radius: 9999px;
    background: rgba(45, 76, 58, 0.08);
    color: #2D4C3A;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }}

  /* Card Central do Produto */
  .card-container {{
    width: 880px;
    height: 880px;
    margin-top: 45px;
    background: #FFFFFF;
    border-radius: 52px;
    box-shadow: 
      0 30px 60px rgba(45, 76, 58, 0.08),
      0 12px 24px rgba(0, 0, 0, 0.04);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
    border: 1px solid rgba(0, 0, 0, 0.03);
  }}

  .card-container img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    filter: drop-shadow(0 15px 30px rgba(0, 0, 0, 0.09));
  }}

  .stamp-tag {{
    position: absolute;
    top: 35px;
    right: 35px;
    background: #E28359;
    color: #FFFFFF;
    padding: 14px 28px;
    border-radius: 20px;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 0.5px;
    box-shadow: 0 8px 20px rgba(226, 131, 89, 0.35);
  }}

  /* Seção de Texto & Ganchos */
  .copy-section {{
    width: 900px;
    margin-top: 55px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }}

  .main-hook {{
    font-family: 'Outfit', sans-serif;
    font-size: 52px;
    font-weight: 800;
    color: #1E2D24;
    line-height: 1.22;
    letter-spacing: -0.5px;
  }}

  .product-real-name {{
    font-size: 30px;
    font-weight: 700;
    color: #2D4C3A;
    background: rgba(45, 76, 58, 0.08);
    padding: 6px 20px;
    border-radius: 12px;
    display: inline-block;
  }}

  .sub-benefit {{
    font-size: 32px;
    font-weight: 500;
    color: #5A6960;
    line-height: 1.35;
    max-width: 820px;
  }}

  .cta-helper {{
    margin-top: 14px;
    font-size: 30px;
    font-weight: 700;
    color: #E28359;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  /* Thumb Zone Canônica (Y=82.7%, X=50%) */
  .sticker-thumb-zone {{
    position: absolute;
    top: 1587px; /* 1920 * 0.8267 = 1587px */
    left: 50%;
    transform: translate(-50%, -50%);
    width: 609px; /* 1080 * 0.5639 = 609px */
    height: 142px; /* 1920 * 0.0739 = 142px */
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .sticker-link {{
    width: 100%;
    height: 100%;
    background: {style_cfg['bg']};
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    box-shadow: {style_cfg['shadow']};
    user-select: none;
  }}

  .sticker-link svg {{
    width: 58px;
    height: 58px;
    display: block;
  }}

  .sticker-link span {{
    color: {style_cfg['color']};
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
  }}
</style>
</head>
<body>

  <!-- Topo Branded -->
  <div class="header">
    <div class="logo-box">
      <img src="data:image/png;base64,{logo_b64}" alt="Saciara Logo" />
    </div>
    <div class="badge">
      <span>{badge_topo}</span>
    </div>
  </div>

  <!-- Card do Produto Oficial Shopee -->
  <div class="card-container">
    <div class="stamp-tag">TESTEI E APROVEI ✓</div>
    <img src="data:image/jpeg;base64,{prod_b64}" alt="{nome_produto_real}" />
  </div>

  <!-- Textos de Curiosidade e Utilidade -->
  <div class="copy-section">
    <div class="main-hook">{gancho_principal}</div>
    <div class="product-real-name">{nome_produto_real}</div>
    <div class="sub-benefit">{detalhe_utilidade}</div>
    <div class="cta-helper">Toque abaixo para ver de onde é 👇</div>
  </div>

  <!-- Sticker Oficial na Thumb Zone -->
  {sticker_html}

</body>
</html>
"""

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page.set_content(html)
        page.wait_for_timeout(500)
        page.screenshot(path=str(output_path), quality=95, type="jpeg")
        browser.close()

    return output_path
