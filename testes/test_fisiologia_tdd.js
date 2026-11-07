const assert = require('assert');
const FisiologiaNutriPlus = require('../js/fisiologia_nutriplus');

console.log("=== INICIANDO SUÍTE TDD: FisiologiaNutriPlus ===");

// 1. Teste TMB Mifflin-St Jeor (Mulher: 70.8kg, 165cm, 32 anos)
// 10*70.8 + 6.25*165 - 5*32 - 161 = 708 + 1031.25 - 160 - 161 = 1418.25 -> ~1418 kcal
const tmb = FisiologiaNutriPlus.calcularTMB(70.8, 165, 32, 'feminino');
console.log(`[TEST 1] TMB Calculada: ${tmb} kcal`);
assert(tmb >= 1410 && tmb <= 1430, `TMB esperada entre 1410 e 1430, obtido: ${tmb}`);

// 2. Teste TDEE (Moderado: fator 1.55)
// 1418 * 1.55 = ~2198 kcal
const tdee = FisiologiaNutriPlus.calcularTDEE(tmb, 'moderado');
console.log(`[TEST 2] TDEE Calculado: ${tdee} kcal`);
assert(tdee >= 2100 && tdee <= 2250, `TDEE esperado ~2200, obtido: ${tdee}`);

// 3. Teste Perda de Gordura com Déficit de 475 kcal/dia
// (475 * 30) / 7700 = 14250 / 7700 = ~1.85 -> 1.9 kg
const perda = FisiologiaNutriPlus.calcularPerdaGorduraMensal(475);
console.log(`[TEST 3] Perda de Gordura Prevista: ${perda} kg`);
assert(perda === 1.9, `Perda esperada 1.9 kg, obtido: ${perda}`);

// 4. Teste Distribuição de Macros (1800 kcal, 70.8kg)
// Proteína: 70.8 * 1.8 = ~127g (127 * 4 = 508 kcal)
// Gordura: 1800 * 0.25 = 450 kcal / 9 = 50g
// Carbo: 1800 - 508 - 450 = 842 kcal / 4 = 210g
const macros = FisiologiaNutriPlus.distribuirMacros(1800, 70.8);
console.log(`[TEST 4] Macros: Prot ${macros.proteinas}g, Gord ${macros.gorduras}g, Carb ${macros.carboidratos}g`);
assert(macros.proteinas >= 125 && macros.proteinas <= 130, "Proteínas devem estar na faixa de 1.8g/kg");
assert(macros.gorduras >= 45 && macros.gorduras <= 55, "Gorduras devem ser ~25% do valor calórico");
assert(macros.carboidratos > 180, "Carboidratos devem suprir o restante energético");

// 5. Teste Cálculo Dinâmico de Pratos Cobertos por Orçamento
const cobBaixa = FisiologiaNutriPlus.calcularCoberturaDespensa(250, 860);
console.log(`[TEST 5.1] Orçamento R$ 250 -> ${cobBaixa.pratos} pratos, ${cobBaixa.dias} dias`);
assert(cobBaixa.pratos < 100, "Com R$ 250 deve cobrir menos de 100 pratos");

const cobMedia = FisiologiaNutriPlus.calcularCoberturaDespensa(750, 860);
console.log(`[TEST 5.2] Orçamento R$ 750 -> ${cobMedia.pratos} pratos, ${cobMedia.dias} dias`);
assert(cobMedia.pratos >= 125 && cobMedia.pratos <= 135, "Com R$ 750 deve cobrir ~130 pratos");

const cobAlta = FisiologiaNutriPlus.calcularCoberturaDespensa(1200, 860);
console.log(`[TEST 5.3] Orçamento R$ 1200 -> ${cobAlta.pratos} pratos, ${cobAlta.dias} dias`);
assert(cobAlta.pratos === 150 && cobAlta.dias === 30, "Com orçamento pleno deve cobrir 150 pratos e 30 dias");

console.log("=== 100% DOS TESTES TDD FISIOLÓGICOS PASSARAM COM SUCESSO! ===");
