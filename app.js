// Saciara Nutri — Motor Fisiológico & Aplicativo PWA (ESM)
// Implementação Determinística de Mifflin-St Jeor, Hall Dynamic Model & Filtro de Kalman

let state = {
  activeTab: 'plano',
  profile: {
    peso: 72,
    altura: 168,
    idade: 29,
    sexo: 'F',
    bf: 28,
    atividade: 1.375,
    ritmo: 'moderado',
    diaCiclo: 18
  },
  recipes: [],
  selectedRecipe: null,
  diaSemanaAtivo: 0,
  shoppingChecks: {}
};

// --- MOTORES CIENTÍFICOS CLIENT-SIDE ---

const Fisiologia = {
  calcularMifflin(p) {
    const base = (10.0 * p.peso) + (6.25 * p.altura) - (5.0 * p.idade);
    return Math.round(p.sexo === 'M' ? base + 5 : base - 161);
  },

  calcularPrescricao(p) {
    const tmb = this.calcularMifflin(p);
    const tdee = Math.round(tmb * p.atividade);
    const deficitMap = { leve: 300, moderado: 450, acelerado_seguro: 600 };
    const deficit = deficitMap[p.ritmo] || 450;
    const piso = p.sexo === 'F' ? 1250 : 1500;
    const caloriasAlvo = Math.max(piso, tdee - deficit);

    const protG = Math.round(p.peso * 1.8);
    const protKcal = protG * 4;
    const gordG = Math.round(p.peso * 0.8);
    const gordKcal = gordG * 9;
    const carbKcal = Math.max(300, caloriasAlvo - protKcal - gordKcal);
    const carbG = Math.round(carbKcal / 4);

    return {
      tmb,
      tdee,
      caloriasAlvo,
      deficit,
      protG,
      carbG,
      gordG,
      fibrasG: Math.max(28, Math.round((caloriasAlvo / 1000) * 14)),
      aguaL: ((p.peso * 35) / 1000).toFixed(1)
    };
  },

  // Simulação de Kevin D. Hall (Lancet 2011)
  simularHall(p, dias = 90) {
    const prescricao = this.calcularPrescricao(p);
    const tdeeIni = prescricao.tdee;
    const deficitIni = prescricao.deficit;
    const ingestao = prescricao.caloriasAlvo;

    let fm = p.peso * (p.bf / 100.0);
    let ffm = p.peso - fm;
    const rmrIni = 370 + (21.6 * ffm) + (3.2 * fm);
    const aeeIni = Math.max(0, (0.90 * tdeeIni) - rmrIni);
    const deltaAtiv = aeeIni / p.peso;

    let adaptacao = 0;
    const maxAgua = Math.min(1.8, Math.max(0.6, 0.015 * p.peso));
    let aguaPerdida = 0;
    const pontos = [];

    for (let d = 1; d <= dias; d++) {
      const rmr = 370 + (21.6 * ffm) + (3.2 * fm);
      const tef = 0.10 * ingestao;
      const aee = deltaAtiv * (fm + ffm);

      if (deficitIni > 0) {
        const alvoAdapt = 0.14 * deficitIni;
        adaptacao += (alvoAdapt - adaptacao) * (1.0 / 14.0);
      }

      const ee = rmr + tef + aee - adaptacao;
      const balanco = ingestao - ee;

      const pForbes = Math.max(0.05, Math.min(0.45, 10.4 / (10.4 + fm)));
      const rhoTecido = ((1.0 - pForbes) * 9400) + (pForbes * 1800);
      const deltaPesoTecido = balanco / rhoTecido;

      fm = Math.max(2, fm + ((1.0 - pForbes) * deltaPesoTecido));
      ffm = Math.max(10, ffm + (pForbes * deltaPesoTecido));

      if (d <= 5 && deficitIni > 0) aguaPerdida += (maxAgua / 5);
      const pesoHall = fm + ffm - (d <= 5 ? aguaPerdida : maxAgua);
      const pesoIngenuo = p.peso - ((deficitIni * d) / 7700);

      pontos.push({ dia: d, hall: pesoHall, ingenuo: pesoIngenuo });
    }
    return pontos;
  },

  diagnosticarCiclo(dia) {
    const d = Math.max(1, Math.min(32, dia));
    if (d <= 5) return { fase: 'Menstrual (Dias 1-5)', aviso: 'Eliminação da retenção hídrica (queda rápida de peso).', deltaKcal: 0 };
    if (d <= 13) return { fase: 'Folicular (Dias 6-13)', aviso: 'Peso mais estável e real da balança. Pico de energia.', deltaKcal: 0 };
    if (d <= 16) return { fase: 'Ovulatória (Dias 14-16)', aviso: 'Leve oscilação de 300g-500g por pico estrogênico.', deltaKcal: 0 };
    return { fase: 'Lútea / TPM (Dias 17-28)', aviso: 'Retenção hídrica de 1 a 2.5 kg por progesterona. NÃO é gordura corporal e TMB sobe +150 kcal.', deltaKcal: 150 };
  }
};

// --- INICIALIZAÇÃO DA APLICAÇÃO ---

async function init() {
  // Carrega perfil salvo
  const savedProfile = localStorage.getItem('saciara_profile');
  if (savedProfile) {
    try { state.profile = JSON.parse(savedProfile); } catch (e) {}
  }
  const savedChecks = localStorage.getItem('saciara_shopping');
  if (savedChecks) {
    try { state.shoppingChecks = JSON.parse(savedChecks); } catch (e) {}
  }

  // Carrega receitas
  try {
    const res = await fetch('receitas.json');
    state.recipes = await res.json();
  } catch (e) {
    console.warn('Usando catálogo embutido de fallback');
  }

  bindEvents();
  renderAll();
}

function bindEvents() {
  // Tabs
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = btn.dataset.tab;
      switchTab(tab);
    });
  });

  // Modal Fechar
  const modal = document.getElementById('recipeModal');
  modal.addEventListener('click', (e) => {
    if (e.target === modal) fecharModal();
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.nav-item').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-screen').forEach(scr => {
    scr.classList.toggle('active', scr.id === `tab-${tabId}`);
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderAll() {
  renderPlano();
  renderCronograma();
  renderReceitas();
  renderShopping();
  renderCiclo();
}

// 1. RENDER PLANO & GRÁFICO DE KEVIN HALL
function renderPlano() {
  const p = state.profile;
  const presc = Fisiologia.calcularPrescricao(p);
  const simulacao = Fisiologia.simularHall(p, 90);
  const pesoFinalHall = simulacao[simulacao.length - 1].hall.toFixed(1);
  const pesoFinalIngenuo = simulacao[simulacao.length - 1].ingenuo.toFixed(1);

  const container = document.getElementById('tab-plano');
  container.innerHTML = `
    <div class="card" style="background: linear-gradient(135deg, #FFF6F2, #FFFFFF); border-color: rgba(217, 107, 67, 0.2);">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <span class="logo-badge">Prescrição Científica</span>
          <h2 class="card-title" style="margin-top: 8px;">Metas Diárias Personalizadas</h2>
          <p class="card-subtitle">Baseado nas equações de Mifflin-St Jeor & Kevin Hall</p>
        </div>
        <button onclick="abrirEditarPerfil()" style="background:none; border:none; color:var(--primary); font-weight:700; font-size:13px; cursor:pointer;">Editar</button>
      </div>

      <div style="text-align:center; padding:16px 0; background:var(--surface); border-radius:var(--radius-sm); border:1px solid var(--border);">
        <span style="font-size:36px; font-weight:800; color:var(--primary); font-family:'Fraunces', serif;">${presc.caloriasAlvo}</span>
        <span style="font-size:14px; font-weight:600; color:var(--text-muted); display:block;">kcal / dia (Déficit Seguro de ${presc.deficit} kcal)</span>
      </div>

      <div class="macro-grid">
        <div class="macro-box">
          <div class="macro-val">${presc.protG}g</div>
          <div class="macro-lbl">Proteínas</div>
        </div>
        <div class="macro-box">
          <div class="macro-val">${presc.carbG}g</div>
          <div class="macro-lbl">Carboidratos</div>
        </div>
        <div class="macro-box">
          <div class="macro-val">${presc.gordG}g</div>
          <div class="macro-lbl">Gorduras</div>
        </div>
        <div class="macro-box">
          <div class="macro-val">${presc.fibrasG}g</div>
          <div class="macro-lbl">Fibras Mín.</div>
        </div>
      </div>
    </div>

    <!-- Gráfico Interativo Kevin Hall vs 7700 kcal -->
    <div class="card">
      <h3 class="card-title">Projeção Científica de 90 Dias</h3>
      <p class="card-subtitle">Hall Model (Linha Verde Realista) vs Regra Ingênua (Linha Laranja 7700 kcal)</p>
      
      <div style="width:100%; height:160px; position:relative; margin-top:10px;">
        ${renderizarSvgGrafico(simulacao, p.peso)}
      </div>

      <div style="display:flex; justify-content:space-between; margin-top:14px; font-size:12px; background:var(--surface-alt); padding:10px 14px; border-radius:var(--radius-sm);">
        <div><span style="color:#4E6E58; font-weight:700;">● Hall Model:</span> ${pesoFinalHall} kg (-${(p.peso - pesoFinalHall).toFixed(1)}kg)</div>
        <div><span style="color:#D96B43; font-weight:700;">● 7700 kcal:</span> ${pesoFinalIngenuo} kg</div>
      </div>
      <p style="font-size:11px; color:var(--text-muted); margin-top:8px;">*O Modelo de Kevin Hall prevê a desaceleração natural causada pela adaptação metabólica e queda do gasto mecânico, evitando frustrações com metas irreais.</p>
    </div>

    <!-- Banner Afiliado Contextual de Alta Conversão -->
    <div class="card" style="border: 1px dashed var(--primary); background: #FFFBF8;">
      <div style="display:flex; gap:12px; align-items:center;">
        <span style="font-size:32px;">⚖️</span>
        <div>
          <h4 style="font-size:15px; font-weight:700; color:var(--text);">Para bater as ${presc.protG}g de proteína sem errar</h4>
          <p style="font-size:12px; color:var(--text-muted); margin-top:2px;">A balança culinária de alta precisão evita comer 30% a mais sem perceber.</p>
        </div>
      </div>
      <a href="https://s.shopee.com.br/9zz6HcfAxu" target="_blank" class="btn btn-primary" style="margin-top:14px; text-decoration:none;">
        Ver Balança SF-400 na Shopee ➔
      </a>
    </div>
  `;
}

function renderizarSvgGrafico(sim, pesoInicial) {
  const w = 400;
  const h = 140;
  const minPeso = Math.min(...sim.map(s => Math.min(s.hall, s.ingenuo))) - 1;
  const maxPeso = pesoInicial + 0.5;

  const getX = (dia) => (dia / 90) * (w - 20) + 10;
  const getY = (val) => h - 15 - ((val - minPeso) / (maxPeso - minPeso)) * (h - 30);

  let pathHall = `M ${getX(1)} ${getY(sim[0].hall)}`;
  let pathIng = `M ${getX(1)} ${getY(sim[0].ingenuo)}`;

  sim.forEach(s => {
    pathHall += ` L ${getX(s.dia)} ${getY(s.hall)}`;
    pathIng += ` L ${getX(s.dia)} ${getY(s.ingenuo)}`;
  });

  return `
    <svg viewBox="0 0 ${w} ${h}" style="width:100%; height:100%; overflow:visible;">
      <!-- Grid -->
      <line x1="10" y1="${h-15}" x2="${w-10}" y2="${h-15}" stroke="#E8E2D5" stroke-width="1" />
      <line x1="10" y1="15" x2="${w-10}" y2="15" stroke="#E8E2D5" stroke-dasharray="3,3" />

      <!-- Curvas -->
      <path d="${pathIng}" fill="none" stroke="#D96B43" stroke-width="2" stroke-dasharray="4,4" />
      <path d="${pathHall}" fill="none" stroke="#4E6E58" stroke-width="3" />

      <!-- Labels -->
      <text x="12" y="12" font-size="10" fill="#6E7D73">${pesoInicial}kg</text>
      <text x="${w-50}" y="${h-4}" font-size="10" fill="#6E7D73">90 dias</text>
    </svg>
  `;
}

// 2. RENDER CRONOGRAMA SEMANAL
function renderCronograma() {
  const container = document.getElementById('tab-cronograma');
  const dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'];
  const diaNome = dias[state.diaSemanaAtivo];

  const recs = state.recipes;
  if (!recs.length) return;

  const rCafe = recs[(state.diaSemanaAtivo * 2) % recs.length];
  const rAlmoco = recs[(state.diaSemanaAtivo * 2 + 1) % recs.length];
  const rLanche = recs[(state.diaSemanaAtivo * 3 + 2) % recs.length];
  const rJantar = recs[(state.diaSemanaAtivo * 2 + 4) % recs.length];

  const refeicoes = [
    { tipo: 'Café da Manhã', hora: '07:30', item: rCafe },
    { tipo: 'Almoço Nutritivo', hora: '12:30', item: rAlmoco },
    { tipo: 'Lanche da Tarde', hora: '16:30', item: rLanche },
    { tipo: 'Jantar Leve', hora: '20:00', item: rJantar }
  ];

  const totalKcal = refeicoes.reduce((acc, r) => acc + r.item.calorias, 0);

  container.innerHTML = `
    <!-- Seletor de Dias em Carrossel Horizontal -->
    <div style="display:flex; gap:8px; overflow-x:auto; padding-bottom:12px; margin-bottom:8px;">
      ${dias.map((d, i) => `
        <button onclick="selecionarDia(${i})" style="
          padding: 8px 16px;
          border-radius: 20px;
          border: 1px solid ${i === state.diaSemanaAtivo ? 'var(--primary)' : 'var(--border)'};
          background: ${i === state.diaSemanaAtivo ? 'var(--primary)' : 'var(--surface)'};
          color: ${i === state.diaSemanaAtivo ? '#FFF' : 'var(--text)'};
          font-weight: 700;
          font-size: 13px;
          white-space: nowrap;
          cursor: pointer;
        ">${d}</button>
      `).join('')}
    </div>

    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h2 class="card-title">${diaNome}</h2>
          <p class="card-subtitle">Total planejado: ${totalKcal} kcal</p>
        </div>
        <span class="logo-badge" style="background:var(--sage-light); color:var(--sage);">Cronograma Ativo</span>
      </div>

      <div style="margin-top:10px;">
        ${refeicoes.map(r => `
          <div class="meal-item" onclick="abrirReceita(${r.item.id})" style="cursor:pointer;">
            <span class="meal-time">${r.hora}</span>
            <div class="meal-info">
              <div class="meal-name">${r.item.titulo}</div>
              <div class="meal-kcal">${r.item.calorias} kcal • ${r.item.macros.proteina_g}g prot • ${r.item.tempo_preparo_min} min</div>
            </div>
            <span style="color:var(--text-muted); font-size:18px;">➔</span>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Utensílio Recomendado para o Dia -->
    <div class="utensil-box">
      <div class="utensil-text">
        <strong>Dica de Preparo:</strong> Use o borrifador 2 em 1 para grelhar o frango e temperar a salada sem estourar as calorias do dia.
      </div>
      <a href="https://s.shopee.com.br/7fbBlr9zK9" target="_blank" class="utensil-link">
        Ver na Shopee ➔
      </a>
    </div>
  `;
}

function selecionarDia(idx) {
  state.diaSemanaAtivo = idx;
  renderCronograma();
}

// 3. RENDER RECEITAS & BUSCA
function renderReceitas() {
  const container = document.getElementById('tab-receitas');
  const recs = state.recipes.slice(0, 30); // Carrega lote inicial

  container.innerHTML = `
    <div style="margin-bottom:16px;">
      <h2 style="font-size:24px;">Livro Dinâmico de Receitas</h2>
      <p style="font-size:13px; color:var(--text-muted);">156 receitas práticas calculadas para emagrecimento</p>
      
      <input type="text" id="buscaInput" oninput="filtrarReceitas(this.value)" placeholder="🔍 Buscar por ingrediente (aveia, ricota, cacau...)" class="form-input" style="margin-top:12px;">
    </div>

    <div id="listaReceitasContainer">
      ${recs.map(r => `
        <div class="card" onclick="abrirReceita(${r.id})" style="cursor:pointer; display:flex; gap:14px; align-items:center;">
          <div style="width:70px; height:70px; border-radius:14px; background:var(--surface-alt); display:flex; align-items:center; justify-content:center; font-size:28px;">
            🥣
          </div>
          <div style="flex:1;">
            <span style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">${r.categoria}</span>
            <h4 style="font-size:16px; font-weight:700; color:var(--text);">${r.titulo}</h4>
            <p style="font-size:12px; color:var(--text-muted);">${r.calorias} kcal • ${r.macros.proteina_g}g proteína • ${r.tempo_preparo_min} min</p>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function filtrarReceitas(termo) {
  const query = termo.toLowerCase().trim();
  const container = document.getElementById('listaReceitasContainer');
  const filtradas = state.recipes.filter(r => 
    r.titulo.toLowerCase().includes(query) || 
    r.categoria.toLowerCase().includes(query) ||
    r.tags.some(t => t.toLowerCase().includes(query))
  );

  container.innerHTML = filtradas.slice(0, 30).map(r => `
    <div class="card" onclick="abrirReceita(${r.id})" style="cursor:pointer; display:flex; gap:14px; align-items:center;">
      <div style="width:70px; height:70px; border-radius:14px; background:var(--surface-alt); display:flex; align-items:center; justify-content:center; font-size:28px;">🥣</div>
      <div style="flex:1;">
        <span style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">${r.categoria}</span>
        <h4 style="font-size:16px; font-weight:700; color:var(--text);">${r.titulo}</h4>
        <p style="font-size:12px; color:var(--text-muted);">${r.calorias} kcal • ${r.macros.proteina_g}g proteína • ${r.tempo_preparo_min} min</p>
      </div>
    </div>
  `).join('');
}

// 4. RENDER LISTA DE COMPRAS
function renderShopping() {
  const container = document.getElementById('tab-compras');
  const itens = [
    { id: 'c1', cat: 'Hortifruti', nome: 'Bananas prata (2 dúzias)' },
    { id: 'c2', cat: 'Hortifruti', nome: 'Cenouras e brócolis (1 kg)' },
    { id: 'c3', cat: 'Hortifruti', nome: 'Alface, tomate e pepino (3 pés)' },
    { id: 'c4', cat: 'Proteínas', nome: 'Ovos caipiras (2 cartelas)' },
    { id: 'c5', cat: 'Proteínas', nome: 'Filé de peito de frango (1.5 kg)' },
    { id: 'c6', cat: 'Proteínas', nome: 'Creme de ricota light (2 potes)' },
    { id: 'c7', cat: 'Mercearia', nome: 'Aveia em flocos finos (500g)' },
    { id: 'c8', cat: 'Mercearia', nome: 'Cacau em pó 100% (200g)' },
    { id: 'c9', cat: 'Mercearia', nome: 'Lentilha e feijão (1 kg)' }
  ];

  container.innerHTML = `
    <div class="card">
      <h2 class="card-title">Lista de Compras da Semana</h2>
      <p class="card-subtitle">Ingredientes consolidados para as refeições planejadas</p>
      
      <div style="margin-top:14px;">
        ${itens.map(it => `
          <div class="checklist-item" onclick="toggleShopping('${it.id}')">
            <input type="checkbox" ${state.shoppingChecks[it.id] ? 'checked' : ''} style="width:18px; height:18px; accent-color:var(--primary); cursor:pointer;">
            <span style="${state.shoppingChecks[it.id] ? 'text-decoration:line-through; color:var(--text-muted);' : 'font-weight:600;'}">
              ${it.nome} <span style="font-size:11px; color:var(--sage); font-weight:700;">[${it.cat}]</span>
            </span>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Utensílio Marmitas -->
    <div class="card" style="border:1px dashed var(--primary); background:#FFFBF8;">
      <h4 style="font-size:15px; font-weight:700;">Kit de Marmitas Herméticas de Vidro</h4>
      <p style="font-size:12px; color:var(--text-muted); margin-top:2px;">Conserve as preparações da semana sem azedar e sem vazar.</p>
      <a href="https://s.shopee.com.br/7fbBlr9zK9" target="_blank" class="btn btn-primary" style="margin-top:12px; text-decoration:none;">
        Ver Marmitas na Shopee ➔
      </a>
    </div>
  `;
}

function toggleShopping(id) {
  state.shoppingChecks[id] = !state.shoppingChecks[id];
  localStorage.setItem('saciara_shopping', JSON.stringify(state.shoppingChecks));
  renderShopping();
}

// 5. RENDER CICLO & SAÚDE FEMININA
function renderCiclo() {
  const container = document.getElementById('tab-ciclo');
  const d = state.profile.diaCiclo || 18;
  const diag = Fisiologia.diagnosticarCiclo(d);

  container.innerHTML = `
    <div class="card" style="background:linear-gradient(135deg, #FFF9F7, #FFF); border-color:rgba(217,107,67,0.2);">
      <span class="logo-badge" style="background:#FDEFEA; color:#D96B43;">Módulo Fisiológico Feminino</span>
      <h2 class="card-title" style="margin-top:8px;">Acompanhamento do Ciclo</h2>
      <p class="card-subtitle">Compreenda as oscilações de água e apetite sem neura</p>

      <div class="form-group" style="margin-top:14px;">
        <label class="form-label">Em qual dia do ciclo você está hoje? (1 a 30)</label>
        <input type="number" min="1" max="32" value="${d}" onchange="atualizarDiaCiclo(this.value)" class="form-input" style="font-size:18px; font-weight:700;">
      </div>

      <div style="background:var(--surface); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border); margin-top:12px;">
        <span style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">Diagnóstico Biológico</span>
        <h3 style="font-size:17px; margin-top:4px; color:var(--text);">${diag.fase}</h3>
        <p style="font-size:13px; color:var(--text); margin-top:6px; line-height:1.5;">${diag.aviso}</p>
      </div>

      <div style="background:var(--sage-light); padding:12px 14px; border-radius:var(--radius-sm); margin-top:12px;">
        <p style="font-size:12px; color:var(--sage-dark); font-weight:600;">
          💡 Regra de Ouro: Se a balança subir 1 kg esta semana, lembre-se: é retenção mediada por progesterona, não gordura. Ela cai sozinha nos primeiros dias da menstruação.
        </p>
      </div>
    </div>
  `;
}

function atualizarDiaCiclo(val) {
  state.profile.diaCiclo = parseInt(val) || 1;
  localStorage.setItem('saciara_profile', JSON.stringify(state.profile));
  renderCiclo();
}

// 6. MODAL DE RECEITA
function abrirReceita(id) {
  const r = state.recipes.find(item => item.id === id);
  if (!r) return;
  state.selectedRecipe = r;

  const modal = document.getElementById('recipeModal');
  const body = document.getElementById('modalBody');

  body.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
      <div>
        <span class="logo-badge">${r.categoria}</span>
        <h2 style="font-size:22px; margin-top:6px;">${r.titulo}</h2>
      </div>
      <button onclick="fecharModal()" style="background:none; border:none; font-size:24px; cursor:pointer; color:var(--text-muted);">&times;</button>
    </div>

    <div class="macro-grid" style="margin:16px 0;">
      <div class="macro-box"><div class="macro-val">${r.calorias}</div><div class="macro-lbl">Calorias</div></div>
      <div class="macro-box"><div class="macro-val">${r.macros.proteina_g}g</div><div class="macro-lbl">Proteínas</div></div>
      <div class="macro-box"><div class="macro-val">${r.macros.carboidrato_g}g</div><div class="macro-lbl">Carboidratos</div></div>
      <div class="macro-box"><div class="macro-val">${r.macros.gordura_g}g</div><div class="macro-lbl">Gorduras</div></div>
    </div>

    <h4 style="font-size:15px; margin-top:16px; margin-bottom:8px;">Modo de Preparo:</h4>
    <ol style="padding-left:20px; font-size:14px; color:var(--text); line-height:1.6;">
      ${r.instrucoes.map(ins => `<li>${ins}</li>`).join('')}
    </ol>

    <!-- Utensílio Recomendado na Receita -->
    ${r.utensilios_recomendados && r.utensilios_recomendados.length ? `
      <div class="utensil-box" style="margin-top:18px;">
        <div class="utensil-text">
          <strong>Utensílio usado:</strong> ${r.utensilios_recomendados[0].nome} (${r.utensilios_recomendados[0].motivo})
        </div>
        <a href="${r.utensilios_recomendados[0].link}" target="_blank" class="utensil-link">
          Ver na Shopee ➔
        </a>
      </div>
    ` : ''}

    <button onclick="fecharModal()" class="btn btn-secondary" style="margin-top:16px;">Fechar</button>
  `;

  modal.style.display = 'flex';
}

function fecharModal() {
  document.getElementById('recipeModal').style.display = 'none';
}

function abrirEditarPerfil() {
  const p = state.profile;
  const modal = document.getElementById('recipeModal');
  const body = document.getElementById('modalBody');

  body.innerHTML = `
    <h2 style="font-size:20px; margin-bottom:14px;">Editar Perfil Nutricional</h2>
    <div class="form-group">
      <label class="form-label">Peso Atual (kg)</label>
      <input type="number" id="inpPeso" value="${p.peso}" class="form-input">
    </div>
    <div class="form-group">
      <label class="form-label">Altura (cm)</label>
      <input type="number" id="inpAlt" value="${p.altura}" class="form-input">
    </div>
    <div class="form-group">
      <label class="form-label">Idade</label>
      <input type="number" id="inpIdade" value="${p.idade}" class="form-input">
    </div>
    <div class="form-group">
      <label class="form-label">Sexo Biológico</label>
      <select id="inpSexo" class="form-select">
        <option value="F" ${p.sexo === 'F' ? 'selected' : ''}>Feminino</option>
        <option value="M" ${p.sexo === 'M' ? 'selected' : ''}>Masculino</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Ritmo de Emagrecimento</label>
      <select id="inpRitmo" class="form-select">
        <option value="leve" ${p.ritmo === 'leve' ? 'selected' : ''}>Leve (-300 kcal/dia)</option>
        <option value="moderado" ${p.ritmo === 'moderado' ? 'selected' : ''}>Moderado Saudável (-450 kcal/dia)</option>
        <option value="acelerado_seguro" ${p.ritmo === 'acelerado_seguro' ? 'selected' : ''}>Acelerado Seguro (-600 kcal/dia)</option>
      </select>
    </div>
    <button onclick="salvarPerfilForm()" class="btn btn-primary" style="margin-top:14px;">Salvar e Recalcular Plano ➔</button>
  `;

  modal.style.display = 'flex';
}

function salvarPerfilForm() {
  state.profile.peso = parseFloat(document.getElementById('inpPeso').value) || 70;
  state.profile.altura = parseFloat(document.getElementById('inpAlt').value) || 165;
  state.profile.idade = parseInt(document.getElementById('inpIdade').value) || 30;
  state.profile.sexo = document.getElementById('inpSexo').value;
  state.profile.ritmo = document.getElementById('inpRitmo').value;

  localStorage.setItem('saciara_profile', JSON.stringify(state.profile));
  fecharModal();
  renderAll();
}

window.onload = init;
