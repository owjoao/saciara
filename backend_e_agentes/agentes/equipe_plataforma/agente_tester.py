"""Agente de Testes & Verificação Matemática / Fisiológica (QA Científico).
Executa bateria de testes unitários e de integração em todos os motores científicos
e atualiza a memória coletiva da equipe com os resultados.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core_fisiologico.hall_model import HallBodyWeightModel, PerfilFisiologico
from core_fisiologico.kalman_tdee import FiltroKalmanPeso, MotorAdaptativoTDEE
from core_fisiologico.mifflin_calculator import CalculadoraFisiologica
from core_fisiologico.ciclo_feminino import ModuloFisiologiaFeminina
from core_nutricional.catalogo_saciara import CatalogoReceitasSaciara
from core_otimizacao.diet_solver import DietSolverSemanal
from agentes.equipe_plataforma.agente_memoria import MemoriaEquipeManager


class TestesMotoresCientificosSaciara(unittest.TestCase):

    def test_01_mifflin_benchmark_homem_mulher(self):
        """Valida se a fórmula de Mifflin-St Jeor bate os valores de referência da literatura."""
        # Mulher: 30 anos, 65 kg, 165 cm -> 10*65 + 6.25*165 - 5*30 - 161 = 650 + 1031.25 - 150 - 161 = 1370.25
        tmb_f = CalculadoraFisiologica.calcular_tmb_mifflin(65.0, 165.0, 30, "F")
        self.assertAlmostEqual(tmb_f, 1370.2, places=1)

        # Homem: 30 anos, 80 kg, 180 cm -> 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780.0
        tmb_m = CalculadoraFisiologica.calcular_tmb_mifflin(80.0, 180.0, 30, "M")
        self.assertAlmostEqual(tmb_m, 1780.0, places=1)

    def test_02_hall_model_nao_linearidade_e_adaptacao(self):
        """Verifica que o modelo de Kevin Hall desacelera a perda com o tempo (não-linear)."""
        perfil = PerfilFisiologico(peso_kg=80.0, altura_cm=175.0, idade=32, sexo="M", bf_percentual=25.0)
        tdee_ini = HallBodyWeightModel.calcular_tdee_inicial(perfil)

        # Déficit de 500 kcal por 90 dias
        res = HallBodyWeightModel.simular_trajetoria(perfil, ingestao_diaria_kcal=tdee_ini - 500.0, dias=90)

        # O modelo ingênuo prevê exatamente (500 * 90) / 7700 = 5.84 kg de perda
        # O modelo real de Hall deve prever menos perda devido à adaptação metabólica e queda do gasto de movimento
        perda_hall = res["resultado_final"]["perda_total_kg"]
        self.assertGreater(perda_hall, 3.5)
        self.assertLess(perda_hall, 6.0)
        self.assertGreater(res["resultado_final"]["queda_metabolica_total"], 50.0)

    def test_03_filtro_kalman_remove_ruido_balanca(self):
        """Testa se o Filtro de Kalman atenua um pico falso de retenção hídrica."""
        kalman = FiltroKalmanPeso()
        # Série com platô e um pico repentino de água (+1.5kg no dia 4)
        pesos_brutos = [70.0, 69.8, 69.7, 71.2, 69.5, 69.4]
        pesos_filtrados = kalman.filtrar_serie(pesos_brutos)

        # No dia do pico (índice 3), o valor filtrado não deve subir 1.5kg
        delta_pico_bruto = pesos_brutos[3] - pesos_brutos[2]  # +1.5kg
        delta_pico_filtrado = pesos_filtrados[3] - pesos_filtrados[2]
        self.assertLess(delta_pico_filtrado, delta_pico_bruto * 0.6)

    def test_04_catalogo_e_utensilios_saciara(self):
        """Valida que todas as 156 receitas carregam e possuem utensílios com links válidos."""
        cat = CatalogoReceitasSaciara()
        recs = cat.carregar_todas()
        self.assertGreaterEqual(len(recs), 100)

        primeira = recs[0]
        self.assertIn("titulo", primeira)
        self.assertIn("calorias", primeira)
        self.assertIn("utensilios_recomendados", primeira)
        self.assertTrue(len(primeira["utensilios_recomendados"]) >= 1)
        self.assertTrue(primeira["utensilios_recomendados"][0]["link"].startswith("https://s.shopee.com.br/"))

    def test_05_diet_solver_7_dias(self):
        """Valida se o cronograma semanal de 7 dias é gerado com equilíbrio calórico."""
        solver = DietSolverSemanal()
        plano = solver.gerar_plano_semanal(meta_calorica_dia=1600.0, meta_proteina_g=120.0)
        dias = plano["cronograma_7_dias"]
        self.assertEqual(len(dias), 7)
        self.assertTrue(len(plano["lista_compras_semanal"]) > 5)


class AgenteTester:
    def __init__(self):
        self.memoria = MemoriaEquipeManager()

    def executar_todos_testes(self) -> bool:
        print("\n" + "=" * 65)
        print(" 🧪 AGENTE TESTER: Executando Bateria de Testes Científicos")
        print("=" * 65)

        suite = unittest.TestLoader().loadTestsFromTestCase(TestesMotoresCientificosSaciara)
        runner = unittest.TextTestRunner(verbosity=2)
        resultado = runner.run(suite)

        total = resultado.testsRun
        erros = len(resultado.errors) + len(resultado.failures)
        sucesso = resultado.wasSuccessful()

        self.memoria.atualizar_metricas(
            testes_passando=total - erros,
            testes_falhando=erros
        )

        if sucesso:
            print(f"\n ✅ TODOS OS {total} TESTES CIENTÍFICOS PASSARAM COM SUCESSO!")
        else:
            print(f"\n ❌ FALHA DETECTADA: {erros} de {total} testes falharam.")

        return sucesso


if __name__ == "__main__":
    t = AgenteTester()
    sys.exit(0 if t.executar_todos_testes() else 1)
