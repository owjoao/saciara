"""Gerador Visual de Stories 1080x1920 (9:16) - Estratégia de Ativação de Cookies Shopee (30 Dias).
FOCO EXCLUSIVO: GERAÇÃO DE CURIOSIDADE E CLIQUE (ZERO APELO DE VENDA DIRETA).
A meta é fazer a pessoa tocar no sticker para ver o achado, ativando a comissão de 30 dias.
"""
from __future__ import annotations

import base64
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT_DIR = Path(__file__).resolve().parent.parent
ARM_DIR = Path("F:/Nova pasta/instagram-agent-arm")

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ARM_DIR) not in sys.path:
    sys.path.insert(0, str(ARM_DIR))

from core.media import burn_link_sticker_to_image


def criar_story_curiosidade_editorial(
    produto_img_path: Path,
    output_path: Path,
    gancho_curiosidade: str = "Quem me perguntou onde achei isso...",
    beneficio_pratico: str = "Salvou meus preparos da semana sem fazer sujeira",
    tag_topo: str = "ACHADINHO DE ROTINA",
    texto_sticker: str = "ONDE COMPREI",
    link_url: str = "https://s.shopee.com.br/50aQ9uF7fX"
) -> Path:
    """Gera Story 1080x1920 focado em curiosidade e compartilhamento de utilidade (sem preços)."""
    w, h = 1080, 1920
    # Fundo creme aconchegante da marca (#FBF8F3)
    story = Image.new("RGB", (w, h), color=(251, 248, 243))
    draw = ImageDraw.Draw(story)

    # 1. Topo: Logo Saciara em harmonia
    logo_path = ROOT_DIR / "assets" / "logo_saciara.png"
    if logo_path.exists():
        with Image.open(logo_path) as logo:
            logo_resized = logo.convert("RGBA").resize((150, 150))
            story.paste(logo_resized, (int(w/2 - 75), 110), logo_resized)

    # 2. Badge Editorial Superior (curiosidade, não propaganda)
    draw.text((w/2, 290), f"• {tag_topo} •", fill=(45, 76, 58), anchor="mm")

    # 3. Card Flutuante com o Produto
    card_w, card_h = 880, 880
    card_x, card_y = int((w - card_w) / 2), 340

    # Sombra suave orgânica
    shadow = Image.new("RGBA", (card_w + 40, card_h + 40), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle([20, 20, card_w + 20, card_h + 20], radius=45, fill=(0, 0, 0, 28))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    story.paste(shadow, (card_x - 20, card_y - 20), shadow)

    # Fundo branco do card do produto
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=45, fill=(255, 255, 255))

    # Imagem do Produto no Card
    if produto_img_path.exists():
        with Image.open(produto_img_path) as prod_im:
            prod_im = prod_im.convert("RGBA")
            prod_im.thumbnail((card_w - 90, card_h - 90))
            px = int(card_x + (card_w - prod_im.width) / 2)
            py = int(card_y + (card_h - prod_im.height) / 2)
            story.paste(prod_im, (px, py), prod_im)

    # Selo de Curiosidade no Canto do Card (Substitui Preço por Gatilho)
    selo_w, selo_h = 290, 65
    selo_x, selo_y = card_x + card_w - selo_w - 30, card_y + 30
    draw.rounded_rectangle([selo_x, selo_y, selo_x + selo_w, selo_y + selo_h], radius=22, fill=(226, 131, 89))
    draw.text((selo_x + selo_w/2, selo_y + selo_h/2), "TESTEI E APROVEI ✓", fill=(255, 255, 255), anchor="mm")

    # 4. Textos de Curiosidade (Conversa informal, tom pessoal e prestativo)
    draw.text((w/2, 1290), gancho_curiosidade, fill=(30, 45, 36), anchor="mm")
    draw.text((w/2, 1360), beneficio_pratico, fill=(100, 110, 105), anchor="mm")

    # Convite para tocar no sticker
    draw.text((w/2, 1460), "Deixei o link de onde achei aqui 👇", fill=(226, 131, 89), anchor="mm")

    temp_base = output_path.parent / f"_temp_base_{output_path.name}"
    story.save(temp_base, quality=95)

    if link_url:
        # Queima o sticker na Thumb Zone (Y=82.7%)
        burn_link_sticker_to_image(
            image_path=str(temp_base),
            output_path=str(output_path),
            link_url=link_url,
            custom_text=texto_sticker,
            sticker_style="sunset",
            align="center",
            x_pct=0.5,
            y_pct=0.8267
        )
        temp_base.unlink(missing_ok=True)
    else:
        story.save(output_path, quality=95)
        temp_base.unlink(missing_ok=True)

    return output_path


def criar_story_faceless_curiosidade(
    frame_path: Path,
    output_path: Path,
    texto_topo: str = "Olha a facilidade disso aqui...",
    link_url: str = "https://s.shopee.com.br/50aQ9uF7fX",
    texto_sticker: str = "ONDE COMPREI"
) -> Path:
    """Gera Story com vídeo/frame faceless com legenda de curiosidade e sticker de clique."""
    with Image.open(frame_path) as im:
        w, h = im.size
        story = im.convert("RGB")
        draw = ImageDraw.Draw(story)

        # Barra sutil no topo para destacar a frase
        bar_h = 160
        overlay = Image.new("RGBA", (w, bar_h), (0, 0, 0, 140))
        story.paste(overlay, (0, 180), overlay)

        draw.text((w/2, 260), texto_topo, fill=(255, 255, 255), anchor="mm")
        draw.text((w/2, 1460), "Toque para ver o produto 👇", fill=(255, 255, 255), anchor="mm")

        temp_base = output_path.parent / f"_temp_faceless_{output_path.name}"
        story.save(temp_base, quality=95)

        burn_link_sticker_to_image(
            image_path=str(temp_base),
            output_path=str(output_path),
            link_url=link_url,
            custom_text=texto_sticker,
            sticker_style="sunset",
            align="center",
            x_pct=0.5,
            y_pct=0.8267
        )
        temp_base.unlink(missing_ok=True)
        return output_path


def gerar_mockup_celular(
    story_image_path: Path,
    output_mockup_path: Path,
    username: str = "saciara_"
) -> Path:
    """Gera visualização realista de smartphone com a interface do Instagram Stories."""
    with Image.open(story_image_path) as story_img:
        mock_w, mock_h = 1240, 2200
        canvas = Image.new("RGB", (mock_w, mock_h), color=(240, 242, 245))
        draw = ImageDraw.Draw(canvas)

        phone_x, phone_y = 80, 140
        phone_w, phone_h = 1080, 1920
        border = 20

        draw.rounded_rectangle(
            [phone_x - border, phone_y - border, phone_x + phone_w + border, phone_y + phone_h + border],
            radius=65, fill=(25, 25, 28)
        )

        canvas.paste(story_img, (phone_x, phone_y))

        # Interface do Instagram Stories:
        prog_y = phone_y + 25
        draw.rounded_rectangle([phone_x + 30, prog_y, phone_x + phone_w - 30, prog_y + 4], radius=2, fill=(255, 255, 255, 180))

        logo_path = ROOT_DIR / "assets" / "logo_saciara.png"
        if logo_path.exists():
            with Image.open(logo_path) as logo:
                avatar = logo.convert("RGBA").resize((60, 60))
                mask = Image.new("L", (60, 60), 0)
                m_draw = ImageDraw.Draw(mask)
                m_draw.ellipse([0, 0, 60, 60], fill=255)
                canvas.paste(avatar, (phone_x + 35, phone_y + 45), mask)

        draw.text((phone_x + 110, phone_y + 75), f"@{username}", fill=(255, 255, 255), anchor="lm")
        draw.text((phone_x + 230, phone_y + 75), "• 1 h", fill=(200, 200, 200), anchor="lm")
        draw.text((phone_x + phone_w - 50, phone_y + 75), "✕", fill=(255, 255, 255), anchor="mm")

        bar_y = phone_y + phone_h - 90
        bar_w = phone_w - 180
        draw.rounded_rectangle([phone_x + 30, bar_y, phone_x + 30 + bar_w, bar_y + 60], radius=30, outline=(255, 255, 255, 160), width=2)
        draw.text((phone_x + 60, bar_y + 30), "Enviar mensagem...", fill=(200, 200, 200), anchor="lm")

        draw.text((phone_x + phone_w - 110, bar_y + 30), "♡", fill=(255, 255, 255), anchor="mm")
        draw.text((phone_x + phone_w - 50, bar_y + 30), "✈", fill=(255, 255, 255), anchor="mm")

        draw.text((mock_w/2, 2120), "ESTRATÉGIA DE CLIQUE • ATIVAÇÃO DE COOKIE 30 DIAS", fill=(80, 90, 100), anchor="mm")

        canvas.save(output_mockup_path, quality=95)
        return output_mockup_path
