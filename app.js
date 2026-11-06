// ==========================================================================
// NUTRIPLUS / SACIARA — MOTOR INTERATIVO & CONTROLE DE ELEMENTOS (ESM)
// ==========================================================================

const AppState = {
  currentPeriod: '30D',
  habitsChecked: [true, true, true, true, true],
  recipes: [],
  profile: {
    nome: "Ana",
    pesoInicial: 74.0,
    pesoAtual: 70.8,
    pesoMeta: 70.0,
    altura: 168,
    idade: 28,
    massaMagra: 49.7,
    bf: 28.0,
    caloriasHoje: 1450,
    caloriasMeta: 1800,
    macrosHoje: {
      proteina: { g: 95, pct: 21 },
      carbo: { g: 160, pct: 35 },
      gordura: { g: 52, pct: 44 }
    }
  }
};

// Dados de evolução de peso por período
const SeriesPeso = {
  '7D': [71.5, 71.3, 71.2, 71.0, 70.9, 70.8, 70.8],
  '30D': [74.0, 73.8, 73.7, 73.4, 73.5, 73.2, 73.1, 72.9, 73.0, 72.7, 72.6, 72.4, 72.5, 72.2, 72.0, 71.9, 72.1, 71.8, 71.6, 71.7, 71.4, 71.3, 71.5, 71.2, 71.1, 71.0, 70.9, 70.9, 70.8, 70.8],
  '90D': [77.5, 76.8, 76.0, 75.2, 74.5, 73.8, 73.1, 72.4, 71.6, 70.8],
  '1A': [82.0, 80.5, 79.0, 77.2, 76.0, 75.1, 74.0, 73.2, 72.5, 71.8, 71.0, 70.8]
};

// ==========================================================================
// INICIALIZAÇÃO
// ==========================================================================
document.addEventListener('DOMContentLoaded', async () => {
  renderWeightChart('30D');
  atualizarHabitosUI();
  bindSidebarNav();

  // Carrega base de receitas do Saciara
  try {
    const res = await fetch('receitas.json');
    if (res.ok) {
      AppState.recipes = await res.json();
    }
  } catch (e) {
    console.log('Catálogo de receitas carregado localmente');
  }
});

// ==========================================================================
// 1. GRÁFICO SVG INTERATIVO DE EVOLUÇÃO DO PESO
// ==========================================================================
function renderWeightChart(period) {
  const container = document.getElementById('weightChartContainer');
  if (!container) return;

  const data = SeriesPeso[period] || SeriesPeso['30D'];
  const minVal = Math.min(...data) - 0.8;
  const maxVal = Math.max(...data) + 0.8;
  const w = 480;
  const h = 130;
  const paddingX = 24;
  const paddingY = 16;

  const getX = (i) => paddingX + (i / (data.length - 1)) * (w - 2 * paddingX);
  const getY = (v) => h - paddingY - ((v - minVal) / (maxVal - minVal)) * (h - 2 * paddingY);

  // Gera path suave
  let pathD = `M ${getX(0)} ${getY(data[0])}`;
  for (let i = 1; i < data.length; i++) {
    const xc = (getX(i) + getX(i - 1)) / 2;
    const yc = (getY(data[i]) + getY(data[i - 1])) / 2;
    pathD += ` Q ${getX(i - 1)} ${getY(data[i - 1])}, ${xc} ${yc}`;
  }
  pathD += ` T ${getX(data.length - 1)} ${getY(data[data.length - 1])}`;

  // Área preenchida com gradiente
  const areaD = `${pathD} L ${getX(data.length - 1)} ${h} L ${getX(0)} ${h} Z`;

  // Último ponto
  const lastX = getX(data.length - 1);
  const lastY = getY(data[data.length - 1]);
  const currentWeight = data[data.length - 1].toFixed(1).replace('.', ',');

  container.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}" style="width:100%; height:100%; overflow:visible;">
      <defs>
        <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#00D070" stop-opacity="0.28" />
          <stop offset="100%" stop-color="#00D070" stop-opacity="0.0" />
        </linearGradient>
      </defs>

      <!-- Linhas de Grade Horizontais -->
      <line x1="${paddingX}" y1="${getY(74)}" x2="${w - paddingX}" y2="${getY(74)}" stroke="#1C2B48" stroke-width="1" stroke-dasharray="3,3" />
      <text x="4" y="${getY(74) + 4}" fill="#64748B" font-size="9" font-weight="600">74 kg</text>

      <line x1="${paddingX}" y1="${getY(72)}" x2="${w - paddingX}" y2="${getY(72)}" stroke="#1C2B48" stroke-width="1" stroke-dasharray="3,3" />
      <text x="4" y="${getY(72) + 4}" fill="#64748B" font-size="9" font-weight="600">72 kg</text>

      <line x1="${paddingX}" y1="${getY(70)}" x2="${w - paddingX}" y2="${getY(70)}" stroke="#1C2B48" stroke-width="1" stroke-dasharray="3,3" />
      <text x="4" y="${getY(70) + 4}" fill="#64748B" font-size="9" font-weight="600">70 kg</text>

      <line x1="${paddingX}" y1="${getY(68)}" x2="${w - paddingX}" y2="${getY(68)}" stroke="#1C2B48" stroke-width="1" stroke-dasharray="3,3" />
      <text x="4" y="${getY(68) + 4}" fill="#64748B" font-size="9" font-weight="600">68 kg</text>

      <!-- Área e Linha da Curva -->
      <path d="${areaD}" fill="url(#chartFill)" />
      <path d="${pathD}" fill="none" stroke="#00D070" stroke-width="2.5" stroke-linecap="round" />

      <!-- Ponto Atual em Destaque -->
      <circle cx="${lastX}" cy="${lastY}" r="4" fill="#00D070" stroke="#070B14" stroke-width="2" />

      <!-- Badge SVG Flutuante Perfeitamente Alinhado e Escalável -->
      <g transform="translate(${Math.min(lastX - 28, w - 64)}, ${Math.max(lastY - 30, 8)})">
        <rect width="56" height="22" rx="6" fill="#00D070" filter="drop-shadow(0px 2px 6px rgba(0,208,112,0.4))" />
        <text x="28" y="15" fill="#070B14" font-family="'Plus Jakarta Sans', sans-serif" font-size="11" font-weight="800" text-anchor="middle">
          ${currentWeight} kg
        </text>
      </g>
    </svg>
  `;
}

function alterarPeriodo(periodo, btn) {
  AppState.currentPeriod = periodo;
  document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderWeightChart(periodo);
}

// ==========================================================================
// 2. CONTROLE DE HÁBITOS DA SEMANA & METAS
// ==========================================================================
function toggleHabit(element) {
  element.classList.toggle('unchecked');
  const items = document.querySelectorAll('.habit-circle-item');
  const checkedCount = Array.from(items).filter(i => !i.classList.contains('unchecked')).length;
  const counter = document.getElementById('habitsCounter');
  if (counter) counter.innerText = `${checkedCount}/5`;
}

function atualizarHabitosUI() {
  const counter = document.getElementById('habitsCounter');
  if (counter) counter.innerText = '7/7';
}

function atualizarMetasContador() {
  const checkboxes = document.querySelectorAll('.meta-checkbox-item input[type="checkbox"]');
  const checked = Array.from(checkboxes).filter(c => c.checked).length;
}

// ==========================================================================
// 3. BARRA LATERAL (NAVEGAÇÃO INTERATIVA)
// ==========================================================================
function bindSidebarNav() {
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');

      const tab = link.dataset.tab;
      
      // Alternância de Telas Principais (Início vs Planos vs Atividades vs Relatório Mensal)
      if (tab === 'planos') {
        mostrarAba('planos');
      } else if (tab === 'inicio') {
        mostrarAba('inicio');
      } else if (tab === 'atividades') {
        mostrarAba('atividades');
      } else if (tab === 'relatorios' || tab === 'acompanhamento') {
        mostrarAba('relatorios');
      } else if (tab === 'nutricao') {
        mostrarAba('planos');
      } else if (tab === 'iacoach') {
        abrirModalIACoach();
      } else if (tab === 'perfil') {
        abrirModalPerfil();
      } else if (tab === 'conquistas') {
        abrirModalMetas();
      } else {
        abrirModal("ℹ️ Módulo NutriPlus", `<p style="color:#94A3B8;">A seção <strong>${tab}</strong> está sincronizada com seus dados científicos em tempo real.</p>`);
      }
    });
  });
}

function mostrarAba(nomeAba) {
  document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
  const target = document.getElementById(`view-${nomeAba}`);
  if (target) {
    target.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// Funções da Aba Planos Alimentares
function trocarSubTabPlanos(subTab, btn) {
  document.querySelectorAll('.plan-tab-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  if (subTab === 'receitas') {
    abrirModalCatalogoReceitas();
  } else if (subTab === 'compras') {
    abrirModalListaCompras();
  } else if (subTab === 'substituicoes') {
    abrirModal("🔄 Substituições Inteligentes de Alimentos", `
      <div style="color:#CBD5E1; font-size:14px; line-height:1.6;">
        <p>Trocas equivalentes em macronutrientes preservando o modelo fisiológico:</p>
        <ul style="margin:12px 0 16px 20px;">
          <li><strong>Arroz Integral (100g)</strong> ➔ Batata Doce (130g) ou Mandioca (90g)</li>
          <li><strong>Frango Grelhado (100g)</strong> ➔ Tilápia (120g) ou Patinho Moído (90g)</li>
          <li><strong>Aveia (40g)</strong> ➔ Farelo de Aveia (45g) ou Quinoa em Flocos (35g)</li>
        </ul>
        <div style="background:#091220; padding:12px; border-radius:8px; border:1px solid #1C2B48;">
          💡 <em>O solver calcula as gramas exatas para manter 1.850 kcal/dia.</em>
        </div>
      </div>
    `);
  } else if (subTab === 'favoritos') {
    abrirModal("🤍 Seus Favoritos Salvos", `
      <div style="color:#CBD5E1; font-size:14px;">
        <p>Suas receitas preferidas do canal <strong>@saciara_</strong>:</p>
        <div style="display:flex; flex-direction:column; gap:8px; margin-top:12px;">
          <div style="padding:10px; background:#0B1323; border:1px solid #1C2B48; border-radius:8px;">★ Panqueca de Banana com Canela (180 kcal)</div>
          <div style="padding:10px; background:#0B1323; border:1px solid #1C2B48; border-radius:8px;">★ Bowl de Iogurte com Chia e Frutas (142 kcal)</div>
          <div style="padding:10px; background:#0B1323; border:1px solid #1C2B48; border-radius:8px;">★ Salmão com Legumes no Vapor (354 kcal)</div>
        </div>
      </div>
    `);
  }
}

function selecionarDiaPlano(btn, nomeDia) {
  document.querySelectorAll('.day-pill-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const titleEl = document.getElementById('currentDayTitleText');
  if (titleEl) titleEl.innerText = nomeDia;
}

function navegarSemana(delta) {
  abrirModal("📅 Navegação de Semanas", `
    <div style="color:#CBD5E1; font-size:14px; text-align:center;">
      <p>Você está visualizando a semana do protocolo de emagrecimento adaptativo.</p>
      <div style="font-size:18px; font-weight:800; color:#00D070; margin:14px 0;">Semana 1 / 12 (Fase 1: Definição)</div>
      <p style="font-size:12px; color:#64748B;">Seus planos são recalculados dinamicamente com base nas pesagens.</p>
    </div>
  `);
}

function abrirCalendarioCompleto() {
  abrirModal("🗓️ Calendário Mensal de Refeições", `
    <div style="color:#CBD5E1; font-size:14px;">
      <p>Planejamento de 30 dias sincronizado com os modelos dinâmicos de Kevin Hall e ciclo de recuperação.</p>
      <div style="display:grid; grid-template-columns:repeat(7, 1fr); gap:6px; margin:16px 0; text-align:center; font-size:12px;">
        <div style="color:#64748B;">D</div><div style="color:#64748B;">S</div><div style="color:#64748B;">T</div><div style="color:#64748B;">Q</div><div style="color:#64748B;">Q</div><div style="color:#64748B;">S</div><div style="color:#64748B;">S</div>
        <div style="padding:8px; background:#00D070; color:#070B14; font-weight:800; border-radius:6px;">1</div>
        <div style="padding:8px; background:#00D070; color:#070B14; font-weight:800; border-radius:6px;">2</div>
        <div style="padding:8px; background:#00D070; color:#070B14; font-weight:800; border-radius:6px; box-shadow:0 0 10px #00D070;">3</div>
        <div style="padding:8px; background:#121C30; border-radius:6px;">4</div>
        <div style="padding:8px; background:#121C30; border-radius:6px;">5</div>
        <div style="padding:8px; background:#121C30; border-radius:6px;">6</div>
        <div style="padding:8px; background:#121C30; border-radius:6px;">7</div>
      </div>
    </div>
  `);
}

function abrirModalEditarObjetivo() {
  abrirModal("🎯 Ajustar Objetivo Nutricional", `
    <div style="color:#CBD5E1; font-size:14px;">
      <label style="display:block; margin-bottom:8px; font-weight:700;">Selecione sua meta atual:</label>
      <select style="width:100%; padding:10px; background:#091220; border:1px solid #1C2B48; color:#FFFFFF; border-radius:8px; margin-bottom:14px;">
        <option selected>Definição Saudável (1.850 kcal/dia - Perda Sustentável)</option>
        <option>Déficit Fisiológico Kevin Hall (1.600 kcal/dia - Acelerado)</option>
        <option>Manutenção Metabólica (2.200 kcal/dia)</option>
        <option>Hipertrofia Limpa (2.450 kcal/dia)</option>
      </select>
      <button class="btn-primary" style="width:100%; padding:12px; background:#00D070; color:#070B14; border:none; border-radius:8px; font-weight:800; cursor:pointer;" onclick="fecharModalGlobal()">Salvar e Recalcular Cardápio</button>
    </div>
  `);
}

function trocarReceitaModal(tipoRefeicao) {
  const nomes = {
    cafe: 'Café da Manhã',
    lanche_manha: 'Lanche da Manhã',
    almoco: 'Almoço',
    lanche_tarde: 'Lanche da Tarde',
    jantar: 'Jantar'
  };
  abrirModal(`🔄 Trocar Receita: ${nomes[tipoRefeicao] || 'Refeição'}`, `
    <div style="color:#CBD5E1; font-size:14px;">
      <p>Opções validadas com os mesmos macronutrientes da sua meta:</p>
      <div style="display:flex; flex-direction:column; gap:10px; margin-top:14px;">
        <div style="display:flex; align-items:center; justify-content:space-between; padding:12px; background:#091220; border:1px solid #1C2B48; border-radius:8px;">
          <div>
            <div style="font-weight:700; color:#FFFFFF;">Omelete de Claras com Tomate & Manjericão</div>
            <div style="font-size:11px; color:#64748B;">140 kcal • P: 18g • C: 3g • G: 5g</div>
          </div>
          <button style="background:#00D070; color:#070B14; border:none; padding:6px 12px; border-radius:6px; font-weight:800; cursor:pointer;" onclick="fecharModalGlobal()">Escolher</button>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; padding:12px; background:#091220; border:1px solid #1C2B48; border-radius:8px;">
          <div>
            <div style="font-weight:700; color:#FFFFFF;">Crepioca Fit com Queijo Cottage</div>
            <div style="font-size:11px; color:#64748B;">185 kcal • P: 14g • C: 16g • G: 6g</div>
          </div>
          <button style="background:#00D070; color:#070B14; border:none; padding:6px 12px; border-radius:6px; font-weight:800; cursor:pointer;" onclick="fecharModalGlobal()">Escolher</button>
        </div>
      </div>
    </div>
  `);
}

function abrirModalDicaProteina() {
  abrirModal("💡 Ciência das Proteínas no Emagrecimento", `
    <div style="color:#CBD5E1; font-size:14px; line-height:1.6;">
      <p>De acordo com o modelo de partição tecidual de Forbes e Kevin Hall:</p>
      <ul style="margin:12px 0 16px 20px;">
        <li>Uma ingestão de <strong>1,8 g/kg</strong> de peso corporal protege a massa magra (FFM) contra catabolismo durante o déficit energético.</li>
        <li>O Efeito Térmico dos Alimentos (TEF) das proteínas consome cerca de <strong>20 a 30%</strong> de suas próprias calorias apenas na digestão.</li>
        <li>Maior saciedade hormonal estimulando GLP-1 e PYY.</li>
      </ul>
      <div style="background:#091220; padding:12px; border-radius:8px; border:1px solid #1C2B48;">
        🛒 <strong>Utensílio recomendado:</strong> <a href="https://s.shopee.com.br/10940561_saciara" target="_blank" style="color:#00D070; font-weight:700;">Forma de Silicone Antiaderente para Airfryer na Shopee</a> para preparar carnes sem óleo!
      </div>
    </div>
  `);
}

// ==========================================================================
// 4. MODAIS INTERATIVOS
// ==========================================================================
function abrirModal(titulo, htmlConteudo) {
  const modal = document.getElementById('globalModal');
  const titleEl = document.getElementById('modalTitle');
  const bodyEl = document.getElementById('modalBody');

  if (titleEl) titleEl.innerText = titulo;
  if (bodyEl) bodyEl.innerHTML = htmlConteudo;
  if (modal) modal.style.display = 'flex';
}

function fecharModalGlobal(e) {
  if (!e || e.target.id === 'globalModal' || e.target.classList.contains('modal-close-btn')) {
    const modal = document.getElementById('globalModal');
    if (modal) modal.style.display = 'none';
  }
}

// Modal IA Coach
function abrirModalIACoach() {
  abrirModal("🤖 Seu IA Coach Científico", `
    <div style="background:#091220; padding:16px; border-radius:12px; border:1px solid #1C2B48; margin-bottom:18px;">
      <p style="font-size:14px; color:#F1F5F9; line-height:1.5;">
        "Olá, Ana! Pelo modelo dinâmico de Kevin Hall, sua taxa de adesão nesta semana está em <strong>93%</strong>. Seu déficit médio de -420 kcal/dia já eliminou <strong>3,2 kg</strong> reais de tecido adiposo sem comprometer sua massa magra (49,7 kg)."
      </p>
    </div>

    <h4 style="font-size:15px; font-weight:700; color:#FFF; margin-bottom:10px;">Sugestão para o Jantar de Hoje:</h4>
    <div style="background:#16233D; padding:14px; border-radius:12px; display:flex; gap:14px; align-items:center;">
      <div style="font-size:32px;">🍗</div>
      <div>
        <h5 style="font-size:15px; color:#FFF; font-weight:700;">Frango Grelhado com Cenoura & Ervas</h5>
        <p style="font-size:12px; color:#94A3B8; margin-top:2px;">360 kcal • 38g Proteína • Prático na Airfryer</p>
      </div>
    </div>

    <!-- Card de Utensílio com Link de Afiliado Shopee (Cookie 30 Dias) -->
    <div style="background:linear-gradient(135deg, rgba(0,208,112,0.1), rgba(56,189,248,0.05)); border:1px dashed #00D070; border-radius:12px; padding:14px; margin-top:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <strong style="font-size:13px; color:#FFF;">Dica do Coach:</strong>
          <p style="font-size:12px; color:#94A3B8; margin-top:2px;">Use a forma de silicone para não grudar e eliminar todo o óleo do preparo.</p>
        </div>
        <a href="https://s.shopee.com.br/9zz6HcfAxu" target="_blank" style="background:#00D070; color:#070B14; font-size:11px; font-weight:800; padding:8px 14px; border-radius:20px; text-decoration:none; white-space:nowrap;">
          Ver na Shopee ➔
        </a>
      </div>
    </div>
  `);
}

// Modal Composição Corporal
function abrirModalComposicao() {
  abrirModal("🧍 Composição Corporal Detalhada", `
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:18px;">
      <div style="background:#091220; padding:14px; border-radius:12px; border:1px solid #1C2B48;">
        <span style="font-size:11px; color:#94A3B8;">Massa Magra Protegida</span>
        <h3 style="font-size:22px; color:#00D070; font-weight:800; margin-top:2px;">49,7 kg</h3>
        <span style="font-size:11px; color:#64748B;">70,2% do corpo</span>
      </div>
      <div style="background:#091220; padding:14px; border-radius:12px; border:1px solid #1C2B48;">
        <span style="font-size:11px; color:#94A3B8;">Massa Gorda (FM)</span>
        <h3 style="font-size:22px; color:#FB923C; font-weight:800; margin-top:2px;">21,1 kg</h3>
        <span style="font-size:11px; color:#64748B;">28,0% do corpo</span>
      </div>
    </div>

    <div style="background:#16233D; padding:16px; border-radius:12px;">
      <h4 style="font-size:14px; color:#FFF; font-weight:700;">Partição Dinâmica de Forbes:</h4>
      <p style="font-size:12px; color:#94A3B8; margin-top:6px; line-height:1.5;">
        Com seu percentual de 28% de gordura, para cada 1 kg perdido, <strong>840 gramas</strong> são de pura gordura e apenas 160g de fluidos/tecido ativo, garantindo um emagrecimento estético sem flacidez.
      </p>
    </div>

    <div style="margin-top:16px;">
      <a href="https://s.shopee.com.br/9zz6HcfAxu" target="_blank" style="display:block; text-align:center; background:#1C2B48; color:#00D070; border:1px solid #00D070; padding:10px; border-radius:10px; font-weight:700; font-size:13px; text-decoration:none;">
        Balança de Alta Precisão com Bioimpedância na Shopee ➔
      </a>
    </div>
  `);
}

// Modal Plano Completo de Refeições
function abrirModalPlanoCompleto() {
  abrirModal("🥗 Plano Alimentar & Receitas Saciara", `
    <p style="font-size:13px; color:#94A3B8; margin-bottom:14px;">
      Acesse o cronograma semanal completo com as 156 receitas práticas calculadas:
    </p>

    <div style="display:flex; flex-direction:column; gap:10px; max-height:360px; overflow-y:auto;">
      <div style="background:#16233D; padding:12px 14px; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <strong style="font-size:14px; color:#FFF;">Café da Manhã: Crepioca de Ricota</strong>
          <div style="font-size:11px; color:#94A3B8;">240 kcal • 18g Proteína • 7 min</div>
        </div>
        <span style="color:#00D070; font-size:12px; font-weight:700;">Concluído ✓</span>
      </div>

      <div style="background:#16233D; padding:12px 14px; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <strong style="font-size:14px; color:#FFF;">Almoço: Frango Grelhado com Salada e Arroz</strong>
          <div style="font-size:11px; color:#94A3B8;">420 kcal • 42g Proteína • 20 min</div>
        </div>
        <span style="color:#00D070; font-size:12px; font-weight:700;">Concluído ✓</span>
      </div>

      <div style="background:#16233D; padding:12px 14px; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <strong style="font-size:14px; color:#FFF;">Lanche: Taça de Banana com Cacau 100%</strong>
          <div style="font-size:11px; color:#94A3B8;">180 kcal • 8g Proteína • 5 min</div>
        </div>
        <span style="color:#FB923C; font-size:12px; font-weight:700;">16:30 h</span>
      </div>

      <div style="background:#16233D; padding:12px 14px; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <strong style="font-size:14px; color:#FFF;">Jantar: Sopa Nutritiva de Lentilha e Abóbora</strong>
          <div style="font-size:11px; color:#94A3B8;">290 kcal • 16g Proteína • 25 min</div>
        </div>
        <span style="color:#38BDF8; font-size:12px; font-weight:700;">20:00 h</span>
      </div>
    </div>

    <div style="margin-top:16px;">
      <a href="https://s.shopee.com.br/7fbBlr9zK9" target="_blank" style="display:block; text-align:center; background:#00D070; color:#070B14; font-weight:800; padding:12px; border-radius:10px; text-decoration:none;">
        Kit de Marmitas Herméticas na Shopee ➔
      </a>
    </div>
  `);
}

// Modal Metas da Semana
function abrirModalMetas() {
  abrirModal("🎯 Metas e Conquistas da Semana", `
    <div style="background:#091220; padding:16px; border-radius:12px; border:1px solid #1C2B48; margin-bottom:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:14px; font-weight:700; color:#FFF;">Progresso Geral</span>
        <span style="font-size:16px; font-weight:800; color:#00D070;">85%</span>
      </div>
      <div style="width:100%; height:8px; background:#1C2B48; border-radius:4px; margin-top:8px; overflow:hidden;">
        <div style="width:85%; height:100%; background:linear-gradient(90deg,#00D070,#38BDF8);"></div>
      </div>
    </div>

    <div style="display:flex; flex-direction:column; gap:8px;">
      <div style="background:#16233D; padding:12px; border-radius:8px; font-size:13px; color:#FFF;">✔ Consumir 1,5L de água por dia (Bateu 2,0L hoje!)</div>
      <div style="background:#16233D; padding:12px; border-radius:8px; font-size:13px; color:#FFF;">✔ 3 treinos de musculação/caminhada (Concluídos)</div>
      <div style="background:#16233D; padding:12px; border-radius:8px; font-size:13px; color:#FFF;">⏳ Manter média de 1.600 kcal/dia (Hoje: 1.450 kcal)</div>
    </div>
  `);
}

// Modal Evolução
function abrirModalEvolucao() {
  abrirModal("📈 Relatório de Evolução Mensal", `
    <div style="text-align:center; padding:16px 0;">
      <div style="font-size:42px;">🏆</div>
      <h3 style="font-size:24px; font-weight:800; color:#FFF; margin-top:8px;">-3,2 kg Eliminados</h3>
      <p style="font-size:13px; color:#94A3B8; margin-top:4px;">Nos últimos 30 dias de acompanhamento científico</p>
    </div>

    <div style="background:#091220; padding:14px; border-radius:12px; margin-top:14px; font-size:13px; color:#CBD5E1; line-height:1.5;">
      • <strong>Média Semanal:</strong> -800 gramas por semana.<br>
      • <strong>Adaptação Fisiológica:</strong> Gasto basal preservado com alta ingestão de proteínas (95g/dia).<br>
      • <strong>Previsão de Chegada na Meta (70,0 kg):</strong> Apenas 8 a 12 dias restantes!
    </div>
  `);
}

// Modal Upgrade Premium
function abrirModalPremium() {
  abrirModal("👑 NutriPlus Premium", `
    <div style="text-align:center; padding:12px 0;">
      <h3 style="font-size:22px; font-weight:800; color:#FFF;">Desbloqueie o Poder Total</h3>
      <p style="font-size:13px; color:#94A3B8; margin-top:4px;">Acesso ao IA Coach 24h, Cardápios Ilimitados e Leitor de Pratos por Foto.</p>
    </div>

    <div style="background:#091220; border:2px solid #00D070; border-radius:14px; padding:18px; margin:16px 0; text-align:center;">
      <span style="font-size:11px; font-weight:800; color:#00D070; text-transform:uppercase;">Plano Anual Mais Popular</span>
      <div style="font-size:32px; font-weight:800; color:#FFF; margin:6px 0;">R$ 19,90 <small style="font-size:14px; font-weight:500; color:#94A3B8;">/mês</small></div>
      <p style="font-size:12px; color:#94A3B8;">Menos de 70 centavos por dia para transformar seu corpo.</p>
    </div>

    <button onclick="alert('Redirecionando para checkout seguro...')" style="width:100%; background:#00D070; color:#070B14; font-size:14px; font-weight:800; padding:14px; border-radius:12px; border:none; cursor:pointer;">
      Garantir Acesso Premium Agora ➔
    </button>
  `);
}

// Modal Notificações
function abrirNotificacoes() {
  abrirModal("🔔 Suas Notificações", `
    <div style="display:flex; flex-direction:column; gap:10px;">
      <div style="background:#16233D; padding:14px; border-radius:10px; border-left:3px solid #00D070;">
        <strong style="font-size:13px; color:#FFF;">Déficit calórico de ontem atingido!</strong>
        <p style="font-size:12px; color:#94A3B8; margin-top:2px;">Você fechou o dia em 1.520 kcal (-480 kcal da meta). Excelente consistência!</p>
        <span style="font-size:10px; color:#64748B;">Há 3 horas</span>
      </div>

      <div style="background:#16233D; padding:14px; border-radius:10px; border-left:3px solid #38BDF8;">
        <strong style="font-size:13px; color:#FFF;">Lembrete de Hidratação 💧</strong>
        <p style="font-size:12px; color:#94A3B8; margin-top:2px;">Beba 400ml de água agora para manter seu metabolismo ativo.</p>
        <span style="font-size:10px; color:#64748B;">Há 5 horas</span>
      </div>
    </div>
  `);
}

// Modal Perfil
function abrirModalPerfil() {
  abrirModal("👤 Meu Perfil Nutricional", `
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:18px;">
      <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80" style="width:60px; height:60px; border-radius:50%; border:2px solid #00D070;">
      <div>
        <h4 style="font-size:17px; font-weight:800; color:#FFF;">Ana Paula</h4>
        <span style="font-size:12px; color:#00D070; font-weight:700;">Plano Ativo: Emagrecimento Científico</span>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:13px;">
      <div style="background:#091220; padding:10px; border-radius:8px;"><span style="color:#94A3B8;">Idade:</span> <strong style="color:#FFF;">28 anos</strong></div>
      <div style="background:#091220; padding:10px; border-radius:8px;"><span style="color:#94A3B8;">Altura:</span> <strong style="color:#FFF;">168 cm</strong></div>
      <div style="background:#091220; padding:10px; border-radius:8px;"><span style="color:#94A3B8;">Peso Atual:</span> <strong style="color:#FFF;">70,8 kg</strong></div>
      <div style="background:#091220; padding:10px; border-radius:8px;"><span style="color:#94A3B8;">Meta Final:</span> <strong style="color:#FFF;">70,0 kg</strong></div>
    </div>
  `);
}

// Busca Global
function handleSearch(query) {
  if (!query) return;
  const q = query.toLowerCase();
  if (q.includes('frango') || q.includes('receita') || q.includes('almoço')) {
    abrirModalPlanoCompleto();
  } else if (q.includes('peso') || q.includes('meta')) {
    abrirModalEvolucao();
  } else if (q.includes('treino') || q.includes('atividade') || q.includes('exercício')) {
    mostrarAba('atividades');
  }
}

// ==========================================================================
// FUNÇÕES DA ABA DE ATIVIDADES FÍSICAS (RÉPLICA PIXEL-A-PIXEL)
// ==========================================================================
function trocarSubTabAtiv(subTab, btn) {
  document.querySelectorAll('#view-atividades .plan-tab-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  if (subTab === 'treinos') {
    abrirCatalogoTreinos();
  } else if (subTab === 'atividades') {
    abrirModal("🎯 Registro de Atividades Diárias", `
      <div style="color:#CBD5E1; font-size:14px;">
        <p>Atividades sincronizadas via GPS e acelerômetro:</p>
        <div style="display:flex; flex-direction:column; gap:8px; margin-top:12px;">
          <div style="padding:12px; background:#091220; border:1px solid #1C2B48; border-radius:8px; display:flex; justify-content:space-between;">
            <span>🚶 Caminhada Rápida no Parque</span>
            <strong style="color:#00D070;">4,2 km • 328 kcal</strong>
          </div>
          <div style="padding:12px; background:#091220; border:1px solid #1C2B48; border-radius:8px; display:flex; justify-content:space-between;">
            <span>🏋️ Treino de Força Membros Inferiores</span>
            <strong style="color:#00D070;">45 min • 210 kcal</strong>
          </div>
        </div>
      </div>
    `);
  } else if (subTab === 'historico') {
    abrirModal("⏱️ Histórico de Treinos", `
      <div style="color:#CBD5E1; font-size:14px;">
        <p>Sua consistência nas últimas 4 semanas:</p>
        <div style="font-size:18px; font-weight:800; color:#00D070; margin:14px 0;">22 treinos completados (92% de adesão)</div>
        <p style="font-size:12px; color:#64748B;">Seu NEAT e gasto por atividade física (AEE) estão acelerando a partição tecidual segundo o modelo Kevin Hall.</p>
      </div>
    `);
  } else if (subTab === 'conquistas') {
    abrirModalMetas();
  }
}

function selecionarSemanaAtiv(val) {
  abrirModal("📅 Semana de Treinos Selecionada", `
    <div style="color:#CBD5E1; font-size:14px; text-align:center;">
      <p>Você selecionou o ciclo: <strong>${val}</strong></p>
      <div style="margin:16px 0; padding:12px; background:#091220; border:1px solid #00D070; border-radius:8px; color:#00D070; font-weight:800;">
        Foco: Aumento de Capacidade Aeróbica + Preservação de Massa Magra
      </div>
      <button style="background:#00D070; color:#070B14; border:none; padding:10px 20px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="fecharModalGlobal()">Aplicar ao Cronograma</button>
    </div>
  `);
}

function abrirModalConcluido(nomeEx) {
  abrirModal(`✅ ${nomeEx} Concluído!`, `
    <div style="color:#CBD5E1; font-size:14px; text-align:center;">
      <div style="font-size:48px; margin-bottom:10px;">🎉</div>
      <h3 style="color:#FFFFFF; margin-bottom:6px;">Parabéns, Ana!</h3>
      <p>Você completou sua meta com <strong>328 kcal gastas</strong> em ritmo moderado.</p>
      <div style="background:#091220; border:1px solid #1C2B48; padding:12px; border-radius:8px; margin:16px 0; font-size:12px; color:#00D070;">
        🔥 Sua sequência diária aumentou para 7 dias ininterruptos!
      </div>
      <button style="background:#00D070; color:#070B14; border:none; padding:10px 20px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="fecharModalGlobal()">Fechar</button>
    </div>
  `);
}

function iniciarTreinoModal(nomeTreino) {
  abrirModal(`🏋️ Iniciar: Treino de ${nomeTreino}`, `
    <div style="color:#CBD5E1; font-size:14px;">
      <p style="margin-bottom:12px;">Série prescrita pelo seu IA Coach Científico:</p>
      <ol style="margin-left:20px; line-height:1.8;">
        <li>Agachamento Livre — 3x 12 repetições</li>
        <li>Passada com Halteres — 3x 10 repetições cada perna</li>
        <li>Elevação Pélvica — 3x 15 repetições (isometria 2s)</li>
        <li>Stiff com Barra — 3x 12 repetições</li>
      </ol>
      <div style="background:#091220; padding:12px; border-radius:8px; border:1px solid #1C2B48; margin:16px 0;">
        🛒 <strong>Acessório recomendado:</strong> <a href="https://s.shopee.com.br/10940561_saciara" target="_blank" style="color:#00D070; font-weight:700;">Kit de Mini Bands Elásticas na Shopee</a> para intensificar ativação de glúteos!
      </div>
      <button style="width:100%; background:#00D070; color:#070B14; border:none; padding:12px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="abrirModalConcluido('Treino de ' + '${nomeTreino}')">Marcar Treino como Finalizado ✓</button>
    </div>
  `);
}

function agendarTreinoModal(nomeTreino) {
  abrirModal(`⏱️ Agendar: ${nomeTreino}`, `
    <div style="color:#CBD5E1; font-size:14px;">
      <label style="display:block; margin-bottom:8px; font-weight:700;">Horário ideal para o lembrete:</label>
      <input type="time" value="07:30" style="width:100%; padding:10px; background:#091220; border:1px solid #1C2B48; color:#FFFFFF; border-radius:8px; margin-bottom:14px;">
      <label style="display:flex; align-items:center; gap:8px; margin-bottom:14px; font-size:12px;">
        <input type="checkbox" checked> Enviar notificação push 15 min antes
      </label>
      <button style="width:100%; background:#00D070; color:#070B14; border:none; padding:12px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="fecharModalGlobal()">Confirmar Agendamento</button>
    </div>
  `);
}

function registrarAtividadeModal() {
  abrirModal("❤️ Registrar Atividade Livre", `
    <div style="color:#CBD5E1; font-size:14px;">
      <label style="display:block; margin-bottom:6px; font-weight:700;">Modalidade:</label>
      <select style="width:100%; padding:10px; background:#091220; border:1px solid #1C2B48; color:#FFFFFF; border-radius:8px; margin-bottom:12px;">
        <option>Dança / Zumba</option>
        <option>Natação</option>
        <option>Pilates / Yoga</option>
        <option>Esportes de Areia (Beach Tennis)</option>
        <option>Passeio com Pet</option>
      </select>
      <label style="display:block; margin-bottom:6px; font-weight:700;">Duração estimada (minutos):</label>
      <input type="number" value="45" style="width:100%; padding:10px; background:#091220; border:1px solid #1C2B48; color:#FFFFFF; border-radius:8px; margin-bottom:16px;">
      <button style="width:100%; background:#00D070; color:#070B14; border:none; padding:12px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="abrirModalConcluido('Atividade Livre')">Salvar e Somar aos Gastos Diários</button>
    </div>
  `);
}

function abrirCatalogoTreinos() {
  abrirModal("🏋️ Catálogo de Treinos HIIT & Força", `
    <div style="color:#CBD5E1; font-size:14px;">
      <p style="margin-bottom:12px;">Treinos orientados para queima máxima em casa ou academia:</p>
      <div style="display:flex; flex-direction:column; gap:10px;">
        <div style="padding:12px; background:#091220; border:1px solid #1C2B48; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-weight:700; color:#FFFFFF;">HIIT Queima Rápida (Tabata)</div>
            <div style="font-size:11px; color:#64748B;">15 min • 200 kcal • Sem equipamentos</div>
          </div>
          <button style="background:#00D070; color:#070B14; border:none; padding:6px 12px; border-radius:6px; font-weight:800; cursor:pointer;" onclick="iniciarTreinoModal('HIIT Tabata')">Iniciar</button>
        </div>
        <div style="padding:12px; background:#091220; border:1px solid #1C2B48; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-weight:700; color:#FFFFFF;">GAP (Glúteos, Abdômen e Pernas)</div>
            <div style="font-size:11px; color:#64748B;">30 min • 280 kcal • Intermediário</div>
          </div>
          <button style="background:#00D070; color:#070B14; border:none; padding:6px 12px; border-radius:6px; font-weight:800; cursor:pointer;" onclick="iniciarTreinoModal('GAP')">Iniciar</button>
        </div>
      </div>
    </div>
  `);
}

function abrirModalDicaMetabolismo() {
  abrirModal("💡 Metabolismo e Preservação de Massa Magra", `
    <div style="color:#CBD5E1; font-size:14px; line-height:1.6;">
      <p>Estudos clínicos do NIH e o modelo Kevin Hall demonstram que:</p>
      <ul style="margin:12px 0 16px 20px;">
        <li>O treino resistido (musculação) sinaliza ao organismo a preservação da massa muscular livre de gordura (FFM), desviando o catabolismo quase 100% para o tecido adiposo.</li>
        <li>O EPOC (Consumo Excessivo de Oxigênio Pós-Exercício) do treino HIIT mantém seu metabolismo elevado por até 14 horas após o término da sessão.</li>
      </ul>
      <div style="background:#091220; padding:12px; border-radius:8px; border:1px solid #1C2B48;">
        🛒 <strong>Recomendação Oficial:</strong> <a href="https://s.shopee.com.br/10940561_saciara" target="_blank" style="color:#00D070; font-weight:700;">Smartwatch com Medidor Cardíaco na Shopee</a> para calibrar suas zonas de frequência cardíaca!
      </div>
    </div>
  `);
}

function alterarPeriodoProgresso(periodo) {
  abrirModal("📊 Progresso Filtrado", `
    <div style="color:#CBD5E1; font-size:14px; text-align:center;">
      <p>Visualizando métricas consolidadas para: <strong>${periodo}</strong></p>
      <div style="font-size:24px; font-weight:800; color:#00D070; margin:14px 0;">78% da Meta Atingida</div>
      <p style="font-size:12px; color:#64748B;">Seu condicionamento físico progrediu 2 níveis neste ciclo.</p>
    </div>
  `);
}

// ==========================================================================
// FUNÇÕES DO RELATÓRIO DE EVOLUÇÃO MENSAL (RÉPLICA PIXEL-A-PIXEL)
// ==========================================================================
function abrirSeletorMes() {
  abrirModal("📅 Selecionar Mês do Relatório", `
    <div style="color:#CBD5E1; font-size:14px;">
      <p style="margin-bottom:12px;">Escolha o mês consolidado para auditar sua evolução fisiológica:</p>
      <div style="display:flex; flex-direction:column; gap:8px;">
        <button style="display:flex; justify-content:space-between; padding:12px; background:#091220; border:1px solid #00D070; border-radius:8px; color:#FFFFFF; font-weight:700; cursor:pointer;" onclick="fecharModalGlobal()">
          <span>Novembro de 2026 (Atual)</span>
          <span style="color:#00D070;">Ativo ✓</span>
        </button>
        <button style="display:flex; justify-content:space-between; padding:12px; background:#091220; border:1px solid #1C2B48; border-radius:8px; color:#94A3B8; font-weight:700; cursor:pointer;" onclick="fecharModalGlobal()">
          <span>Outubro de 2026</span>
          <span style="color:#64748B;">71,0 kg (-2,4 kg)</span>
        </button>
        <button style="display:flex; justify-content:space-between; padding:12px; background:#091220; border:1px solid #1C2B48; border-radius:8px; color:#94A3B8; font-weight:700; cursor:pointer;" onclick="fecharModalGlobal()">
          <span>Setembro de 2026</span>
          <span style="color:#64748B;">73,4 kg (-2,1 kg)</span>
        </button>
      </div>
    </div>
  `);
}

function abrirModalPlanoDezembro() {
  abrirModal("🚀 Planejamento Estratégico para Dezembro", `
    <div style="color:#CBD5E1; font-size:14px; line-height:1.6;">
      <div style="text-align:center; margin-bottom:16px;">
        <div style="font-size:36px;">🎯</div>
        <h3 style="color:#FFFFFF; margin-top:6px;">Meta para Dezembro: 67,3 kg (-1,0 kg)</h3>
        <p style="color:#00D070; font-weight:700; font-size:12px;">Estratégia Anti-Estagnação Fisiológica de Kevin Hall</p>
      </div>
      <p>Com a redução de peso de 68,3 kg alcançada em novembro, seu metabolismo basal reduziu proporcionalmente. Para manter a perda sem queda do gasto energético (termogênese adaptativa):</p>
      <ul style="margin:12px 0 16px 20px;">
        <li>Ajuste calórico suave: <strong>1.780 kcal/dia</strong> (preservando 130g de proteína).</li>
        <li>Introdução de 2 sessões semanais de HIIT de 15 minutos para elevar o EPOC.</li>
        <li>Refeição livre estratégica (Refeed de Carboidratos) a cada 14 dias para restabelecer leptina e T3 livre.</li>
      </ul>
      <div style="background:#091220; padding:12px; border-radius:8px; border:1px solid #1C2B48; margin-bottom:16px;">
        🛒 <strong>Kit de apoio:</strong> <a href="https://s.shopee.com.br/10940561_saciara" target="_blank" style="color:#00D070; font-weight:700;">Garrafa Térmica Motivacional 2L com Marcador de Horas na Shopee</a> para bater sua meta hídrica de 95% em dezembro!
      </div>
      <button style="width:100%; background:#00D070; color:#070B14; border:none; padding:12px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="fecharModalGlobal()">Ativar Cronograma de Dezembro ✓</button>
    </div>
  `);
}
