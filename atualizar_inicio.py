"""
Script auxiliar para atualizar a aba de início em index.html com segurança
"""
import sys

def main():
    c = open(r'f:\Nova pasta\site\saciara\index.html', encoding='utf-8').read()
    idx1 = c.find('<!-- ======================================================================\n         SEÇÃO 1: ABA DE INÍCIO')
    if idx1 == -1:
        idx1 = c.find('SEÇÃO 1: ABA DE INÍCIO')
    idx2 = c.find('</div> <!-- /view-inicio -->') + len('</div> <!-- /view-inicio -->')

    novo_bloco = """<!-- ======================================================================
         SEÇÃO 1: ABA DE INÍCIO OTIMIZADA — ROTINA ESSENCIAL, ÁGUA & PERDA DE PESO
         (Foco 100% em Qualidade de Vida, Sem Gráficos, Praticidade Diária Máxima)
         ====================================================================== -->
    <div id="view-inicio" class="view-section active">
      <!-- 1. Saudação Calma e Data Atual -->
      <section class="inicio-hero-compact">
        <div>
          <h2 class="inicio-saudacao-title">Olá, Ana! 👋</h2>
          <p class="inicio-saudacao-sub">Aqui está sua rotina diária essencial para viver bem e atingir sua meta com leveza.</p>
        </div>
        <div class="inicio-date-pill">
          <span>📅</span>
          <span id="inicioDataHoje">Hoje • Segunda-feira, 03/11</span>
        </div>
      </section>

      <!-- 2. Os Três Pilares da Sua Rotina Diária -->
      <div class="inicio-pilares-grid">
        <!-- Pilar 1: Alimentação de Hoje -->
        <div class="pilar-card">
          <div class="pilar-header">
            <div class="pilar-title-group">
              <div class="pilar-icon-wrap" style="background:rgba(0, 208, 112, 0.12); color:#00D070;">🥗</div>
              <span class="pilar-title-text">Alimentação</span>
            </div>
            <span class="pilar-badge-status" style="background:rgba(0,208,112,0.15); color:#00D070;">Dentro da meta</span>
          </div>
          <div class="pilar-primary-val" id="inicioCaloriasVal">1.450 <span style="font-size:16px; font-weight:600; color:#64748B;">/ 1.800 kcal</span></div>
          <div class="pilar-sub-desc">Faltam <strong>350 kcal</strong> para completar seu dia com precisão energética.</div>
          
          <div class="pilar-progress-bar">
            <div class="pilar-progress-fill" style="width:80%; background:#00D070;"></div>
          </div>

          <div class="pilar-footer-note">
            <span>🥩</span>
            <span>Proteínas: <strong>95g / 130g</strong> • Foco em saciedade</span>
          </div>
        </div>

        <!-- Pilar 2: Hidratação Interativa -->
        <div class="pilar-card">
          <div class="pilar-header">
            <div class="pilar-title-group">
              <div class="pilar-icon-wrap" style="background:rgba(56, 189, 248, 0.12); color:#38BDF8;">💧</div>
              <span class="pilar-title-text">Água & Hidratação</span>
            </div>
            <span class="pilar-badge-status" id="inicioWaterStatus" style="background:rgba(56,189,248,0.15); color:#38BDF8;">84% da meta</span>
          </div>
          <div class="pilar-primary-val" id="inicioWaterVal">2,1 <span style="font-size:16px; font-weight:600; color:#64748B;">/ 2,5 L</span></div>
          <div class="pilar-sub-desc">Faltam apenas <strong>400 ml</strong> (2 copos) para otimizar sua taxa metabólica.</div>

          <div class="pilar-progress-bar">
            <div class="pilar-progress-fill" id="inicioWaterBar" style="width:84%; background:#38BDF8;"></div>
          </div>

          <div class="water-quick-buttons">
            <button class="btn-add-water" onclick="adicionarAguaRapida(200)">+ 200 ml</button>
            <button class="btn-add-water" onclick="adicionarAguaRapida(300)">+ 300 ml</button>
            <button class="btn-add-water" onclick="adicionarAguaRapida(500)">+ 500 ml</button>
          </div>
        </div>

        <!-- Pilar 3: Perda de Peso Sustentável -->
        <div class="pilar-card">
          <div class="pilar-header">
            <div class="pilar-title-group">
              <div class="pilar-icon-wrap" style="background:rgba(255, 176, 32, 0.12); color:#FFB020;">⚖️</div>
              <span class="pilar-title-text">Perda de Peso</span>
            </div>
            <span class="pilar-badge-status" style="background:rgba(255,176,32,0.15); color:#FFB020;">Rumo a 70 kg</span>
          </div>
          <div class="pilar-primary-val">70,8 kg</div>
          <div class="pilar-sub-desc">Você já eliminou <strong>-3,2 kg</strong> de forma sustentável e saudável!</div>

          <div class="pilar-progress-bar">
            <div class="pilar-progress-fill" style="width:93%; background:#FFB020;"></div>
          </div>

          <div class="pilar-footer-note" style="color:#00D070; font-weight:700;">
            <span>✓</span>
            <span>Faltam apenas 0,8 kg para sua meta inicial!</span>
          </div>
        </div>
      </div>

      <!-- 3. Rotina Alimentar Passo a Passo (O que comer hoje, horários e refeições práticas) -->
      <section class="inicio-rotina-section">
        <div class="rotina-section-header">
          <div class="rotina-header-title">
            <span>🍽️</span>
            <span>Sua Rotina Alimentar de Hoje</span>
          </div>
          <div class="rotina-header-badge">
            <span>✓</span>
            <span>Cardápio Científico Saciara • Sem complicações</span>
          </div>
        </div>

        <div class="refeicoes-timeline-list">
          <!-- 1. Café da Manhã -->
          <div class="refeicao-item-card">
            <div class="refeicao-timing-box">
              <span class="refeicao-icon-tag">☕</span>
              <div>
                <div class="refeicao-time-label">07:00 – 08:00</div>
                <div class="refeicao-name-bold">Café da Manhã</div>
              </div>
            </div>
            <img class="refeicao-mini-thumb" src="https://images.unsplash.com/photo-1517673132405-a56a62b18caf?auto=format&fit=crop&w=200&q=80" alt="Aveia com Banana">
            <div>
              <div class="refeicao-prato-title">Aveia com Banana, Canela e Chia</div>
              <div class="refeicao-ingredientes-short">1 xícara de aveia (40g) • 1 banana média fatiada • 1 colher de chá de chia</div>
            </div>
            <div class="refeicao-actions-box">
              <div class="refeicao-kcals">326 kcal</div>
              <div class="refeicao-macros-mini">P: 12g • C: 52g • G: 8g</div>
              <button class="btn-check-meal" onclick="toggleRefeicaoFeita(this)">
                <span>✓</span>
                <span>Consumido</span>
              </button>
            </div>
          </div>

          <!-- 2. Lanche da Manhã -->
          <div class="refeicao-item-card">
            <div class="refeicao-timing-box">
              <span class="refeicao-icon-tag">🍏</span>
              <div>
                <div class="refeicao-time-label">10:30 – 11:30</div>
                <div class="refeicao-name-bold">Lanche da Manhã</div>
              </div>
            </div>
            <img class="refeicao-mini-thumb" src="https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=200&q=80" alt="Iogurte com Frutas">
            <div>
              <div class="refeicao-prato-title">Iogurte Natural com Frutas Vermelhas</div>
              <div class="refeicao-ingredientes-short">1 pote de iogurte natural (170g) • Frutas vermelhas frescas (50g)</div>
            </div>
            <div class="refeicao-actions-box">
              <div class="refeicao-kcals">142 kcal</div>
              <div class="refeicao-macros-mini">P: 10g • C: 14g • G: 4g</div>
              <button class="btn-check-meal" onclick="toggleRefeicaoFeita(this)">
                <span>✓</span>
                <span>Consumido</span>
              </button>
            </div>
          </div>

          <!-- 3. Almoço -->
          <div class="refeicao-item-card">
            <div class="refeicao-timing-box">
              <span class="refeicao-icon-tag">🍴</span>
              <div>
                <div class="refeicao-time-label">12:30 – 14:00</div>
                <div class="refeicao-name-bold">Almoço</div>
              </div>
            </div>
            <img class="refeicao-mini-thumb" src="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=200&q=80" alt="Frango com Arroz Integral">
            <div>
              <div class="refeicao-prato-title">Frango Grelhado, Arroz Integral & Salada Colorida</div>
              <div class="refeicao-ingredientes-short">100g peito de frango • ½ xícara de arroz integral • Salada verde à vontade com azeite em spray</div>
            </div>
            <div class="refeicao-actions-box">
              <div class="refeicao-kcals">436 kcal</div>
              <div class="refeicao-macros-mini">P: 38g • C: 45g • G: 12g</div>
              <button class="btn-check-meal" onclick="toggleRefeicaoFeita(this)">
                <span>✓</span>
                <span>Consumido</span>
              </button>
            </div>
          </div>

          <!-- 4. Lanche da Tarde -->
          <div class="refeicao-item-card">
            <div class="refeicao-timing-box">
              <span class="refeicao-icon-tag">🧁</span>
              <div>
                <div class="refeicao-time-label">16:00 – 17:00</div>
                <div class="refeicao-name-bold">Lanche da Tarde</div>
              </div>
            </div>
            <img class="refeicao-mini-thumb" src="https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=200&q=80" alt="Castanhas e Maçã">
            <div>
              <div class="refeicao-prato-title">Mix de Castanhas & Maçã Crocante</div>
              <div class="refeicao-ingredientes-short">1 punhado de castanhas do pará/caju (15g) • 1 maçã média</div>
            </div>
            <div class="refeicao-actions-box">
              <div class="refeicao-kcals">198 kcal</div>
              <div class="refeicao-macros-mini">P: 3g • C: 25g • G: 10g</div>
              <button class="btn-check-meal" onclick="toggleRefeicaoFeita(this)">
                <span>✓</span>
                <span>Consumido</span>
              </button>
            </div>
          </div>

          <!-- 5. Jantar -->
          <div class="refeicao-item-card">
            <div class="refeicao-timing-box">
              <span class="refeicao-icon-tag">🌙</span>
              <div>
                <div class="refeicao-time-label">19:00 – 20:30</div>
                <div class="refeicao-name-bold">Jantar</div>
              </div>
            </div>
            <img class="refeicao-mini-thumb" src="https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=200&q=80" alt="Salmão com Legumes">
            <div>
              <div class="refeicao-prato-title">Salmão Grelhado com Legumes no Vapor</div>
              <div class="refeicao-ingredientes-short">120g filé de salmão • Brócolis, cenoura e abobrinha no vapor à vontade</div>
            </div>
            <div class="refeicao-actions-box">
              <div class="refeicao-kcals">354 kcal</div>
              <div class="refeicao-macros-mini">P: 32g • C: 18g • G: 16g</div>
              <button class="btn-check-meal" onclick="toggleRefeicaoFeita(this)">
                <span>✓</span>
                <span>Consumido</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 4. Rodapé Focado em Qualidade de Vida e Hidratação -->
      <div class="inicio-bottom-duo">
        <!-- Perda de Peso Sem Estresse -->
        <div class="perda-card-science">
          <div class="perda-content-left">
            <div class="perda-title-badge">
              <span>🎯</span>
              <span>Ciência da Perda de Peso Sem Estresse</span>
            </div>
            <h3 class="perda-main-title">Você não precisa se pesar todo dia</h3>
            <p class="perda-text-desc">
              O modelo Kevin Hall comprova que oscilações diárias de até 1,5 kg decorrem de retenção hídrica, sódio e trânsito intestinal, não de ganho de gordura. O segredo da qualidade de vida é seguir sua rotina com tranquilidade: os resultados fisiológicos são inevitáveis.
            </p>
            <button class="btn-edit-target" onclick="abrirModalDicaPerdaPeso()">Entenda a Fisiologia ➔</button>
          </div>
          <div class="perda-metric-bigbox">
            <div class="perda-big-num">-3,2 kg</div>
            <div class="perda-big-label">Gordura Real Perdida</div>
            <div style="font-size:11px; color:#00D070; margin-top:6px; font-weight:700;">Ritmo Ideal ✓</div>
          </div>
        </div>

        <!-- Lembrete Hídrico Inteligente -->
        <div class="water-reminder-card">
          <div class="water-reminder-header">
            <span>💧</span>
            <span>Regra de Ouro da Água</span>
          </div>
          <p class="water-reminder-text">
            Beber 500 ml de água cerca de 30 minutos antes das principais refeições aumenta a saciedade e eleva seu gasto energético de repouso em até 24% por 60 minutos.
          </p>
          <button class="btn-primary" style="width:100%; padding:10px; background:#38BDF8; color:#070B14; border:none; border-radius:8px; font-weight:800; cursor:pointer; margin-top:auto;" onclick="adicionarAguaRapida(500)">
            Bebi 500 ml agora! 💧
          </button>
        </div>
      </div>
    </div> <!-- /view-inicio -->"""

    c_novo = c[:idx1] + novo_bloco + c[idx2:]
    with open(r'f:\Nova pasta\site\saciara\index.html', 'w', encoding='utf-8') as f:
        f.write(c_novo)
    print("Sucesso! index.html atualizado.")

if __name__ == "__main__":
    main()
