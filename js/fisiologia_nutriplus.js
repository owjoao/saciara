const FisiologiaNutriPlus = {
  /**
   * Cálculo da Taxa Metabólica Basal (TMB / BMR) via fórmula de Mifflin-St Jeor
   */
  calcularTMB(pesoKg, alturaCm, idadeAnos, sexo = 'feminino') {
    if (!pesoKg || !alturaCm || !idadeAnos) return 1450;
    // Mifflin-St Jeor:
    // Homens: 10 * peso + 6.25 * altura - 5 * idade + 5
    // Mulheres: 10 * peso + 6.25 * altura - 5 * idade - 161
    const base = (10 * pesoKg) + (6.25 * alturaCm) - (5 * idadeAnos);
    return Math.round(sexo === 'masculino' ? base + 5 : base - 161);
  },

  /**
   * Cálculo do Gasto Energético Total Diário (TDEE)
   */
  calcularTDEE(tmb, nivelAtividade = 'moderado') {
    const fatores = {
      sedentario: 1.2,
      leve: 1.375,
      moderado: 1.55,
      intenso: 1.725,
      atleta: 1.9
    };
    const fator = fatores[nivelAtividade] || 1.45;
    return Math.round(tmb * fator);
  },

  /**
   * Modelo de Forbes / Kevin Hall: partição fisiológica de perda de gordura
   */
  calcularPerdaGorduraMensal(deficitDiarioKcal) {
    if (!deficitDiarioKcal || deficitDiarioKcal <= 0) return 0;
    // 1 kg de gordura corporal pura equivale a ~7.700 kcal
    const deficitMensal = deficitDiarioKcal * 30;
    const kgGordura = deficitMensal / 7700;
    return Number(kgGordura.toFixed(1));
  },

  /**
   * Distribuição de Macronutrientes com foco em preservação de massa magra
   */
  distribuirMacros(kcalAlvo, pesoKg) {
    // 1.8g de proteína por kg de peso corporal
    const proteinaG = Math.round(pesoKg * 1.8);
    const kcalProt = proteinaG * 4;

    // 25% das calorias totais em gorduras saudáveis
    const kcalGord = kcalAlvo * 0.25;
    const gorduraG = Math.round(kcalGord / 9);

    // O restante das calorias em carboidratos complexos
    const kcalCarb = Math.max(0, kcalAlvo - kcalProt - kcalGord);
    const carboidratoG = Math.round(kcalCarb / 4);

    return {
      calorias: kcalAlvo,
      proteinas: proteinaG,
      gorduras: gorduraG,
      carboidratos: carboidratoG
    };
  },

  /**
   * Cálculo dinâmico de pratos cobertos e dias de despensa
   */
  calcularCoberturaDespensa(orcamentoReais, totalCestaMensal, totalPratosPrescritos = 150) {
    if (!totalCestaMensal || totalCestaMensal <= 0) {
      return { pratos: totalPratosPrescritos, dias: 30 };
    }
    const proporcao = Math.min(1.0, Math.max(0.2, orcamentoReais / totalCestaMensal));
    const pratos = Math.round(totalPratosPrescritos * proporcao);
    const dias = Math.max(1, Math.round(30 * proporcao));
    return { pratos, dias };
  }
};

// Exportação universal (Node.js & Navegador)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FisiologiaNutriPlus;
} else if (typeof window !== 'undefined') {
  window.FisiologiaNutriPlus = FisiologiaNutriPlus;
}
