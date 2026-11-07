# REGRA CANÔNICA SOBERANA: IMAGENS INDIVIDUAIS DE ALTA QUALIDADE VIA GOOGLE FLOW

> **Autoridade:** Ordem direta do usuário.  
> **Escopo:** Todas as receitas, itens culinários e conteúdos do aplicativo NutriPlus Saciara Fitness.  
> **Status:** OBRIGATÓRIA E INEGOCIÁVEL (Zero Exceções).

---

## 1. Princípio Fundamental
Nenhuma receita do NutriPlus pode utilizar imagens genéricas, desconexas da realidade do prato, fallbacks aleatórios de bancos externos (Unsplash/Pexels) ou fotos de terceiros sem fidelidade gastronômica exata.

- **Proibição Absoluta:**
  - ❌ Gatos dormindo para representar mingaus.
  - ❌ Torradas com abacate para representar cuscuz nordestino.
  - ❌ Placeholders cinzas ou quebrados.
  - ❌ Instruções de frigideira para posts de hábitos comportamentais (mindfulness, caminhada, água).

---

## 2. Padrão Visual Obrigatório (Fórmula 8K / 9:16)
Todas as imagens geradas devem seguir o pipeline de alta qualidade visual pelo **Google Flow** via Brave CDP (porta 9222) ou Chrome CDP:
- **Aspect Ratio:** Proporção vertical 9:16 (enquadramento mobile cinematográfico).
- **Estética:** Anti-IA, fotografia gastronômica documental de revista culinária (Kinfolk / Bon Appétit).
- **Iluminação:** Luz natural difusa de janela matinal ou vespertina (warm side lighting).
- **Textura e Realismo:** Vapor suave ascendente em pratos quentes, cerâmica fosca artesanal, grãos nítidos, ingredientes frescos reais ao fundo desfocado (bokeh suave f/1.8).

---

## 3. Estratégia de Resolução de Imagens
Toda renderização no catálogo, rotina diária ou substituições deve obedecer à seguinte hierarquia rígida:

1. **Arte Oficial do Canal (`conteudo-saciara/<data-pasta>/01.png`):**
   - Utilizada quando a pasta possui carrossel oficial diagramado pela equipe Saciara (25 receitas atuais).
2. **Arte Dedicada Gerada pelo Google Flow (`assets/receitas_flow/<slug>.png`):**
   - Imagens individuais renderizadas especificamente para a receita com o prompt gastronômico individual.
3. **Loop Contínuo de Geração:**
   - O script autônomo `scratch/gerar_lote_flow.py` (ou `backend_e_agentes/gerador_flow_continuo.py`) deve gerar em segundo plano as receitas pendentes até que todas as 156 receitas tenham seu asset visual individual exclusivo.
4. **Tratamento de Hábitos Comportamentais:**
   - Itens como "Comer com atenção", "Caminhada possível" e "Uma pausa possível" devem ser identificados como Hábitos (`categoria: "hábito & estilo de vida"`), exibindo badges e modais informativos sobre saúde mental e presença, sem tempos de forno ou calorias nutricionais incorretas.

---

## 4. Rastreamento e Conformidade
Qualquer nova receita adicionada à base de dados `receitas.json` deve imediatamente disparar a solicitação de geração da imagem individual correspondente ao Google Flow.
