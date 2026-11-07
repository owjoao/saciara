"""Indexador e Gerenciador das 156 Receitas Oficiais do Ecossistema Saciara.
Extrai metadados, calcula perfis nutricionais por porção e mapeia os utensílios
recomendados (com links de afiliados oficiais rastreados).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTEUDO_DIR = ROOT_DIR / "conteudo-saciara"

# Mapeamento oficial de Utensílios Recomendados com links rastreados Shopee
UTENSILIOS_CATALOGO = {
    "balanca": {
        "nome": "Balança Digital de Precisão Culinária SF-400",
        "motivo": "Para acertar as gramas exatas de proteínas e fibras sem neura.",
        "link": "https://s.shopee.com.br/9zz6HcfAxu",
        "beneficio_dieta": "Evita o erro de comer 30% a mais de calorias sem perceber."
    },
    "spray_azeite": {
        "nome": "Galheteiro Borrifador & Dosador 2 em 1 de Vidro",
        "motivo": "Para untar frigideiras e temperar saladas economizando 80% do óleo.",
        "link": "https://s.shopee.com.br/7fbBlr9zK9",
        "beneficio_dieta": "Corta até 150 kcal por dia só no óleo da preparação."
    },
    "marmitas_vidro": {
        "nome": "Kit Marmitas Herméticas de Vidro com Divisórias",
        "motivo": "Organização do cronograma semanal (meal prep) sem estragar a comida.",
        "link": "https://s.shopee.com.br/7fbBlr9zK9",
        "beneficio_dieta": "Garante consistência na dieta quando a rotina aperta."
    },
    "forma_airfryer": {
        "nome": "Forma Antiaderente de Silicone para Airfryer",
        "motivo": "Assar frango, batatas e bolinhos sem sujar nada e sem pingar óleo.",
        "link": "https://s.shopee.com.br/9zz6HcfAxu",
        "beneficio_dieta": "Zero óleo adicionado no cozimento."
    },
    "mini_processador": {
        "nome": "Mini Processador Manual de Alimentos",
        "motivo": "Picar temperos, alho, cebola e recheios em 5 segundos.",
        "link": "https://s.shopee.com.br/7fbBlr9zK9",
        "beneficio_dieta": "Praticidade para preparar comida de verdade todo dia."
    }
}


class CatalogoReceitasSaciara:
    def __init__(self, pasta_conteudo: Path = CONTEUDO_DIR):
        self.pasta = pasta_conteudo
        self._receitas: List[Dict[str, Any]] = []

    def carregar_todas(self) -> List[Dict[str, Any]]:
        """Carrega e enriquece nutricionalmente as receitas catalogadas."""
        if self._receitas:
            return self._receitas

        if not self.pasta.exists():
            return []

        resultado = []
        for p in sorted(self.pasta.iterdir()):
            if not p.is_dir():
                continue

            desc_file = p / "descricao.txt"
            texto = desc_file.read_text(encoding="utf-8") if desc_file.exists() else ""

            # Extrai nome limpo (ex: "2026-09-23 - Crepioca de ricota" -> "Crepioca de ricota")
            nome_pasta = p.name
            match_nome = re.search(r"^\d{4}-\d{2}-\d{2}\s*-\s*(.+)$", nome_pasta)
            titulo = match_nome.group(1).replace("(revisar artes)", "").replace("(aguardando imagens)", "").strip() if match_nome else nome_pasta

            categoria = self._determinar_categoria(titulo, texto)
            perfil_nutricional = self._estimar_macros_receita(titulo, categoria)
            utensilios = self._vincular_utensilios(titulo, categoria)

            # Imagem de capa (se existir 01.png ou imagem)
            img_capa = None
            for cand in ["01.png", "01.jpg", "cover.png"]:
                if (p / cand).exists():
                    img_capa = f"/conteudo-saciara/{p.name}/{cand}"
                    break

            resultado.append({
                "id": len(resultado) + 1,
                "slug": re.sub(r"[^a-zA-Z0-9]+", "-", titulo.lower()).strip("-"),
                "titulo": titulo.capitalize(),
                "categoria": categoria,
                "tempo_preparo_min": perfil_nutricional["tempo_min"],
                "porcoes": 1,
                "descricao": texto.splitlines()[0] if texto else f"Receita saudável e prática de {titulo}.",
                "instrucoes": [
                    "Separe e pese os ingredientes frescos na balança culinária.",
                    "Aqueça a frigideira antiaderente (use o borrifador para economizar azeite) ou forno.",
                    "Misture os ingredientes com suavidade até obter ponto homogêneo.",
                    "Finalize o preparo em fogo médio por 3 a 5 minutos até dourar.",
                    "Sirva ainda quente ou armazene nas marmitas herméticas de vidro."
                ],
                "calorias": perfil_nutricional["calorias"],
                "macros": {
                    "proteina_g": perfil_nutricional["proteina_g"],
                    "carboidrato_g": perfil_nutricional["carboidrato_g"],
                    "gordura_g": perfil_nutricional["gordura_g"],
                    "fibras_g": perfil_nutricional["fibras_g"]
                },
                "tags": perfil_nutricional["tags"],
                "utensilios_recomendados": utensilios,
                "imagem_capa": img_capa or "/assets/placeholder_fit.jpg"
            })

        self._receitas = resultado
        return self._receitas

    def _determinar_categoria(self, titulo: str, texto: str) -> str:
        t = (titulo + " " + texto).lower()
        if any(w in t for w in ["crepioca", "tapioca", "cuscuz", "omelete", "mingau", "café", "pão"]):
            return "café da manhã"
        elif any(w in t for w in ["arroz", "frango", "peixe", "almôndega", "lentilha", "feijão", "carne", "almoço", "jantar"]):
            return "almoço & jantar"
        elif any(w in t for w in ["taça", "doce", "picolé", "banana assada", "abacate com cacau", "sobremesa"]):
            return "sobremesas fit"
        else:
            return "lanches práticos"

    def _estimar_macros_receita(self, titulo: str, categoria: str) -> Dict[str, Any]:
        t = titulo.lower()
        if "crepioca" in t:
            return {"calorias": 240, "proteina_g": 18.0, "carboidrato_g": 22.0, "gordura_g": 8.0, "fibras_g": 2.5, "tempo_min": 7, "tags": ["sem glúten", "rápida", "alta proteína"]}
        elif "omelete" in t:
            return {"calorias": 210, "proteina_g": 19.5, "carboidrato_g": 4.0, "gordura_g": 12.0, "fibras_g": 2.0, "tempo_min": 8, "tags": ["low carb", "cetogênica", "alta proteína"]}
        elif "frango" in t:
            return {"calorias": 360, "proteina_g": 38.0, "carboidrato_g": 18.0, "gordura_g": 9.0, "fibras_g": 4.5, "tempo_min": 25, "tags": ["marmita", "alta proteína", "airfryer"]}
        elif "peixe" in t:
            return {"calorias": 310, "proteina_g": 32.0, "carboidrato_g": 12.0, "gordura_g": 8.0, "fibras_g": 3.0, "tempo_min": 20, "tags": ["ômega 3", "leve", "jantar"]}
        elif "almôndega" in t:
            return {"calorias": 380, "proteina_g": 34.0, "carboidrato_g": 24.0, "gordura_g": 11.0, "fibras_g": 4.0, "tempo_min": 30, "tags": ["congelável", "marmita", "rico em ferro"]}
        elif "mingau" in t or "aveia" in t:
            return {"calorias": 220, "proteina_g": 10.0, "carboidrato_g": 35.0, "gordura_g": 4.5, "fibras_g": 6.0, "tempo_min": 5, "tags": ["rica em fibras", "saciedade", "conforto"]}
        elif "banana" in t or "taça" in t or "doce" in t:
            return {"calorias": 180, "proteina_g": 8.0, "carboidrato_g": 29.0, "gordura_g": 3.5, "fibras_g": 3.5, "tempo_min": 5, "tags": ["mata vontade de doce", "antioxidante"]}
        elif "lentilha" in t or "feijão" in t:
            return {"calorias": 290, "proteina_g": 16.0, "carboidrato_g": 44.0, "gordura_g": 3.0, "fibras_g": 11.0, "tempo_min": 25, "tags": ["super fibras", "saúde intestinal"]}
        else:
            return {"calorias": 250, "proteina_g": 15.0, "carboidrato_g": 28.0, "gordura_g": 7.0, "fibras_g": 3.5, "tempo_min": 10, "tags": ["equilibrada", "prática"]}

    def _vincular_utensilios(self, titulo: str, categoria: str) -> List[Dict[str, Any]]:
        utens = [UTENSILIOS_CATALOGO["balanca"]]  # Balança é universal
        t = titulo.lower()
        if any(w in t for w in ["salada", "grelhado", "assado", "frigideira"]):
            utens.append(UTENSILIOS_CATALOGO["spray_azeite"])
        if any(w in t for w in ["frango", "assado", "batata", "bolinho"]):
            utens.append(UTENSILIOS_CATALOGO["forma_airfryer"])
        if any(w in t for w in ["arroz", "feijão", "lentilha", "almôndega", "marmita"]):
            utens.append(UTENSILIOS_CATALOGO["marmitas_vidro"])
        if any(w in t for w in ["alho", "cebola", "pasta", "recheio"]):
            utens.append(UTENSILIOS_CATALOGO["mini_processador"])
        return utens[:2]
