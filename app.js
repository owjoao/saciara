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
    </svg>

    <!-- Badge Flutuante de Peso Atual Exato -->
    <div class="chart-badge-weight" style="left:${lastX - 25}px; top:${lastY - 28}px;">
      70,8 kg
    </div>
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
      if (tab === 'nutricao' || tab === 'planos') {
        abrirModalPlanoCompleto();
      } else if (tab === 'iacoach') {
        abrirModalIACoach();
      } else if (tab === 'acompanhamento' || tab === 'relatorios') {
        abrirModalEvolucao();
      } else if (tab === 'perfil') {
        abrirModalPerfil();
      } else if (tab === 'conquistas') {
        abrirModalMetas();
      }
    });
  });
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
  }
}
