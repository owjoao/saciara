"""
Atualiza o HTML da aba Compras do Mês para integrar o gerador de plano por perfil biológico
"""
import sys

def main():
    c = open(r'f:\Nova pasta\site\saciara\index.html', encoding='utf-8').read()
    idx1 = c.find('<!-- ======================================================================\n         SEÇÃO 5: ABA DE COMPRAS DO MÊS')
    if idx1 == -1:
        idx1 = c.find('SEÇÃO 5: ABA DE COMPRAS DO MÊS')
    idx2 = c.find('</div> <!-- /view-compras -->') + len('</div> <!-- /view-compras -->')

    novo_html = """<!-- ======================================================================
         SEÇÃO 5: ABA DE COMPRAS DO MÊS INTELIGENTE (BASEADA NO SEU PLANO PERSONALIZADO)
         ====================================================================== -->
    <div id="view-compras" class="view-section">
      <!-- 1. Header com Imagem de Supermercado e Legumes Frescos -->
      <section class="compras-header">
        <img class="compras-header-bg" src="https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1200&q=80" alt="Supermercado Fresco">
        <div class="compras-header-content">
          <div class="compras-title-row">
            <span class="compras-cart-icon">🛒</span>
            <h1 class="compras-title">Compras do Mês para o Seu Plano</h1>
          </div>
          <p class="compras-subtitle">A lista de compras mensal não é aleatória: ela é a soma exata dos ingredientes de todas as receitas prescritas para o seu perfil fisiológico e meta calórica.</p>
        </div>
      </section>

      <!-- 2. Formulário de Perfil Biológico & Preferências (Dados Pessoais) -->
      <section class="perfil-form-card">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:20px;">🧬</span>
            <h3 style="color:#FFFFFF; font-size:16px; font-weight:800;">Seus Dados Fisiológicos & Alergias</h3>
          </div>
          <span style="font-size:11px; color:#00D070; font-weight:700;">Modelo Científico Kevin Hall & Mifflin-St Jeor</span>
        </div>

        <div class="perfil-form-grid">
          <div class="form-field-group">
            <label class="form-field-label">Gênero Biológico</label>
            <select id="userGenero" class="form-field-select" onchange="recalcularPlanoECompras()">
              <option value="feminino" selected>Feminino</option>
              <option value="masculino">Masculino</option>
            </select>
          </div>

          <div class="form-field-group">
            <label class="form-field-label">Peso Atual (kg)</label>
            <input type="number" id="userPeso" class="form-field-input" value="70.8" step="0.1" onchange="recalcularPlanoECompras()">
          </div>

          <div class="form-field-group">
            <label class="form-field-label">Altura (cm)</label>
            <input type="number" id="userAltura" class="form-field-input" value="165" onchange="recalcularPlanoECompras()">
          </div>

          <div class="form-field-group">
            <label class="form-field-label">Idade (anos)</label>
            <input type="number" id="userIdade" class="form-field-input" value="28" onchange="recalcularPlanoECompras()">
          </div>

          <div class="form-field-group">
            <label class="form-field-label">Nível de Atividade Física</label>
            <select id="userAtividade" class="form-field-select" onchange="recalcularPlanoECompras()">
              <option value="moderado" selected>Moderado (3 a 5 treinos/sem)</option>
              <option value="sedentario">Sedentário (pouco ou nenhum)</option>
              <option value="leve">Leve (1 a 2 treinos/sem)</option>
              <option value="intenso">Intenso (6 a 7 treinos/sem)</option>
            </select>
          </div>

          <div class="form-field-group">
            <label class="form-field-label">Alergias ou Restrições</label>
            <select id="userRestricoes" class="form-field-select" onchange="recalcularPlanoECompras()">
              <option value="nenhuma" selected>Nenhuma (Onívoro Saudável)</option>
              <option value="lactose">Intolerância a Lactose</option>
              <option value="gluten">Sem Glúten (Celíaco/Sensível)</option>
              <option value="frutos_mar">Alergia a Frutos do Mar / Peixe</option>
              <option value="vegetariano">Vegetariano (Ovolacto)</option>
            </select>
          </div>

          <div class="form-field-group">
            <label class="form-field-label">Meta de Emagrecimento</label>
            <select id="userMetaKg" class="form-field-select" onchange="recalcularPlanoECompras()">
              <option value="70" selected>Meta: 70 kg (Definição Sustentável)</option>
              <option value="65">Meta: 65 kg (Perda Acentuada)</option>
              <option value="60">Meta: 60 kg (Foco Atlético)</option>
            </select>
          </div>

          <div class="form-field-group">
            <label class="form-field-label">Orçamento Alvo (Opcional R$)</label>
            <input type="number" id="inputOrcamentoReais" class="form-field-input" value="480" step="50" oninput="recalcularPlanoECompras()">
          </div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; padding-top:12px; border-top:1px solid #1C2B48;">
          <div style="font-size:12px; color:#64748B;">
            Ao alterar qualquer dado, as refeições dos 30 dias são recalculadas e os ingredientes são somados automaticamente.
          </div>
          <button class="btn-gerar-plano" onclick="recalcularPlanoECompras()">
            <span>⚡</span>
            <span>Recalcular Plano & Cesta</span>
          </button>
        </div>
      </section>

      <!-- 3. Diagnóstico Fisiológico do Seu Plano Gerado -->
      <section class="diagnostico-banner-card">
        <div>
          <div class="diag-title-row">
            <span style="color:#00D070; font-size:22px;">📊</span>
            <div class="diag-title-text" id="diagTituloPlano">Plano Científico Saciara: 1.800 kcal/dia (Déficit Fisiológico Kevin Hall)</div>
          </div>
          <p class="diag-desc-text" id="diagDescricaoPlano">
            Metabolismo Basal (TMB) de 1.468 kcal somado à atividade física resulta em TDEE de 2.275 kcal. O déficit controlado de 475 kcal/dia gera <strong>perda real de 1,9 kg de pura gordura ao mês</strong> preservando 100% da sua massa muscular.
          </p>
          <div class="diag-badges-row" id="diagBadgesRow">
            <span class="diag-pill">🔥 1.800 kcal/dia</span>
            <span class="diag-pill">🥩 130g Proteínas/dia (1,8g/kg)</span>
            <span class="diag-pill">🌾 185g Carboidratos/dia</span>
            <span class="diag-pill">🥑 62g Gorduras/dia</span>
            <span class="diag-pill" style="color:#00D070;">✓ 150 Refeições/mês Somadas</span>
          </div>
        </div>
      </section>

      <!-- 4. Resumo de Custos e Totais da Cesta Mensal -->
      <section class="budget-control-card">
        <div>
          <div style="font-size:12px; color:#64748B; font-weight:700; text-transform:uppercase; margin-bottom:4px;">Cotação nos Grandes Atacadistas</div>
          <h2 style="font-size:20px; font-weight:800; color:#FFFFFF; margin-bottom:6px;">Preço Total das Refeições do Mês</h2>
          <p style="font-size:13px; color:#94A3B8;">Valores médios para compra mensal consolidada em redes de Salvador, SP e RJ:</p>
          <div class="budget-supermarket-badges">
            <span class="market-badge" style="color:#00D070; border-color:#00D070;">Atacarejo</span>
            <span class="market-badge" style="color:#00D070; border-color:#00D070;">Assaí</span>
            <span class="market-badge">Extra</span>
            <span class="market-badge">Carrefour</span>
          </div>
        </div>

        <div class="budget-summary-stats">
          <div class="budget-stat-box">
            <div class="budget-stat-num" id="statTotalEstimado">R$ 468,30</div>
            <div class="budget-stat-label">Custo dos 30 Dias</div>
          </div>
          <div class="budget-stat-box">
            <div class="budget-stat-num" id="statEconomiaEstimada" style="color:#38BDF8;">R$ 93,60</div>
            <div class="budget-stat-label">Economia vs. Varejo</div>
          </div>
          <div class="budget-stat-box">
            <div class="budget-stat-num" id="statRefeicoesCobertas" style="color:#FFB020;">150 pratos</div>
            <div class="budget-stat-label">Refeições Completas</div>
          </div>
        </div>
      </section>

      <!-- 5. Categorias com Alimentos Reais, Gramas Somadas e Fotos -->
      <div class="compras-categories-grid" id="comprasCategoriesGrid">
        <!-- Renderizado dinamicamente via JS a partir da soma dos 30 dias de receitas -->
      </div>
    </div> <!-- /view-compras -->"""

    c_novo = c[:idx1] + novo_html + c[idx2:]
    with open(r'f:\Nova pasta\site\saciara\index.html', 'w', encoding='utf-8') as f:
        f.write(c_novo)
    print("Sucesso! index.html atualizado com nova aba Compras do Mês.")

if __name__ == "__main__":
    main()
