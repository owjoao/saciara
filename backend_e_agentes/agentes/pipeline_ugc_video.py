"""Pipeline de Captação e Mineração de Vídeos UGC com Gatekeeper Visual para Stories do @saciara_.
Executa o protocolo:
  [PRODUTO SHOPEE -> FOTO DE REFERÊNCIA -> BUSCA VÍDEOS DE USO -> AUDITORIA GATEKEEPER -> RENDER 9:16 -> STORY]
"""
from __future__ import annotations

import json
import logging
import os
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
ARM_DIR = Path("F:/Nova pasta/instagram-agent-arm")

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ARM_DIR) not in sys.path:
    sys.path.insert(0, str(ARM_DIR))

# Carrega .env
env_file = ROOT_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

from afiliados_shopee import AgenteAfiliadosShopeeFitness
from .revisor_visual import AgenteRevisorVisual
from .hunter_faceless import HunterFacelessAgent
from .memoria_manager import MemoriaSaciaraManager
from .roteiros_ugc import VARIASCOES_UGC_SACIARA, VariacaoPostStoryVideo

logger = logging.getLogger(__name__)


class PipelineUGCVideoStories:
    def __init__(self):
        self.shopee = AgenteAfiliadosShopeeFitness()
        self.revisor = AgenteRevisorVisual()
        self.hunter = HunterFacelessAgent()
        self.memoria = MemoriaSaciaraManager()
        self.tmp_dir = ROOT_DIR / "temp" / "ugc_stories"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def renderizar_video_story_com_overlay(
        self,
        video_input: Path,
        output_path: Path,
        frase_topo: str,
        duracao_max: int = 15
    ) -> Path:
        """Renderiza o vídeo faceless aprovado em 9:16 com faixa sutil de curiosidade no topo."""
        from PIL import Image, ImageDraw, ImageFont

        output_path.parent.mkdir(parents=True, exist_ok=True)
        overlay_path = output_path.parent / f"_overlay_{output_path.stem}.png"

        # Gera overlay transparente com Pillow (sem dependência de fontconfig)
        overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle([60, 180, 1020, 310], radius=30, fill=(0, 0, 0, 160))

        font = None
        font_candidates = ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf", "arial.ttf"]
        for fc in font_candidates:
            if Path(fc).exists():
                try:
                    font = ImageFont.truetype(fc, 44)
                    break
                except Exception:
                    pass

        draw.text((540, 245), frase_topo, font=font, fill=(255, 255, 255), anchor="mm")
        overlay.save(overlay_path)

        # Filtro de Renderização de Alta Definição:
        # Se o vídeo for horizontal, faz SMART CROP centralizado em vez de barras borradas,
        # OU se for vertical, escala mantendo a proporção nativa limpa em 1080x1920.
        # Proibido colocar vídeo esticado pequeno no meio com barras borradas.
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[base];"
            "[base][1:v]overlay=0:0[outv]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_input),
            "-i", str(overlay_path),
            "-t", str(duracao_max),
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "128k",
            str(output_path)
        ]

        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=flags)
        overlay_path.unlink(missing_ok=True)
        return output_path

    def processar_variacao_ugc(
        self,
        variacao_id: int = 1,
        simular: bool = True
    ) -> Dict[str, Any]:
        """Executa o ciclo completo para uma das 10 variações UGC."""
        var = next((v for v in VARIASCOES_UGC_SACIARA if v.id == variacao_id), VARIASCOES_UGC_SACIARA[0])

        print("\n" + "=" * 70)
        print(f" 🎬 PROCESSANDO VARIAÇÃO UGC #{var.id}: {var.produto_foco}")
        print(f" 🎯 Ângulo Psicológico: {var.angulo_psicologico}")
        print(f" 🗣️ Tom Conversacional: '{var.frase_topo_story}'")
        print("=" * 70)

        # 1. Garimpo Shopee e Foto de Referência
        print("\n[1/5] Conectando à Shopee e gerando link oficial rastreado...")
        achados = self.shopee.buscar_achados(var.produto_foco, limit=1)
        if not achados:
            print("  ⚠️ Produto não encontrado no catálogo. Usando busca ampla.")
            achados = self.shopee.buscar_achados("cozinha", limit=1)

        prod = achados[0]
        link_dados = self.shopee.gerar_link_rastreado(
            prod.offer_link or prod.product_link,
            canal="saciara",
            formato="ugcstory"
        )
        link_oficial = link_dados["link_afiliado"]
        print(f"  • Produto: {prod.name[:50]}...")
        print(f"  • Link Shopee Oficial: {link_oficial}")

        # Baixa foto oficial do anúncio para a auditoria de veracidade
        import urllib.request
        foto_ref = self.tmp_dir / f"ref_{prod.item_id}.jpg"
        if prod.image_url and not foto_ref.exists():
            try:
                with urllib.request.urlopen(prod.image_url, timeout=10) as r:
                    foto_ref.write_bytes(r.read())
                print(f"  • Foto oficial de referência baixada: {foto_ref.name}")
            except Exception as e:
                print(f"  ⚠️ Aviso ao baixar foto de referência: {e}")

        # 2. Mineração de Vídeos no YouTube Shorts
        print(f"\n[2/5] Minerando vídeos de demonstração real: '{var.termo_busca_video}'...")
        candidatos = self.hunter.buscar_videos_candidatos(var.termo_busca_video, limite=4)
        if not candidatos:
            print("  ⚠️ Nenhum candidato encontrado para o termo exato. Tentando variante curta...")
            candidatos = self.hunter.buscar_videos_candidatos(f"{var.produto_foco} shorts", limite=3)

        # 3. Auditoria pelo Gatekeeper Visual (Tolerância Zero para Rostos / Lojas)
        print("\n[3/5] Acionando Gatekeeper Visual (Auditoria de 4 frames)...")
        video_aprovado: Optional[Path] = None
        laudo_aprovado: Optional[Dict[str, Any]] = None

        for c in candidatos:
            print(f"  📥 Baixando candidato: {c['titulo'][:45]}...")
            try:
                raw_v = self.hunter.baixar_video(c["url"], c["id"])
                aprovado, laudo = self.revisor.auditar_video_candidato(
                    video_path=raw_v,
                    nome_produto=var.produto_foco,
                    imagem_referencia_shopee=foto_ref if foto_ref.exists() else None
                )

                if aprovado:
                    print(f"  ✅ APROVADO PELO GATEKEEPER VISUAL!")
                    print(f"     Motivo: {laudo.get('motivo_detalhado') or laudo.get('motivo')}")
                    video_aprovado = raw_v
                    laudo_aprovado = laudo
                    break
                else:
                    print(f"  ❌ REPROVADO PELO GATEKEEPER:")
                    print(f"     Motivo: {laudo.get('motivo_detalhado') or laudo.get('motivo')}")
                    raw_v.unlink(missing_ok=True)
            except Exception as e:
                print(f"  ⚠️ Erro ao auditar candidato: {e}")
                continue

        if not video_aprovado:
            print("\n  🛑 Nenhum candidato atendeu 100% aos critérios do Gatekeeper.")
            print("  👉 Regra de Ouro ativada: Não improvisar cortes estranhos; descartar lote.")
            return {"status": "DESCARTE_GATEKEEPER", "motivo": "Nenhum vídeo 100% faceless aprovado"}

        # 4. Renderização 9:16 Vertical com Frase de Amigo
        print("\n[4/5] Renderizando vídeo 9:16 com overlay conversacional...")
        story_pronto = self.tmp_dir / f"story_ugc_final_{var.id}.mp4"
        self.renderizar_video_story_com_overlay(
            video_input=video_aprovado,
            output_path=story_pronto,
            frase_topo=var.frase_topo_story,
            duracao_max=15
        )
        print(f"  🎬 Vídeo de Story 9:16 Finalizado: {story_pronto.name}")

        # 5. Publicação ou Simulação
        if simular:
            print("\n[5/5] MODO SIMULAÇÃO (Sem disparo ao vivo):")
            print(f"  • Vídeo Pronto:    {story_pronto}")
            print(f"  • Link do Sticker: {link_oficial}")
            print(f"  • Texto Sticker:   {var.texto_sticker}")
            print(f"  • Posição:         Thumb Zone (Y=82.7%, X=50%)")
            return {
                "status": "SIMULADO_OK",
                "variacao_id": var.id,
                "video": str(story_pronto),
                "link": link_oficial,
                "texto_sticker": var.texto_sticker
            }

        # Disparo ao vivo para o @saciara_
        print("\n[5/5] Enviando Story em Vídeo com Sticker na Thumb Zone para o @saciara_...")
        from core.client import InstagramPublisher
        from core.session import load_session

        sess = load_session()
        pub = InstagramPublisher(sess["sessionid"], sess["csrftoken"], sess.get("ds_user_id", ""))

        resultado_post = pub.post_story_video(
            video_path=str(story_pronto),
            cover_image_path=str(foto_ref) if foto_ref.exists() else None,
            link_url=link_oficial,
            sticker_text=var.texto_sticker,
            sticker_x=0.5,
            sticker_y=0.8267
        )

        if resultado_post.get("success"):
            print("  ✅ STORY EM VÍDEO PUBLICADO COM SUCESSO NO @saciara_!")
            self.memoria.registrar_story_publicado({
                "produto": var.produto_foco,
                "variacao_id": var.id,
                "link_afiliado": link_oficial,
                "texto_sticker": var.texto_sticker,
                "tipo_midia": "video_ugc_faceless"
            })
            return {"status": "SUCESSO", "media_id": resultado_post.get("media_id")}
        else:
            print(f"  ❌ Falha no upload: {resultado_post.get('error')}")
            return {"status": "ERRO", "erro": resultado_post.get("error")}
