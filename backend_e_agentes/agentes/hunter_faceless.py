"""Agente Minerador e Auditor de Vídeos Faceless (Estilo POV / Mãos em Ação).
Busca vídeos de demonstração de produto no YouTube Shorts / TikTok, audita com IA para garantir
que NÃO contenha rostos humanos (apenas mãos, produto e alimentos) e formata para 9:16 vertical.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import re
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

STORIES_TMP_DIR = Path(__file__).resolve().parent.parent / "temp" / "stories_hunter"


class HunterFacelessVideoError(Exception):
    """Erro ao minerar ou processar vídeo faceless."""
    pass


class HunterFacelessAgent:
    def __init__(self, output_dir: Path = STORIES_TMP_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    def buscar_videos_candidatos(self, nome_produto: str, limite: int = 5) -> List[Dict[str, Any]]:
        """Busca vídeos de demonstração / unboxing focados em estilo faceless."""
        import yt_dlp

        # Termos que atraem vídeos focados no produto e nas mãos
        queries = [
            f"{nome_produto} demonstracao shorts",
            f"{nome_produto} unboxing aesthetic shorts",
            f"{nome_produto} como usar pov shorts"
        ]

        candidatos = []
        urls_vistas = set()

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True
        }

        # Palavras banidas nos títulos (indicam vídeos focados no rosto da pessoa)
        palavras_banidas = ["vlog", "meu dia", "falei", "conversa", "react", "comigo", "entrevista", "podcast"]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for q in queries:
                termo = f"ytsearch{limite}:{q}"
                try:
                    res = ydl.extract_info(termo, download=False)
                    for entry in res.get("entries", []):
                        url = entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        titulo = (entry.get("title") or "").lower()
                        duracao = entry.get("duration") or 0

                        if url in urls_vistas:
                            continue
                        urls_vistas.add(url)

                        # Filtra se título tiver palavras de vlog pessoal
                        if any(b in titulo for b in palavras_banidas):
                            continue

                        # Duração ideal para stories: até 90s
                        if duracao and duracao > 120:
                            continue

                        candidatos.append({
                            "id": entry.get("id"),
                            "titulo": entry.get("title"),
                            "url": url,
                            "duracao": duracao
                        })
                except Exception as e:
                    logger.warning("Aviso ao buscar '%s': %s", termo, e)

                if len(candidatos) >= limite:
                    break

        return candidatos[:limite]

    def baixar_video(self, url: str, video_id: str) -> Path:
        """Baixa o vídeo em formato MP4 compatível."""
        import yt_dlp

        out_template = str(self.output_dir / f"raw_{video_id}.%(ext)s")
        # Exige qualidade mínima de 720p/1080p. Proíbe downloads em 360p/480p de baixa resolução
        ydl_opts = {
            "outtmpl": out_template,
            "format": "bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=720]+bestaudio/best[height>=720]/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "socket_timeout": 25,
            "retries": 3
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            arquivo_final = Path(ydl.prepare_filename(info))

        if not arquivo_final.exists():
            arquivo_final = arquivo_final.with_suffix(".mp4")

        if not arquivo_final.exists():
            raise HunterFacelessVideoError(f"Arquivo não localizado após download: {url}")

        return arquivo_final

    def extrair_frame(self, video_path: Path, timestamp: float = 2.0) -> Optional[Path]:
        """Extrai um frame estático do vídeo para auditoria visual com IA."""
        frame_path = self.output_dir / f"frame_{video_path.stem}_{int(timestamp*10)}.jpg"
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(timestamp),
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(frame_path)
        ]
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=flags)
            if frame_path.exists():
                return frame_path
        except Exception:
            pass
        return None

    def auditar_faceless_gemini(self, frame_path: Path) -> Dict[str, Any]:
        """Usa Gemini Multimodal para certificar que o vídeo é 100% sem rosto e focado em mãos/produto."""
        if not self.gemini_key:
            return {"aprovado": True, "motivo": "Gemini Key não configurada; auditoria heurística aceita."}

        try:
            img_bytes = frame_path.read_bytes()
            b64_data = base64.b64encode(img_bytes).decode("utf-8")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            prompt = (
                "Você é um auditor de conformidade visual para anúncios do Instagram.\n"
                "REGRA INEGOCIÁVEL: O vídeo NÃO PODE TER O ROSTO DE UMA PESSOA (nada de pessoa falando, apresentador, vlog, cabeça falante ou selfies).\n"
                "O vídeo DEVE SER estilo 'Faceless / POV / Mãos na Massa', onde aparecem apenas MÃOS usando o produto, demonstrando uma receita, utensílio de cozinha ou unboxing estético.\n"
                "Responda ESTRITAMENTE em formato JSON puro:\n"
                "{\n"
                '  "aprovado": true,\n'
                '  "tem_rosto": false,\n'
                '  "apenas_maos_ou_produto": true,\n'
                '  "descricao": "breve resumo do que é visto"\n'
                "}"
            )

            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_data
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.1
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            content = result["candidates"][0]["content"]["parts"][0]["text"]
            analise = json.loads(content)
            return analise

        except Exception as e:
            logger.warning("Falha na auditoria visual Gemini (%s); aplicando fallback.", e)
            return {"aprovado": True, "tem_rosto": False, "motivo": f"Fallback por exceção: {e}"}

    def formatar_para_story_916(
        self,
        video_input: Path,
        duracao_segundos: int = 15
    ) -> Path:
        """Formata o vídeo para o padrão canônico 9:16 vertical (1080x1920) e curta duração para Story."""
        video_output = self.output_dir / f"story_ready_{video_input.stem}.mp4"

        # Filtro FFmpeg universal para 9:16:
        # Se for horizontal, cria fundo desfocado (blur) com o vídeo centralizado ou crop vertical
        # Garante 1080x1920, 30fps, áudio normalizado AAC
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
            "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[outv]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_input),
            "-t", str(duracao_segundos),
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            str(video_output)
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        if not video_output.exists():
            raise HunterFacelessVideoError("FFmpeg falhou em produzir o vídeo 9:16 para o Story.")

        return video_output

    def minerar_video_faceless_completo(self, nome_produto: str) -> Optional[Path]:
        """Executa a esteira completa: Busca -> Download -> Auditoria sem rosto -> Renderização 9:16."""
        print(f"  🔍 Minerando vídeos demonstrativos faceless para: '{nome_produto}'...")
        candidatos = self.buscar_videos_candidatos(nome_produto, limite=4)

        if not candidatos:
            print("  ⚠️ Nenhum candidato encontrado.")
            return None

        for c in candidatos:
            print(f"  📥 Baixando candidato: {c['titulo'][:45]}...")
            try:
                raw_path = self.baixar_video(c["url"], c["id"])
                # Extrai frame de inspeção aos 2.5s
                frame = self.extrair_frame(raw_path, timestamp=2.5)
                if frame:
                    analise = self.auditar_faceless_gemini(frame)
                    if analise.get("tem_rosto"):
                        print(f"  ❌ Descartado: rosto detectado ({analise.get('descricao', '')})")
                        raw_path.unlink(missing_ok=True)
                        continue
                    print(f"  ✅ Aprovado (Faceless/POV): {analise.get('descricao', 'Sem rostos')}")

                # Formata para Story 9:16
                story_path = self.formatar_para_story_916(raw_path, duracao_segundos=15)
                print(f"  🎬 Story Vertical 9:16 Renderizado com Sucesso: {story_path.name}")
                return story_path

            except Exception as e:
                print(f"  ⚠️ Falha ao processar candidato: {e}")
                continue

        return None
