"""Pipeline Automatizado de Stories com Afiliados Shopee para o @saciara_.
Fluxo Canônico:
  1. Produto Shopee Selecionado -> Link Oficial Rastreado Gerado
  2. Imagem Oficial em Alta Definição Baixada
  3. Mineração de Vídeo Faceless (POV / Mãos) no YT Shorts / TikTok
  4. Auditoria IA (Garantia de ausência total de rostos)
  5. Renderização 9:16 Vertical (1080x1920)
  6. Publicação no Story do @saciara_ com Sticker de Link na Thumb Zone
  7. Persistência no Cofre de Memória Fechado (memoria_saciara.json)
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

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

AGENTES_DIR = Path(__file__).resolve().parent
if str(AGENTES_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTES_DIR))

from afiliados_shopee import AgenteAfiliadosShopeeFitness
try:
    from .hunter_faceless import HunterFacelessAgent
    from .memoria_manager import MemoriaSaciaraManager
except ImportError:
    from hunter_faceless import HunterFacelessAgent
    from memoria_manager import MemoriaSaciaraManager


class PipelineStoriesAfiliados:
    def __init__(self):
        self.shopee_agent = AgenteAfiliadosShopeeFitness()
        self.hunter_faceless = HunterFacelessAgent()
        self.memoria = MemoriaSaciaraManager()
        self.tmp_dir = ROOT_DIR / "temp" / "stories_pipeline"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def _obter_instagram_publisher(self):
        from core.session import load_session
        from core.client import InstagramPublisher
        sess = load_session()
        if not sess:
            sess = {
                "sessionid": os.getenv("INSTAGRAM_SESSION_ID"),
                "csrftoken": os.getenv("INSTAGRAM_CSRF_TOKEN"),
                "ds_user_id": os.getenv("INSTAGRAM_USER_ID", "73335883756")
            }
        return InstagramPublisher(sess["sessionid"], sess["csrftoken"], sess.get("ds_user_id", ""))

    def baixar_imagem_produto(self, image_url: str, item_id: str) -> Optional[Path]:
        """Baixa a imagem oficial do produto para uso como thumbnail ou story estático."""
        if not image_url:
            return None
        dest = self.tmp_dir / f"shopee_prod_{item_id}.jpg"
        try:
            req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                dest.write_bytes(resp.read())
            return dest
        except Exception as e:
            print(f"  ⚠️ Aviso ao baixar imagem do produto: {e}")
            return None

    def executar(
        self,
        termo_ou_url: str,
        texto_sticker: str = "ONDE COMPREI",
        estilo_sticker: str = "sunset",
        publicar_agora: bool = True
    ) -> Dict[str, Any]:
        """Executa a esteira ponta a ponta."""
        print("\n" + "=" * 65)
        print(" 🚀 PIPELINE DE STORIES SACIARA: DA SHOPEE AO CLIQUE NO LINK")
        print("=" * 65)

        # -------------------------------------------------------------
        # ETAPA 1: Identificação do Produto e Link Oficial Rastreado
        # -------------------------------------------------------------
        print("\n[ETAPA 1/5] Selecionando produto e gerando link oficial de afiliado...")
        produto_info = None

        if "shopee.com" in termo_ou_url:
            dados_link = self.shopee_agent.gerar_link_rastreado(termo_ou_url, canal="saciara", formato="stories")
            nome_busca = dados_link.get("produto_nome") or "produto shopee"
            link_afiliado = dados_link["link_afiliado"]
            item_id = "shopee_link"
            img_url = dados_link.get("imagem")
        else:
            achados = self.shopee_agent.buscar_achados(termo_ou_url, limit=1)
            if not achados:
                raise RuntimeError(f"Nenhum produto Shopee encontrado para: '{termo_ou_url}'")
            p = achados[0]
            dados_link = self.shopee_agent.gerar_link_rastreado(
                p.offer_link or p.product_link, canal="saciara", formato="stories"
            )
            nome_busca = p.name
            link_afiliado = dados_link["link_afiliado"]
            item_id = p.item_id
            img_url = p.image_url
            produto_info = {
                "item_id": p.item_id,
                "nome": p.name,
                "preco": p.price_min,
                "comissao": p.commission,
                "link_afiliado": link_afiliado
            }
            self.memoria.registrar_produto(produto_info)

        print(f"  • Produto: {nome_busca[:55]}")
        print(f"  • Link Shopee Oficial: {link_afiliado}")

        # -------------------------------------------------------------
        # ETAPA 2: Obter Imagem Oficial do Produto
        # -------------------------------------------------------------
        print("\n[ETAPA 2/5] Baixando imagem oficial do catálogo Shopee...")
        imagem_local = self.baixar_imagem_produto(img_url, item_id) if img_url else None
        if imagem_local:
            print(f"  • Imagem do produto salva: {imagem_local.name}")

        # -------------------------------------------------------------
        # ETAPA 3 & 4: Minerar Vídeo Faceless (Sem Rosto / Mãos em Ação)
        # -------------------------------------------------------------
        print("\n[ETAPA 3/5] Minerando vídeo de demonstração faceless (estilo POV/mãos)...")
        # Simplifica o termo para busca (remove termos de SEO longos)
        palavras_chave = " ".join([w for w in nome_busca.split()[:4] if len(w) > 2])
        video_story_path = self.hunter_faceless.minerar_video_faceless_completo(palavras_chave)

        # -------------------------------------------------------------
        # ETAPA 5: Publicação no Story do @saciara_ com Sticker Interativo
        # -------------------------------------------------------------
        print("\n[ETAPA 4/5] Preparando mídia vertical 9:16 para os Stories...")

        if not publicar_agora:
            print("  🛑 Modo simulação (publicar_agora=False). Story pronto para envio:")
            print(f"     Vídeo: {video_story_path}")
            print(f"     Link:  {link_afiliado}")
            return {
                "status": "SIMULADO_OK",
                "produto": nome_busca,
                "link": link_afiliado,
                "video": str(video_story_path) if video_story_path else None
            }

        print("\n[ETAPA 5/5] Enviando Story com Sticker Interativo na Thumb Zone para o @saciara_...")
        pub = self._obter_instagram_publisher()

        resultado_post = None
        if video_story_path and video_story_path.exists():
            resultado_post = pub.post_story_video(
                video_path=str(video_story_path),
                cover_image_path=str(imagem_local) if imagem_local else None,
                link_url=link_afiliado,
                sticker_text=texto_sticker,
                sticker_x=0.5,
                sticker_y=0.827  # Thumb zone canônica (82.7%)
            )
        elif imagem_local and imagem_local.exists():
            # Fallback seguro: se não achar vídeo faceless confiável, posta foto 9:16 com sticker queimado
            resultado_post = pub.post_story_photo(
                image_path=str(imagem_local),
                link_url=link_afiliado,
                sticker_text=texto_sticker,
                sticker_style=estilo_sticker,
                align="center",
                sticker_x=0.5,
                sticker_y=0.827
            )
        else:
            raise RuntimeError("Não foi possível obter mídia (vídeo ou imagem) para compor o Story.")

        # Persistência na memória fechada
        if resultado_post and resultado_post.get("success"):
            print("\n" + "=" * 65)
            print(" ✅ STORY PUBLICADO COM SUCESSO NO INSTAGRAM!")
            print(f"   • Conta:            @saciara_")
            print(f"   • Produto Vinculado: {nome_busca[:50]}")
            print(f"   • Link do Sticker:   {link_afiliado}")
            print(f"   • Posição Sticker:   Thumb Zone (X=50%, Y=82.7%)")
            print("=" * 65 + "\n")

            self.memoria.registrar_story_publicado({
                "produto": nome_busca,
                "link_afiliado": link_afiliado,
                "tipo_midia": "video_faceless" if video_story_path else "imagem",
                "texto_sticker": texto_sticker,
                "status": "publicado"
            })
            return {"status": "SUCESSO", "link": link_afiliado, "produto": nome_busca}
        else:
            erro = resultado_post.get("error") if resultado_post else "Resposta nula"
            print(f"\n❌ Erro ao enviar Story: {erro}")
            return {"status": "ERRO", "erro": erro}


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Stories Shopee - Saciara Fitness")
    parser.add_argument("--produto", type=str, required=True, help="Nome do produto fitness ou URL da Shopee")
    parser.add_argument("--texto-sticker", type=str, default="ONDE COMPREI", help="Texto do sticker (max 20 chars)")
    parser.add_argument("--simular", action="store_true", help="Gera link e vídeo faceless sem postar no Instagram")
    args = parser.parse_args()

    pipeline = PipelineStoriesAfiliados()
    pipeline.executar(
        termo_ou_url=args.produto,
        texto_sticker=args.texto_sticker,
        publicar_agora=not args.simular
    )


if __name__ == "__main__":
    main()
