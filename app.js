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
      
      // Alternância de Telas Principais (Início vs Planos vs Compras vs Atividades vs Relatório Mensal)
      if (tab === 'planos') {
        mostrarAba('planos');
      } else if (tab === 'compras') {
        mostrarAba('compras');
        recalcularPlanoECompras();
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
      } else if (tab === 'jornada') {
        mostrarAba('jornada');
      } else if (tab === 'conquistas') {
        mostrarAba('jornada');
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

  // Sincroniza links da sidebar
  document.querySelectorAll('.nav-link').forEach(l => {
    if (l.dataset.tab === nomeAba) {
      l.classList.add('active');
    } else {
      l.classList.remove('active');
    }
  });

  // Sincroniza botões do Bottom Dock Mobile
  document.querySelectorAll('.dock-item').forEach(d => {
    if (d.dataset.dock === nomeAba) {
      d.classList.add('active');
    } else {
      d.classList.remove('active');
    }
  });
}

// Navegação exclusiva da Thumb Zone Mobile
function navegarTabMobile(tab) {
  fecharSidebarMobile();
  if (tab === 'compras') {
    mostrarAba('compras');
    recalcularPlanoECompras();
  } else if (tab === 'planos') {
    mostrarAba('planos');
  } else if (tab === 'inicio') {
    mostrarAba('inicio');
  } else if (tab === 'atividades') {
    mostrarAba('atividades');
  } else if (tab === 'iacoach') {
    abrirModalIACoach();
  }
}

// Controle da Sidebar no Celular (Menu Hambúrguer & Backdrop)
function toggleSidebarMobile() {
  const sidebar = document.querySelector('.sidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  if (!sidebar) return;

  const isOpen = sidebar.classList.contains('open');
  if (isOpen) {
    fecharSidebarMobile();
  } else {
    sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function fecharSidebarMobile() {
  const sidebar = document.querySelector('.sidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  if (sidebar) sidebar.classList.remove('open');
  if (backdrop) backdrop.classList.remove('active');
  document.body.style.overflow = '';
}

// Atalho: Rola suavemente até a Refeição Atual com destaque visual
function scrollParaRefeicaoAtual() {
  const box = document.getElementById('refeicaoMomentoBox');
  if (box) {
    box.scrollIntoView({ behavior: 'smooth', block: 'center' });
    box.classList.remove('highlight-pulse-anim');
    void box.offsetWidth; // Força reflow para reiniciar animação
    box.classList.add('highlight-pulse-anim');
    mostrarToastFeedback('🍽️ Prato deste horário em destaque!');
  }
}

// Modal Rápido de Registro de Peso com Steppers para Celular
let pesoTempRegistro = 70.8;
function abrirModalRegistrarPesoRapido() {
  pesoTempRegistro = AppState.profile.pesoAtual || 70.8;
  abrirModal("⚖️ Registrar Peso de Hoje", `
    <div style="text-align:center; padding:10px 0;">
      <p style="font-size:13px; color:#94A3B8; margin-bottom:16px;">
        Pese-se sempre em jejum pela manhã. Nosso modelo com <strong>Filtro de Kalman</strong> neutraliza o ruído diário de líquidos.
      </p>

      <!-- Stepper Grande de Toque Fácil -->
      <div style="display:flex; justify-content:center; align-items:center; gap:16px; margin:20px 0;">
        <button style="width:52px; height:52px; border-radius:12px; background:#1C2B48; color:#FFF; font-size:24px; font-weight:800; border:none; cursor:pointer;" onclick="ajustarPesoStepper(-0.1)">-</button>
        <div style="background:#121B2E; border:2px solid #00D070; border-radius:14px; padding:12px 24px;">
          <span id="displayPesoInput" style="font-size:32px; font-weight:800; color:#FFFFFF;">${pesoTempRegistro.toFixed(1).replace('.', ',')}</span>
          <span style="font-size:16px; font-weight:600; color:#00D070; margin-left:4px;">kg</span>
        </div>
        <button style="width:52px; height:52px; border-radius:12px; background:#1C2B48; color:#FFF; font-size:24px; font-weight:800; border:none; cursor:pointer;" onclick="ajustarPesoStepper(0.1)">+</button>
      </div>

      <!-- Pílulas Rápidas de Ajuste com 1 Toque -->
      <div style="display:flex; justify-content:center; gap:8px; margin-bottom:20px; flex-wrap:wrap;">
        <button style="padding:6px 12px; border-radius:8px; background:#121B2E; border:1px solid #1C2B48; color:#94A3B8; font-size:12px; cursor:pointer;" onclick="ajustarPesoStepper(-0.5)">-0,5 kg</button>
        <button style="padding:6px 12px; border-radius:8px; background:#121B2E; border:1px solid #1C2B48; color:#94A3B8; font-size:12px; cursor:pointer;" onclick="ajustarPesoStepper(-0.2)">-0,2 kg</button>
        <button style="padding:6px 12px; border-radius:8px; background:#121B2E; border:1px solid #1C2B48; color:#38BDF8; font-size:12px; cursor:pointer;" onclick="definirPesoExato(70.8)">Manter 70,8</button>
        <button style="padding:6px 12px; border-radius:8px; background:#121B2E; border:1px solid #1C2B48; color:#94A3B8; font-size:12px; cursor:pointer;" onclick="ajustarPesoStepper(0.2)">+0,2 kg</button>
      </div>

      <button style="width:100%; padding:14px; background:#00D070; color:#070B14; font-size:15px; font-weight:800; border:none; border-radius:12px; cursor:pointer; box-shadow:0 4px 14px rgba(0,208,112,0.4);" onclick="confirmarRegistroPeso()">
        ✓ Salvar e Atualizar Gráfico
      </button>
    </div>
  `);
}

function ajustarPesoStepper(delta) {
  pesoTempRegistro = Math.max(40, Math.min(200, Math.round((pesoTempRegistro + delta) * 10) / 10));
  const el = document.getElementById('displayPesoInput');
  if (el) el.innerText = pesoTempRegistro.toFixed(1).replace('.', ',');
}

function definirPesoExato(val) {
  pesoTempRegistro = val;
  const el = document.getElementById('displayPesoInput');
  if (el) el.innerText = pesoTempRegistro.toFixed(1).replace('.', ',');
}

function confirmarRegistroPeso() {
  AppState.profile.pesoAtual = pesoTempRegistro;
  
  // Atualiza última posição do histórico de 30D
  if (SeriesPeso['30D']) {
    SeriesPeso['30D'][SeriesPeso['30D'].length - 1] = pesoTempRegistro;
  }
  
  renderWeightChart(AppState.currentPeriod || '30D');

  // Atualiza pill na tela de início
  const pillPeso = document.getElementById('pillPesoSub');
  if (pillPeso) pillPeso.innerText = `Hoje ${pesoTempRegistro.toFixed(1).replace('.', ',')} kg`;

  fecharModalGlobal();
  mostrarToastFeedback(`⚖️ Peso de ${pesoTempRegistro.toFixed(1).replace('.', ',')} kg salvo com sucesso!`);
}

// Toast de feedback visual universal
function mostrarToastFeedback(mensagem) {
  const toast = document.createElement('div');
  toast.innerText = mensagem;
  toast.style.position = 'fixed';
  toast.style.bottom = '84px'; // Acima do bottom dock no mobile
  toast.style.left = '50%';
  toast.style.transform = 'translateX(-50%)';
  toast.style.background = '#00D070';
  toast.style.color = '#070B14';
  toast.style.fontWeight = '800';
  toast.style.fontSize = '13px';
  toast.style.padding = '10px 20px';
  toast.style.borderRadius = '20px';
  toast.style.boxShadow = '0 6px 20px rgba(0,0,0,0.5)';
  toast.style.zIndex = '99999';
  toast.style.pointerEvents = 'none';
  toast.style.whiteSpace = 'nowrap';
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 2200);
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

// ==========================================================================
// FUNÇÕES DA ABA DE INÍCIO OTIMIZADA (ROTINA DIÁRIA, ÁGUA & PERDA DE PESO)
// ==========================================================================
let aguaConsumidaMl = 2100;
const metaAguaMl = 2500;

function adicionarAguaRapida(quantidadeMl) {
  aguaConsumidaMl = Math.min(aguaConsumidaMl + quantidadeMl, 4000);
  const litros = (aguaConsumidaMl / 1000).toFixed(1).replace('.', ',');
  const pct = Math.min(Math.round((aguaConsumidaMl / metaAguaMl) * 100), 100);

  const valEl = document.getElementById('inicioWaterVal');
  const barEl = document.getElementById('inicioWaterBar');
  const statusEl = document.getElementById('inicioWaterStatus');
  const pillAgua = document.getElementById('pillAguaSub');

  if (valEl) valEl.innerHTML = `${litros} <span style="font-size:16px; font-weight:600; color:#64748B;">/ 2,5 L</span>`;
  if (pillAgua) pillAgua.innerText = `${litros} / 2,5 L`;
  if (barEl) barEl.style.width = `${pct}%`;
  if (statusEl) {
    if (pct >= 100) {
      statusEl.innerHTML = "Meta batida! 🎉";
      statusEl.style.color = "#00D070";
      statusEl.style.background = "rgba(0,208,112,0.15)";
    } else {
      statusEl.innerHTML = `${pct}% da meta`;
    }
  }

  mostrarToastFeedback(`💧 +${quantidadeMl} ml adicionados! Total: ${litros}L`);
}

function toggleRefeicaoFeita(btn) {
  btn.classList.toggle('checked');
  if (btn.classList.contains('checked')) {
    btn.innerHTML = '<span>✓</span> <span>Consumido!</span>';
    btn.style.background = '#00D070';
    btn.style.color = '#070B14';
  } else {
    btn.innerHTML = '<span>✓</span> <span>Consumido</span>';
    btn.style.background = 'rgba(0, 208, 112, 0.1)';
    btn.style.color = '#00D070';
  }
}

function abrirModalDicaPerdaPeso() {
  abrirModal("⚖️ Fisiologia da Perda de Peso Sem Estresse", `
    <div style="color:#CBD5E1; font-size:14px; line-height:1.6;">
      <h3 style="color:#FFFFFF; margin-bottom:8px;">Por que o peso oscila todos os dias?</h3>
      <p>Estudos clínicos rigorosos do National Institutes of Health (NIH) conduzidos pelo Dr. Kevin Hall demonstram que:</p>
      <ul style="margin:12px 0 16px 20px;">
        <li>Para queimar <strong>1 kg de pura gordura corporal</strong>, é necessário oxidar cerca de 7.700 kcal de déficit acumulado.</li>
        <li>Oscilações de peso de um dia para o outro refletem 95% de retenção de água, glicogênio muscular (cada 1g de glicogênio retém 3g de água) e bolo digestivo.</li>
        <li>Seguir sua rotina diária alimentar prescrita e manter sua hidratação garante a queima silenciosa e contínua de gordura.</li>
      </ul>
      <div style="background:#091220; padding:12px; border-radius:8px; border:1px solid #1C2B48;">
        💡 <strong>Recomendação Científica:</strong> Suba na balança apenas uma vez a cada 15 ou 30 dias, sempre pela manhã em jejum. Viva o seu dia a dia com leveza!
      </div>
    </div>
  `);
}

// ==========================================================================
// HIERARQUIA POR HORÁRIO: REFEIÇÃO DESTAQUE ATRELADA À HORA DO DIA
// ==========================================================================
const CatalogoReceitasDetalhes = {
  aveia_banana: {
    titulo: "Aveia com Banana, Canela e Chia",
    horario: "07:00 – 08:00 (Café da Manhã)",
    tipo: "Café da Manhã",
    calorias: "326 kcal",
    macros: "P: 12g • C: 52g • G: 8g",
    ingredientes: [
      "1 xícara de aveia em flocos finos (40g)",
      "1 banana nanica ou prata média fatiada",
      "1 colher de chá de sementes de chia (5g)",
      "Canela em pó a gosto",
      "150 ml de água quente ou leite desnatado/vegetal"
    ],
    passos: [
      "Coloque a aveia e a chia em um bowl e adicione o líquido quente.",
      "Misture bem até hidratar e atingir consistência cremosa de mingau (cerca de 2 minutos).",
      "Disponha as rodelas de banana por cima.",
      "Salpique canela a gosto para estimular o efeito termogênico natural e saboreie quente."
    ],
    imagem: "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?auto=format&fit=crop&w=600&q=80",
    utensilio: "Balança Digital de Cozinha de Alta Precisão",
    utensilioLink: "https://s.shopee.com.br/10940561_saciara"
  },
  iogurte_frutas: {
    titulo: "Iogurte Natural com Frutas Vermelhas",
    horario: "10:30 – 11:30 (Lanche da Manhã)",
    tipo: "Lanche da Manhã",
    calorias: "142 kcal",
    macros: "P: 10g • C: 14g • G: 4g",
    ingredientes: [
      "1 pote de iogurte natural desnatado sem açúcar (170g)",
      "50g de frutas vermelhas (morangos picados ou mirtilos)",
      "Folhas de hortelã para decorar (opcional)"
    ],
    passos: [
      "Despeje o iogurte natural em uma taça ou pote de vidro.",
      "Lave as frutas vermelhas e corte os morangos em lâminas.",
      "Cubra o iogurte com as frutas frescas para manter a crocância e frescor."
    ],
    imagem: "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=600&q=80",
    utensilio: "Conjunto de Potes Herméticos de Vidro",
    utensilioLink: "https://s.shopee.com.br/10940561_saciara"
  },
  frango_arroz: {
    titulo: "Frango Grelhado, Arroz Integral & Salada Colorida",
    horario: "12:30 – 14:00 (Almoço)",
    tipo: "Almoço",
    calorias: "436 kcal",
    macros: "P: 38g • C: 45g • G: 12g",
    ingredientes: [
      "100g de peito de frango limpo sem pele",
      "½ xícara de arroz integral cozido (100g)",
      "Mix de folhas verdes (alface, rúcula e agrião à vontade)",
      "½ tomate fatiado e raspas de cenoura",
      "1 colher de chá de azeite extravirgem (ou 3 borrifadas do spray)",
      "Sal de ervas, páprica defumada e limão a gosto"
    ],
    passos: [
      "Tempere os filés de frango com limão, sal de ervas e páprica defumada.",
      "Aqueça uma frigideira antiaderente (borrife suavemente azeite).",
      "Grelhe o frango por 3 a 4 minutos de cada lado até ficar dourado e suculento.",
      "Monte o prato dividindo a metade com a salada verde colorida, ¼ com arroz integral e ¼ com o peito de frango grelhado."
    ],
    imagem: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80",
    utensilio: "Borrifador Spray de Azeite Culinário em Inox",
    utensilioLink: "https://s.shopee.com.br/10940561_saciara"
  },
  castanhas_maca: {
    titulo: "Mix de Castanhas & Maçã Crocante",
    horario: "16:00 – 17:00 (Lanche da Tarde)",
    tipo: "Lanche da Tarde",
    calorias: "198 kcal",
    macros: "P: 3g • C: 25g • G: 10g",
    ingredientes: [
      "1 punhado de castanhas do pará e caju (15g - aprox. 4 a 5 unidades)",
      "1 maçã gala ou fuji média lavada",
      "Canela em pó a gosto"
    ],
    passos: [
      "Corte a maçã em fatias finas com casca para preservar fibras pécticas.",
      "Salpique canela a gosto.",
      "Consuma junto com as castanhas mastigando lentamente para estimular saciedade prolongada."
    ],
    imagem: "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=600&q=80",
    utensilio: "Marmitas Herméticas com Divisória Dupla",
    utensilioLink: "https://s.shopee.com.br/10940561_saciara"
  },
  salmao_legumes: {
    titulo: "Salmão Grelhado com Legumes no Vapor",
    horario: "19:00 – 20:30 (Jantar)",
    tipo: "Jantar",
    calorias: "354 kcal",
    macros: "P: 32g • C: 18g • G: 16g",
    ingredientes: [
      "120g de filé de salmão fresco",
      "1 xícara de brócolis ninja em floretes",
      "½ cenoura em rodelas e ½ abobrinha",
      "Suco de ½ limão siciliano, alho picado e alecrim",
      "1 borrifada de azeite"
    ],
    passos: [
      "Cozinhe os legumes no vapor por 6 a 8 minutos até ficarem al dente.",
      "Aqueça a frigideira, doure o salmão com a pele virada para baixo por 4 minutos.",
      "Vire delicadamente e finalize por mais 2 minutos, regando com limão e alecrim.",
      "Sirva o filé acompanhado da cama de legumes fumegantes."
    ],
    imagem: "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=600&q=80",
    utensilio: "Forma de Silicone Antiaderente para Airfryer",
    utensilioLink: "https://s.shopee.com.br/10940561_saciara"
  }
};

function abrirModalReceitaDetalhada(chave) {
  const r = CatalogoReceitasDetalhes[chave] || CatalogoReceitasDetalhes.aveia_banana;
  const listaIngredientes = r.ingredientes.map(i => `<li style="margin-bottom:6px; color:#CBD5E1;">• ${i}</li>`).join('');
  const listaPassos = r.passos.map((p, idx) => `<li style="margin-bottom:8px; color:#CBD5E1;"><strong style="color:#00D070;">Passo ${idx+1}:</strong> ${p}</li>`).join('');

  abrirModal(`📖 ${r.titulo}`, `
    <div style="font-size:14px;">
      <div style="position:relative; width:100%; height:180px; border-radius:10px; overflow:hidden; margin-bottom:16px; border:1px solid #1C2B48;">
        <img src="${r.imagem}" style="width:100%; height:100%; object-fit:cover;">
        <div style="position:absolute; bottom:10px; left:10px; background:rgba(7,11,20,0.85); padding:4px 10px; border-radius:6px; font-weight:800; color:#00D070; font-size:12px;">
          ${r.horario} • ${r.calorias}
        </div>
      </div>

      <div style="background:#091220; padding:10px 14px; border-radius:8px; border:1px solid #1C2B48; margin-bottom:16px; font-weight:700; color:#38BDF8;">
        Macronutrientes da Porção: ${r.macros}
      </div>

      <h4 style="color:#FFFFFF; margin-bottom:8px;">🛒 Ingredientes Selecionados:</h4>
      <ul style="list-style:none; padding-left:0; margin-bottom:16px;">
        ${listaIngredientes}
      </ul>

      <h4 style="color:#FFFFFF; margin-bottom:8px;">👨‍🍳 Modo de Preparo Rápido:</h4>
      <ol style="padding-left:18px; margin-bottom:18px; line-height:1.5;">
        ${listaPassos}
      </ol>

      <div style="background:#091220; padding:12px; border-radius:8px; border:1px solid #00D070; margin-bottom:14px;">
        🛒 <strong>Utensílio que facilita:</strong> <a href="${r.utensilioLink}" target="_blank" style="color:#00D070; font-weight:700;">${r.utensilio} na Shopee</a>
      </div>

      <button style="width:100%; background:#00D070; color:#070B14; border:none; padding:12px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="fecharModalGlobal()">Pronto, já sei como preparar! ✓</button>
    </div>
  `);
}

// Atualiza o card de Refeição de Agora de acordo com o horário real do sistema
function atualizarRefeicaoMomentoPorHorario() {
  const agora = new Date();
  const hora = agora.getHours();
  let chave = 'aveia_banana';
  let tagTexto = "Café da Manhã • Horário Ideal";

  if (hora >= 5 && hora < 10) {
    chave = 'aveia_banana';
    tagTexto = "Seu Café da Manhã de Agora";
  } else if (hora >= 10 && hora < 12) {
    chave = 'iogurte_frutas';
    tagTexto = "Seu Lanche da Manhã de Agora";
  } else if (hora >= 12 && hora < 15) {
    chave = 'frango_arroz';
    tagTexto = "Seu Almoço de Agora";
  } else if (hora >= 15 && hora < 18) {
    chave = 'castanhas_maca';
    tagTexto = "Seu Lanche da Tarde de Agora";
  } else {
    chave = 'salmao_legumes';
    tagTexto = "Seu Jantar de Agora";
  }

  const r = CatalogoReceitasDetalhes[chave];
  const tagEl = document.getElementById('momentoTagText');
  const titleEl = document.getElementById('momentoPratoTitulo');
  const subEl = document.getElementById('momentoPratoSub');
  const kcalsEl = document.getElementById('momentoKcals');
  const imgEl = document.getElementById('momentoPratoImg');
  const btnEl = document.getElementById('btnVerReceitaMomento');

  if (tagEl) tagEl.innerText = tagTexto;
  if (titleEl) titleEl.innerText = r.titulo;
  if (subEl) subEl.innerText = r.ingredientes.slice(0, 3).join(' • ');
  if (kcalsEl) kcalsEl.innerText = r.calorias;
  if (imgEl) imgEl.src = r.imagem;
  if (btnEl) btnEl.onclick = () => abrirModalReceitaDetalhada(chave);
}

// ==========================================================================
// ABA DE COMPRAS DO MÊS: ALGORITMO DE OTIMIZAÇÃO POR ORÇAMENTO
// Preços médios populares monitorados em Atacarejo, Assaí e Extra (Salvador/SP/RJ)
// ==========================================================================
const ItensPrecosSupermercados = [
  // Proteínas
  { 
    cat: "Proteínas de Alto Valor", 
    nome: "Peito de Frango Congelado (kg)", 
    precoUnit: 17.90, 
    baseMes: 4.5, 
    unidade: "kg",
    imagem: "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Proteínas de Alto Valor", 
    nome: "Ovos Brancos Grandes (Cartela c/ 30)", 
    precoUnit: 16.50, 
    baseMes: 2, 
    unidade: "cartelas",
    imagem: "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Proteínas de Alto Valor", 
    nome: "Filé de Tilápia / Peixe Fresco (kg)", 
    precoUnit: 31.90, 
    baseMes: 1.5, 
    unidade: "kg",
    imagem: "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Proteínas de Alto Valor", 
    nome: "Patinho Moído Bovino (kg)", 
    precoUnit: 34.90, 
    baseMes: 1.2, 
    unidade: "kg",
    imagem: "https://images.unsplash.com/photo-1551028150-64b9f398f678?auto=format&fit=crop&w=150&q=80"
  },
  
  // Carboidratos & Grãos
  { 
    cat: "Carboidratos & Grãos Integrais", 
    nome: "Arroz Integral Tipo 1 (1kg)", 
    precoUnit: 5.90, 
    baseMes: 3, 
    unidade: "pcts",
    imagem: "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Carboidratos & Grãos Integrais", 
    nome: "Aveia em Flocos Finos (500g)", 
    precoUnit: 6.20, 
    baseMes: 3, 
    unidade: "pcts",
    imagem: "https://images.unsplash.com/photo-1614961908595-6b801a6104fa?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Carboidratos & Grãos Integrais", 
    nome: "Batata Doce Roxa (kg)", 
    precoUnit: 4.50, 
    baseMes: 3.5, 
    unidade: "kg",
    imagem: "https://images.unsplash.com/photo-1596560548464-f010549b84d7?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Carboidratos & Grãos Integrais", 
    nome: "Feijão Carioca Tipo 1 (1kg)", 
    precoUnit: 6.80, 
    baseMes: 2, 
    unidade: "pcts",
    imagem: "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=150&q=80"
  },

  // Hortifrúti & Fibras
  { 
    cat: "Hortifrúti, Legumes & Frutas", 
    nome: "Banana Prata / Nanica (kg)", 
    precoUnit: 4.90, 
    baseMes: 5, 
    unidade: "kg",
    imagem: "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Hortifrúti, Legumes & Frutas", 
    nome: "Maçã Nacional (kg)", 
    precoUnit: 7.90, 
    baseMes: 2.5, 
    unidade: "kg",
    imagem: "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Hortifrúti, Legumes & Frutas", 
    nome: "Brócolis Ninja / Couve-Flor", 
    precoUnit: 6.50, 
    baseMes: 4, 
    unidade: "unidades",
    imagem: "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Hortifrúti, Legumes & Frutas", 
    nome: "Cenoura & Abobrinha (kg)", 
    precoUnit: 4.80, 
    baseMes: 3, 
    unidade: "kg",
    imagem: "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Hortifrúti, Legumes & Frutas", 
    nome: "Mix de Folhas (Alface/Rúcula)", 
    precoUnit: 3.50, 
    baseMes: 6, 
    unidade: "maços",
    imagem: "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=150&q=80"
  },

  // Gorduras & Laticínios
  { 
    cat: "Gorduras Boas & Laticínios", 
    nome: "Iogurte Natural Integral/Desn (Pote 170g)", 
    precoUnit: 3.20, 
    baseMes: 15, 
    unidade: "potes",
    imagem: "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Gorduras Boas & Laticínios", 
    nome: "Sementes de Chia / Linhaça (200g)", 
    precoUnit: 8.90, 
    baseMes: 1, 
    unidade: "pct",
    imagem: "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Gorduras Boas & Laticínios", 
    nome: "Azeite de Oliva Extravirgem (500ml)", 
    precoUnit: 36.90, 
    baseMes: 1, 
    unidade: "garrafa",
    imagem: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=150&q=80"
  },
  { 
    cat: "Gorduras Boas & Laticínios", 
    nome: "Mix de Castanhas (200g)", 
    precoUnit: 18.90, 
    baseMes: 1, 
    unidade: "pct",
    imagem: "https://images.unsplash.com/photo-1536591375315-1b838421a153?auto=format&fit=crop&w=150&q=80"
  }
];

// ==========================================================================
// ABA DE COMPRAS DO MÊS: ALGORITMO CIENTÍFICO BASEADO NO PLANO PERSONALIZADO
// Soma todas as refeições do mês (150 refeições) calculadas para o indivíduo
// e orça nos grandes atacadistas populares (Atacarejo, Assaí, Extra)
// ==========================================================================
function recalcularPlanoECompras() {
  const genero = document.getElementById('userGenero')?.value || 'feminino';
  const peso = parseFloat(document.getElementById('userPeso')?.value) || 70.8;
  const altura = parseFloat(document.getElementById('userAltura')?.value) || 165;
  const idade = parseFloat(document.getElementById('userIdade')?.value) || 28;
  const atividade = document.getElementById('userAtividade')?.value || 'moderado';
  const restricoes = document.getElementById('userRestricoes')?.value || 'nenhuma';
  const metaKg = parseFloat(document.getElementById('userMetaKg')?.value) || 70;

  // 1. Cálculo da TMB (Mifflin-St Jeor)
  // Homem: 10*peso + 6.25*altura - 5*idade + 5
  // Mulher: 10*peso + 6.25*altura - 5*idade - 161
  let tmb = (10 * peso) + (6.25 * altura) - (5 * idade);
  tmb = (genero === 'masculino') ? tmb + 5 : tmb - 161;

  // 2. Fatores de Atividade Física (GET)
  const fatoresAtiv = {
    sedentario: 1.2,
    leve: 1.375,
    moderado: 1.55,
    intenso: 1.725
  };
  const get = tmb * (fatoresAtiv[atividade] || 1.55);

  // 3. Meta Calórica com Déficit Fisiológico Kevin Hall (aprox. 450 a 500 kcal de déficit)
  const metaKcal = Math.round(Math.max(get - 475, genero === 'masculino' ? 1600 : 1350));
  
  // 4. Macronutrientes Fisiológicos
  // Proteína: 1.8 g/kg (preservação de FFM)
  const protG = Math.round(peso * 1.8);
  // Gordura: 0.8 g/kg (saúde hormonal)
  const gordG = Math.round(peso * 0.8);
  // Carboidratos: restante calórico
  const carbKcal = metaKcal - (protG * 4) - (gordG * 9);
  const carbG = Math.round(Math.max(carbKcal / 4, 100));

  // 5. Atualizar Diagnóstico Visual na Tela
  const diagTitulo = document.getElementById('diagTituloPlano');
  const diagDesc = document.getElementById('diagDescricaoPlano');
  const badgesRow = document.getElementById('diagBadgesRow');

  if (diagTitulo) {
    diagTitulo.innerText = `Plano Científico Saciara: ${metaKcal} kcal/dia (Déficit Fisiológico Kevin Hall)`;
  }
  if (diagDesc) {
    const perdaMes = (((get - metaKcal) * 30) / 7700).toFixed(1).replace('.', ',');
    diagDesc.innerHTML = `Metabolismo Basal (TMB) de <strong>${Math.round(tmb)} kcal</strong> somado ao fator de atividade resulta em gasto diário de <strong>${Math.round(get)} kcal</strong>. O déficit controlado de ${Math.round(get - metaKcal)} kcal/dia gera <strong>perda real prevista de ${perdaMes} kg de gordura ao mês</strong> preservando sua massa magra.`;
  }
  if (badgesRow) {
    badgesRow.innerHTML = `
      <span class="diag-pill">🔥 ${metaKcal} kcal/dia</span>
      <span class="diag-pill">🥩 ${protG}g Proteínas/dia (1,8g/kg)</span>
      <span class="diag-pill">🌾 ${carbG}g Carboidratos/dia</span>
      <span class="diag-pill">🥑 ${gordG}g Gorduras/dia</span>
      <span class="diag-pill" style="color:#00D070;">✓ 150 Refeições/mês Somadas</span>
    `;
  }

  // 6. Multiplicador de escala das receitas do mês (30 dias x 5 refeições/dia = 150 pratos)
  // Calibra as quantidades totais necessárias de compras com base no peso e calorias do usuário
  const escalaCalorica = metaKcal / 1800;

  // Filtragem e Adaptação por Alergias
  let fatorPeixe = 1.0;
  let fatorLactose = 1.0;
  let substitutoPeixe = "Filé de Frango ou Ovos Adicionais";

  if (restricoes === 'frutos_mar') {
    fatorPeixe = 0;
  }
  if (restricoes === 'lactose') {
    fatorLactose = 0;
  }

  // 7. Soma dos Ingredientes para os 30 Dias Inteiros
  const itensSoma30Dias = [
    // PROTEÍNAS
    {
      cat: "Proteínas de Alto Valor (Para atingir " + (protG * 30 / 1000).toFixed(1) + " kg de proteína pura)",
      nome: restricoes === 'vegetariano' ? "Ovos Caipiras Grandes (Cartela c/ 30)" : "Peito de Frango Congelado (kg)",
      precoUnit: restricoes === 'vegetariano' ? 16.50 : 17.90,
      qtdCalculada: restricoes === 'vegetariano' ? Math.round(5 * escalaCalorica) : Math.round((4.8 * (peso / 70) * escalaCalorica) * 10) / 10,
      unidade: restricoes === 'vegetariano' ? "cartelas" : "kg",
      imagem: restricoes === 'vegetariano' ? "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=150&q=80" : "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Proteínas de Alto Valor (Para atingir " + (protG * 30 / 1000).toFixed(1) + " kg de proteína pura)",
      nome: "Ovos Brancos Selecionados (Cartela c/ 30)",
      precoUnit: 16.50,
      qtdCalculada: Math.round(2 * escalaCalorica),
      unidade: "cartelas (60 ovos)",
      imagem: "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Proteínas de Alto Valor (Para atingir " + (protG * 30 / 1000).toFixed(1) + " kg de proteína pura)",
      nome: restricoes === 'frutos_mar' || restricoes === 'vegetariano' ? "Tofu Fresco ou Queijo Cottage (kg)" : "Filé de Tilápia / Peixe Branco (kg)",
      precoUnit: restricoes === 'frutos_mar' ? 24.90 : 31.90,
      qtdCalculada: Math.round((1.6 * escalaCalorica) * 10) / 10,
      unidade: "kg",
      imagem: "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Proteínas de Alto Valor (Para atingir " + (protG * 30 / 1000).toFixed(1) + " kg de proteína pura)",
      nome: restricoes === 'vegetariano' ? "Lentilha / Grão de Bico (1kg)" : "Patinho Moído Magro (kg)",
      precoUnit: restricoes === 'vegetariano' ? 8.90 : 34.90,
      qtdCalculada: Math.round((1.2 * escalaCalorica) * 10) / 10,
      unidade: restricoes === 'vegetariano' ? "pcts" : "kg",
      imagem: "https://images.unsplash.com/photo-1551028150-64b9f398f678?auto=format&fit=crop&w=150&q=80"
    },

    // CARBOIDRATOS & GRÃOS
    {
      cat: "Carboidratos Complexos & Fibras (30 Almoços e Jantares)",
      nome: restricoes === 'gluten' ? "Quinoa Real em Grãos (500g)" : "Arroz Integral Tipo 1 (1kg)",
      precoUnit: restricoes === 'gluten' ? 12.50 : 5.90,
      qtdCalculada: Math.round(3 * escalaCalorica),
      unidade: "pcts (3kg cozidos)",
      imagem: "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Carboidratos Complexos & Fibras (30 Almoços e Jantares)",
      nome: restricoes === 'gluten' ? "Aveia sem Glúten Certificada (500g)" : "Aveia em Flocos Finos (500g)",
      precoUnit: restricoes === 'gluten' ? 11.90 : 6.20,
      qtdCalculada: Math.round(2.5 * escalaCalorica),
      unidade: "pcts (para 30 cafés da manhã)",
      imagem: "https://images.unsplash.com/photo-1614961908595-6b801a6104fa?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Carboidratos Complexos & Fibras (30 Almoços e Jantares)",
      nome: "Batata Doce Roxa Orgânica (kg)",
      precoUnit: 4.50,
      qtdCalculada: Math.round((3.2 * escalaCalorica) * 10) / 10,
      unidade: "kg",
      imagem: "https://images.unsplash.com/photo-1596560548464-f010549b84d7?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Carboidratos Complexos & Fibras (30 Almoços e Jantares)",
      nome: "Feijão Carioca Tipo 1 (1kg)",
      precoUnit: 6.80,
      qtdCalculada: 2,
      unidade: "pcts (2kg)",
      imagem: "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=150&q=80"
    },

    // HORTIFRÚTI & FRUTAS DOS 30 DIAS
    {
      cat: "Hortifrúti Fresco & Frutas (Lanches & Saciedade)",
      nome: "Banana Prata (kg)",
      precoUnit: 4.90,
      qtdCalculada: Math.round((5.0 * escalaCalorica) * 10) / 10,
      unidade: "kg (30 bananas p/ cafés)",
      imagem: "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Hortifrúti Fresco & Frutas (Lanches & Saciedade)",
      nome: "Maçã Nacional Fuji (kg)",
      precoUnit: 7.90,
      qtdCalculada: Math.round((3.0 * escalaCalorica) * 10) / 10,
      unidade: "kg (para lanches da tarde)",
      imagem: "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Hortifrúti Fresco & Frutas (Lanches & Saciedade)",
      nome: "Brócolis Ninja & Couve-Flor",
      precoUnit: 6.50,
      qtdCalculada: Math.round(4 * escalaCalorica),
      unidade: "unidades",
      imagem: "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Hortifrúti Fresco & Frutas (Lanches & Saciedade)",
      nome: "Cenoura & Abobrinha Italiana (kg)",
      precoUnit: 4.80,
      qtdCalculada: Math.round((3.5 * escalaCalorica) * 10) / 10,
      unidade: "kg",
      imagem: "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Hortifrúti Fresco & Frutas (Lanches & Saciedade)",
      nome: "Mix de Folhas (Alface Americana & Rúcula)",
      precoUnit: 3.50,
      qtdCalculada: 6,
      unidade: "maços (consumo semanal)",
      imagem: "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=150&q=80"
    },

    // GORDURAS BOAS & LATICÍNIOS
    {
      cat: "Gorduras Boas, Laticínios & Superalimentos",
      nome: restricoes === 'lactose' ? "Iogurte Vegetal de Coco ou Zero Lactose (Pote)" : "Iogurte Natural Desnatado (Pote 170g)",
      precoUnit: restricoes === 'lactose' ? 4.50 : 3.20,
      qtdCalculada: Math.round(18 * escalaCalorica),
      unidade: "potes (para lanches)",
      imagem: "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Gorduras Boas, Laticínios & Superalimentos",
      nome: "Sementes de Chia / Linhaça Dourada (200g)",
      precoUnit: 8.90,
      qtdCalculada: 1,
      unidade: "pct (dura o mês inteiro)",
      imagem: "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Gorduras Boas, Laticínios & Superalimentos",
      nome: "Azeite de Oliva Extravirgem Acidez < 0,5% (500ml)",
      precoUnit: 36.90,
      qtdCalculada: 1,
      unidade: "garrafa (usar em spray)",
      imagem: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=150&q=80"
    },
    {
      cat: "Gorduras Boas, Laticínios & Superalimentos",
      nome: "Castanhas do Pará e Caju (250g)",
      precoUnit: 19.90,
      qtdCalculada: 1,
      unidade: "pct (porções de 15g)",
      imagem: "https://images.unsplash.com/photo-1536591375315-1b838421a153?auto=format&fit=crop&w=150&q=80"
    }
  ];

  // 8. Cálculo de Totais e Agrupamento
  const categoriasMap = {};
  let totalEstimado = 0;

  itensSoma30Dias.forEach(item => {
    const subtotal = item.qtdCalculada * item.precoUnit;
    totalEstimado += subtotal;

    if (!categoriasMap[item.cat]) {
      categoriasMap[item.cat] = { itens: [], subtotalCat: 0 };
    }
    categoriasMap[item.cat].itens.push({
      nome: item.nome,
      qtd: item.qtdCalculada,
      unidade: item.unidade,
      subtotal: subtotal,
      imagem: item.imagem
    });
    categoriasMap[item.cat].subtotalCat += subtotal;
  });

  // Atualiza totais na tela
  const totalEl = document.getElementById('statTotalEstimado');
  const econEl = document.getElementById('statEconomiaEstimada');
  const refCobertasEl = document.getElementById('statRefeicoesCobertas');

  if (totalEl) totalEl.innerText = `R$ ${totalEstimado.toFixed(2).replace('.', ',')}`;
  if (econEl) econEl.innerText = `R$ ${(totalEstimado * 0.20).toFixed(2).replace('.', ',')}`;
  if (refCobertasEl) refCobertasEl.innerText = `150 refeições`;

  // Renderiza no DOM com Imagens e Gramas Somadas
  const gridEl = document.getElementById('comprasCategoriesGrid');
  if (!gridEl) return;

  gridEl.innerHTML = Object.entries(categoriasMap).map(([nomeCat, dados]) => `
    <div class="compras-category-card">
      <div class="compras-category-header">
        <div class="compras-cat-title">
          <span>📦</span>
          <span>${nomeCat}</span>
        </div>
        <span class="compras-cat-subtotal">R$ ${dados.subtotalCat.toFixed(2).replace('.', ',')}</span>
      </div>
      <div>
        ${dados.itens.map(it => `
          <div class="compras-item-row">
            <div class="compras-item-left">
              <img src="${it.imagem}" class="compras-item-img-thumb" alt="${it.nome}" loading="lazy">
              <div>
                <div class="compras-item-name">${it.nome}</div>
                <div class="compras-item-qtd">Soma das receitas do mês: <strong>${it.qtd} ${it.unidade}</strong></div>
              </div>
            </div>
            <div class="compras-item-price">R$ ${it.subtotal.toFixed(2).replace('.', ',')}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function copiarListaComprasTexto() {
  const itens = [
    "🛒 *LISTA DE COMPRAS DO MÊS — PROTOCOLO SACIARA*",
    "• Peito de Frango / Tilápia: 7,5 kg",
    "• Ovos Caipiras / Granja: 90 unidades (3 cartelas)",
    "• Patinho Moído de Primeira: 3,0 kg",
    "• Arroz Integral / Parboilizado: 3,0 kg",
    "• Aveia em Flocos Finos: 1,8 kg",
    "• Batata Doce / Mandioca: 4,0 kg",
    "• Brócolis, Cenoura e Abobrinha: 6,0 kg",
    "• Banana Prata e Frutas da Estação: 8,0 kg",
    "• Azeite de Oliva Extra Virgem: 2 garrafas (500ml)",
    "",
    "⚡ _Valores e quantidades calculadas para 30 dias (150 refeições)._"
  ];
  const texto = itens.join('\n');
  if (navigator.clipboard) {
    navigator.clipboard.writeText(texto).then(() => {
      mostrarToastFeedback("📋 Lista de compras copiada para a área de transferência!");
    });
  } else {
    mostrarToastFeedback("📋 Lista pronta para copiar!");
  }
}

// Sons Sintetizados via Web Audio API (Sem arquivos externos pesados)
function tocarSomVitoria() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const notas = [261.63, 329.63, 392.00, 523.25]; // C4, E4, G4, C5 (Acorde Feliz Maior)
    notas.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + idx * 0.08);
      gain.gain.setValueAtTime(0.15, ctx.currentTime + idx * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.08 + 0.3);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(ctx.currentTime + idx * 0.08);
      osc.stop(ctx.currentTime + idx * 0.08 + 0.32);
    });
  } catch (e) {
    // Fallback silencioso caso áudio esteja desabilitado
  }
}

function tocarSomErro() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(150, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.2);
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.22);
  } catch (e) {}
}

function abrirLojaGemas() {
  abrirModal("🛍️ Loja de Recompensas DuoNutri", `
    <div style="color:#CBD5E1; font-size:14px;">
      <div style="display:flex; justify-content:space-between; align-items:center; background:#121B2E; border:1px solid #1C2B48; padding:12px 16px; border-radius:12px; margin-bottom:18px;">
        <span>Seu Saldo:</span>
        <strong style="color:#00D070; font-size:16px;">💎 ${duoUserGemas} Gemas</strong>
      </div>

      <div style="display:flex; flex-direction:column; gap:12px;">
        <!-- Item 1: Protetor de Ofensiva -->
        <div style="display:flex; justify-content:space-between; align-items:center; background:#0E1626; border:1px solid #1C2B48; border-radius:12px; padding:14px;">
          <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:26px;">🧊</span>
            <div>
              <div style="color:#FFF; font-weight:700;">Congelamento de Ofensiva</div>
              <div style="font-size:12px; color:#94A3B8;">Protege seus 14 dias se esquecer de registrar amanhã.</div>
            </div>
          </div>
          <button style="padding:8px 12px; background:#00D070; color:#070B14; font-weight:800; border:none; border-radius:8px; cursor:pointer;" onclick="comprarItemLoja('Congelamento de Ofensiva', 100)">
            100 💎
          </button>
        </div>

        <!-- Item 2: E-book de Doces Fit -->
        <div style="display:flex; justify-content:space-between; align-items:center; background:#0E1626; border:1px solid #1C2B48; border-radius:12px; padding:14px;">
          <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:26px;">📖</span>
            <div>
              <div style="color:#FFF; font-weight:700;">Guia de Sobremesas Fit Sem Açúcar</div>
              <div style="font-size:12px; color:#94A3B8;">20 receitas rápidas para matar a vontade de doce.</div>
            </div>
          </div>
          <button style="padding:8px 12px; background:#00D070; color:#070B14; font-weight:800; border:none; border-radius:8px; cursor:pointer;" onclick="comprarItemLoja('Guia de Sobremesas Fit', 150)">
            150 💎
          </button>
        </div>

        <!-- Item 3: Cupom Shopee Balança -->
        <div style="display:flex; justify-content:space-between; align-items:center; background:#0E1626; border:1px solid #1C2B48; border-radius:12px; padding:14px;">
          <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:26px;">⚖️</span>
            <div>
              <div style="color:#FFF; font-weight:700;">Cupom de Desconto Shopee Utensílios</div>
              <div style="font-size:12px; color:#94A3B8;">Balança SF-400 e marmitas herméticas com comissão.</div>
            </div>
          </div>
          <a href="https://s.shopee.com.br/9zz6HcfAxu" target="_blank" style="padding:8px 12px; background:#FF9F1C; color:#070B14; font-weight:800; text-decoration:none; border-radius:8px; display:inline-block;">
            Ver na Shopee ➔
          </a>
        </div>
      </div>
    </div>
  `);
}

function comprarItemLoja(nome, preco) {
  if (duoUserGemas >= preco) {
    duoUserGemas -= preco;
    const gemasEl = document.getElementById('duoGemasVal');
    if (gemasEl) gemasEl.innerText = duoUserGemas;
    tocarSomVitoria();
    fecharModalGlobal();
    mostrarToastFeedback(`🎉 Parabéns! Você adquiriu: ${nome}`);
  } else {
    tocarSomErro();
    mostrarToastFeedback(`❌ Gemas insuficientes! Faltam ${preco - duoUserGemas} 💎.`);
  }
}
let duoUserGemas = 380;
let duoUserXp = 1840;

const LicoesDuolingoData = {
  1: {
    titulo: "1. O Segredo da Proteína",
    icone: "🥚",
    pergunta: "Por que comer proteína acelera seu emagrecimento sem você passar fome?",
    opcoes: [
      {
        texto: "Ela tem o maior Efeito Térmico dos Alimentos (TEF) e libera peptídeos de saciedade no cérebro.",
        correta: true,
        explicacao: "Exato! Cerca de 20% a 30% das calorias da proteína são gastas apenas para digeri-la, e ela estimula o GLP-1 e PYY naturais."
      },
      {
        texto: "Porque ela zera o carboidrato do sangue instantaneamente.",
        correta: false,
        explicacao: "Incorreto. A proteína não anula outros nutrientes, mas gera saciedade prolongada pela mastigação e digestão gástrica."
      }
    ]
  },
  2: {
    titulo: "2. Hidratação & Taxa Metabólica",
    icone: "💧",
    pergunta: "O que acontece metabolicamente quando você bebe 500ml de água fria em jejum?",
    opcoes: [
      {
        texto: "O corpo gasta energia termogênica para aquecer a água e acelera a taxa metabólica basal em até 24% por 60 minutos.",
        correta: true,
        explicacao: "Cientificamente comprovado! Esse efeito termogênico da água foi demonstrado em estudos clínicos do Journal of Clinical Endocrinology."
      },
      {
        texto: "A água dilui a gordura no estômago e a elimina pelas fezes.",
        correta: false,
        explicacao: "Mito comum! A gordura é oxidada nos pulmões (CO2) e na água metabólica, e não eliminada diretamente pela água ingerida."
      }
    ]
  },
  3: {
    titulo: "3. O Balanço de Kevin Hall",
    icone: "⚖️",
    pergunta: "Por que a regra antiga de '7.700 kcal = 1 kg' falha no mundo real?",
    opcoes: [
      {
        texto: "Porque o corpo adapta o metabolismo (termogênese adaptativa) e a partição de Forbes altera a proporção de gordura vs. músculo.",
        correta: true,
        explicacao: "Perfeito! Kevin Hall (Lancet 2011) provou que o metabolismo desacelera conforme o peso cai, exigindo déficits sustentáveis."
      },
      {
        texto: "Porque as calorias não contam nada, apenas o horário da comida.",
        correta: false,
        explicacao: "Incorreto. As calorias obedecem à primeira lei da termodinâmica, mas a resposta biológica humana é dinâmica e não estática."
      }
    ]
  },
  4: {
    titulo: "4. Fibras & Fim da Fome",
    icone: "🥗",
    pergunta: "Qual destes dois pratos sacia mais o cérebro com as mesmas 200 calorias?",
    opcoes: [
      {
        texto: "🥔 250g de Batata Cozida ou Legumes no Vapor com casca (Fibras e alto índice de saciedade de Holt).",
        correta: true,
        explicacao: "Sensacional! No Índice de Saciedade de Holt (Universidade de Sydney), a batata cozida alcançou incríveis 323%, o maior escore de todos!"
      },
      {
        texto: "🥐 1 mini croissant amanteigado.",
        correta: false,
        explicacao: "O croissant tem alta densidade energética e baixo volume, gerando esvaziamento gástrico rápido e fome 1 hora depois."
      }
    ]
  }
};

function iniciarLicaoDuolingo(nodeId) {
  const licao = LicoesDuolingoData[nodeId] || LicoesDuolingoData[4];
  
  abrirModal(`${licao.icone} ${licao.titulo}`, `
    <div class="duo-quiz-container">
      <!-- Barra de Progresso no Topo estilo Duolingo -->
      <div class="duo-quiz-progress">
        <div class="duo-quiz-fill" style="width: 50%;"></div>
      </div>

      <div class="duo-quiz-question">${licao.pergunta}</div>

      <div class="duo-quiz-options" id="duoQuizOptionsList">
        ${licao.opcoes.map((opt, idx) => `
          <button class="quiz-option-btn" onclick="responderQuizDuolingo(${nodeId}, ${idx})">
            <span class="quiz-opt-icon">${idx === 0 ? '🅰️' : '🅱️'}</span>
            <div>
              <div class="quiz-opt-title">${opt.texto}</div>
            </div>
          </button>
        `).join('')}
      </div>

      <div id="duoFeedbackArea"></div>
    </div>
  `);
}

function responderQuizDuolingo(nodeId, optIdx) {
  const licao = LicoesDuolingoData[nodeId] || LicoesDuolingoData[4];
  const escolha = licao.opcoes[optIdx];
  const area = document.getElementById('duoFeedbackArea');
  const progFill = document.querySelector('.duo-quiz-fill');

  if (progFill) progFill.style.width = '100%';

  if (escolha.correta) {
    tocarSomVitoria();
    // Recompensas
    duoUserGemas += 5;
    duoUserXp += 25;
    
    // Atualiza elementos
    const gemasEl = document.getElementById('duoGemasVal');
    const xpEl = document.getElementById('userCurrentXpVal');
    if (gemasEl) gemasEl.innerText = duoUserGemas;
    if (xpEl) xpEl.innerText = `${duoUserXp} XP`;

    area.innerHTML = `
      <div class="quiz-feedback-box">
        <div class="feedback-title">
          <span>🎉</span> <span>Sensacional! Resposta Correta!</span>
        </div>
        <div class="feedback-body">${escolha.explicacao}</div>
      </div>
      <button class="btn-primary" style="width:100%; padding:14px; background:#00D070; color:#070B14; font-size:15px; font-weight:800; border:none; border-radius:12px; cursor:pointer; box-shadow:0 4px 14px rgba(0,208,112,0.4);" onclick="fecharModalGlobal(); mostrarToastFeedback('💎 +5 Gemas e +25 XP conquistados!');">
        Continuar (+25 XP & +5 💎)
      </button>
    `;
  } else {
    area.innerHTML = `
      <div class="quiz-feedback-box" style="border-color:#EF4444; background:rgba(239,68,68,0.15);">
        <div class="feedback-title" style="color:#EF4444;">
          <span>💡</span> <span>Quase lá! Veja a explicação:</span>
        </div>
        <div class="feedback-body">${escolha.explicacao}</div>
      </div>
      <button class="btn-primary" style="width:100%; padding:14px; background:#1C2B48; color:#FFF; font-size:14px; font-weight:800; border:none; border-radius:12px; cursor:pointer;" onclick="iniciarLicaoDuolingo(${nodeId})">
        Tentar Novamente
      </button>
    `;
  }
}

function abrirBauRecompensa() {
  duoUserGemas += 50;
  const gemasEl = document.getElementById('duoGemasVal');
  if (gemasEl) gemasEl.innerText = duoUserGemas;

  abrirModal("🎁 Baú do Tesouro da Trilha Aberto!", `
    <div style="text-align:center; padding:16px 0;">
      <div style="font-size:64px; margin-bottom:12px; animation:fireFlicker 1.5s infinite;">💎</div>
      <h2 style="font-size:20px; font-weight:800; color:#FFD700; margin-bottom:8px;">Você recebeu +50 Gemas Esmeralda!</h2>
      <p style="font-size:13px; color:#94A3B8; max-width:320px; margin:0 auto 20px auto;">
        Continue mantendo sua ofensiva de hábitos diários para abrir os próximos baús da Fase 2!
      </p>
      <button class="btn-primary" style="width:100%; padding:14px; background:#00D070; color:#070B14; font-weight:800; border:none; border-radius:12px; cursor:pointer;" onclick="fecharModalGlobal(); mostrarToastFeedback('💎 +50 Gemas adicionadas ao seu cofre!');">
        Coletar Recompensa
      </button>
    </div>
  `);
}

function abrirModalLiga() {
  abrirModal("🛡️ Ligas Semanais Saciara", `
    <div style="color:#E2E8F0; font-size:14px; line-height:1.5;">
      <p>As <strong>Ligas Semanais</strong> incentivam a disciplina diária. O ranking é atualizado conforme você registra água, treinos e completa lições rápidas.</p>
      
      <div style="background:#0E1626; border:1px solid #1C2B48; border-radius:12px; padding:14px; margin:14px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span>Sua Divisão:</span>
          <strong style="color:#FFD700;">Liga Ouro</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span>Sua Posição:</span>
          <strong style="color:#00D070;">3º Lugar (Zona de Acesso)</strong>
        </div>
        <div style="display:flex; justify-content:space-between;">
          <span>Próxima Liga:</span>
          <strong style="color:#38BDF8;">Liga Esmeralda</strong>
        </div>
      </div>

      <p style="font-size:12px; color:#64748B;">Os 3 primeiros colocados sobem de divisão todo domingo à meia-noite e ganham 100 Gemas bônus!</p>
    </div>
  `);
}

// Inicializa no carregamento
document.addEventListener('DOMContentLoaded', () => {
  atualizarRefeicaoMomentoPorHorario();
  setInterval(atualizarRefeicaoMomentoPorHorario, 60000); // Checa a cada minuto
});
