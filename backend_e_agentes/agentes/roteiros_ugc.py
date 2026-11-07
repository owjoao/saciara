"""Fábrica de Roteiros e Overlays de Vídeos UGC (Estilo Amigo Apresentando).
Zero tom de loja. 10 variações focadas em curiosidade, utilidade e clique para o @saciara_.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class VariacaoPostStoryVideo:
    id: int
    angulo_psicologico: str
    produto_foco: str
    termo_busca_video: str
    frase_topo_story: str
    locucao_ou_legenda_amigo: str
    texto_sticker: str
    motivo_conversao: str


VARIASCOES_UGC_SACIARA: List[VariacaoPostStoryVideo] = [
    VariacaoPostStoryVideo(
        id=1,
        angulo_psicologico="Segredo de Bastidor / Confidência",
        produto_foco="Balança Digital de Cozinha SF-400",
        termo_busca_video="balanca sf 400 pesando comida pov shorts",
        frase_topo_story="Quem me perguntou onde achei isso...",
        locucao_ou_legenda_amigo="Gente, vocês sempre me perguntam como eu não erro na quantidade das receitas... Eu peso direto no prato com essa balancinha que não custou quase nada na Shopee. Olha que praticidade!",
        texto_sticker="ONDE COMPREI",
        motivo_conversao="Parece resposta a uma pergunta real de DM. Zero pressão de venda."
    ),
    VariacaoPostStoryVideo(
        id=2,
        angulo_psicologico="Alívio de Preguiça / Não Sujar Louça",
        produto_foco="Forma de Silicone para Airfryer",
        termo_busca_video="forma de silicone air fryer tirando comida shorts",
        frase_topo_story="Minha airfryer nunca mais viu esponja 😂",
        locucao_ou_legenda_amigo="Se você tem preguiça de lavar a cesta da airfryer todo dia igual eu, olha essa forma de silicone. Tira, come e passa uma água. Mudou minha rotina real!",
        texto_sticker="PEGAR O LINK",
        motivo_conversao="Resolve uma das maiores dores universais de quem cozinha."
    ),
    VariacaoPostStoryVideo(
        id=3,
        angulo_psicologico="Descoberta Acidental / Dica de Ouro",
        produto_foco="Mini Processador Manual de Alimentos",
        termo_busca_video="mini processador manual de alimentos puxando cordinha pov shorts",
        frase_topo_story="O melhor achado que fiz esse mês",
        locucao_ou_legenda_amigo="Olha a facilidade pra picar cebola e alho em 5 segundos sem chorar e sem ligar nada na tomada. Paguei uma pechincha na Shopee e uso todo santo dia.",
        texto_sticker="OLHA ESSE ACHADO",
        motivo_conversao="Demonstração visual hipnótica (puxar cordinha) + benefício tangível."
    ),
    VariacaoPostStoryVideo(
        id=4,
        angulo_psicologico="Organização Terapêutica / Satisfying",
        produto_foco="Marmitas Herméticas com Divisória de Vidro",
        termo_busca_video="marmita de vidro hermetica organizando comida pov shorts",
        frase_topo_story="O segredo pra comida não azedar na semana",
        locucao_ou_legenda_amigo="Muita gente me fala que marmita fica ruim depois de 2 dias... O segredo não é a comida, é essa trava hermética com anel de silicone. Deixei o link de onde peguei as minhas!",
        texto_sticker="LINK DAS MARMITAS",
        motivo_conversao="Combina com o carrossel de alimentação da semana do Saciara."
    ),
    VariacaoPostStoryVideo(
        id=5,
        angulo_psicologico="Economia Inteligente / Quebra de Mito",
        produto_foco="Pulverizador e Borrifador de Azeite em Spray",
        termo_busca_video="spray azeite borrifando na frigideira pov shorts",
        frase_topo_story="Como economizar metade da garrafa de azeite",
        locucao_ou_legenda_amigo="Eu vivia encharcando a frigideira sem perceber... Esse borrifador espalha uma nuvem fininha que não gruda nada e faz o azeite durar 3 vezes mais. Olha isso!",
        texto_sticker="VER O BORRIFADOR",
        motivo_conversao="Apelo duplo: menos calorias (fitness) + economia no bolso."
    ),
    VariacaoPostStoryVideo(
        id=6,
        angulo_psicologico="Praticidade Móvel / Rotina de Trabalho",
        produto_foco="Mini Liquidificador Portátil USB",
        termo_busca_video="mini liquidificador portatil batendo whey frutas pov shorts",
        frase_topo_story="Faço meu shake no carro ou no trabalho",
        locucao_ou_legenda_amigo="Gente, esse mini liquidificador portátil bate whey com fruta congelada em qualquer lugar por USB. Nem sujo a cozinha de manhã!",
        texto_sticker="ONDE ENCONTREI",
        motivo_conversao="Perfeito para o público que treina ou não tem tempo de tomar café da manhã."
    ),
    VariacaoPostStoryVideo(
        id=7,
        angulo_psicologico="Testei e Me Surpreendi (Ceticismo Vencido)",
        produto_foco="Espátula e Pincel de Silicone Inteiriço",
        termo_busca_video="espatula silicone raspando tigela bolo pov shorts",
        frase_topo_story="Pensei que era bobagem até usar a primeira vez",
        locucao_ou_legenda_amigo="Sabe aquela espátula que solta a ponta e acumula sujeira? Essa aqui é uma peça só de silicone macio, rapa a tigela todinha sem deixar nada. Achei baratinho!",
        texto_sticker="CONFERIR AQUI",
        motivo_conversao="Elimina a frustração de utensílios descartáveis que estragam rápido."
    ),
    VariacaoPostStoryVideo(
        id=8,
        angulo_psicologico="Estética de Cozinha / Clean Girl Fitness",
        produto_foco="Potes Porta Temperos Magnéticos / Vidro com Tampa Bambu",
        termo_busca_video="porta temperos organizando bancada aesthetic shorts",
        frase_topo_story="Deixou minha bancada parecendo de Pinterest",
        locucao_ou_legenda_amigo="Olha como ficou linda a organização dos temperos naturais... Comprei esse kit na Shopee pra tirar os saquinhos feios do armário, super prático na hora de cozinhar.",
        texto_sticker="DETALHES DO KIT",
        motivo_conversao="Apelo estético e inspirador muito forte para mulheres no Instagram."
    ),
    VariacaoPostStoryVideo(
        id=9,
        angulo_psicologico="Lanche Rápido / Zero Bagunça",
        produto_foco="Omeleteira e Frigideira Antiaderente 4 Cavidades",
        termo_busca_video="frigideira 4 cavidades fazendo ovo panqueca pov shorts",
        frase_topo_story="Faço o café de todo mundo em 4 minutos",
        locucao_ou_legenda_amigo="Dá pra fazer o ovinho, a panqueca de banana e o pão de queijo de frigideira tudo de uma vez sem misturar. Nem precisa de óleo porque não gruda nada!",
        texto_sticker="VER COMO FUNCIONA",
        motivo_conversao="Demonstração visual altamente compartilhável (mãos virando os 4 ovos perfeitos)."
    ),
    VariacaoPostStoryVideo(
        id=10,
        angulo_psicologico="Hidratação Sem Sofrimento / Hábito Diário",
        produto_foco="Garrafa Motivacional 2 Litros com Canudo",
        termo_busca_video="garrafa motivacional 2l enchendo agua frutas pov shorts",
        frase_topo_story="O único jeito que me fez bater 2L de água por dia",
        locucao_ou_legenda_amigo="Eu esquecia de beber água o dia todo até pegar essa garrafa com os horários marcados. O canudo facilita demais pra ir tomando enquanto trabalho.",
        texto_sticker="ONDE PEGUEI A MINHA",
        motivo_conversao="Conexão direta com bem-estar e emagrecimento sem esforço."
    ),
]


def listar_variacoes_formatadas() -> List[Dict[str, Any]]:
    return [v.__dict__ for v in VARIASCOES_UGC_SACIARA]
