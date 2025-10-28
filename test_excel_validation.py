"""
Valida biblioteca Paraconsistent contra valores de referência da planilha PAL2v.xlsx

Estrutura da planilha:
- Linha 0: Headers em inglês
- Linha 1: Abreviações (FL, FtC, FD, μ, λ, GC, GCT, etc.)
- Linhas 2-39: Dados de teste (38 casos)

Colunas mapeadas (apenas as que existem no programa atual):
- Col 1: FtC (Certainty Control Limit)
- Col 11: μ (mu - input favorável)
- Col 12: λ (lam - input desfavorável)
- Col 13: GC (gc - Grau de Certeza)
- Col 14: GCT (gct - Grau de Contradição)
- Col 16: d (distância radial)
- Col 17: D (distância normalizada)
- Col 18: GCR (gcr - Grau de Certeza Radial)
- Col 19: φ (phi - Intervalo de certeza)
- Col 20: μE (muE - Resulting Evidence Degree)
- Col 22: μECT (muECT - Resulting Contradiction Degree)
- Col 23: μER (muER - Resulting Real Evidence Degree) ⚠️ CORRIGIDO
- Col 24: φE (phiE - alias de phi)
"""

import pandas as pd
from paraconsistent.blocks import ParaconsistentBlock

def load_test_cases(excel_path):
    """Carrega casos de teste do Excel, pulando linhas de header"""
    # Ler Excel pulando primeiras 2 linhas (headers)
    df = pd.read_excel(excel_path, sheet_name=0, header=None, skiprows=2)

    # Dar nomes às colunas baseado na linha 1 (abreviações)
    # Ler linha 1 separadamente para pegar os nomes
    df_headers = pd.read_excel(excel_path, sheet_name=0, header=None, nrows=2)

    return df, df_headers

def run_test_case(mu, lam, ftc):
    """Executa um caso de teste"""
    b = ParaconsistentBlock()

    # Configurar FtC se não for NaN
    if pd.notna(ftc):
        b.config.FtC = ftc
    else:
        b.config.FtC = 0.5  # Default

    b.input.mu = mu
    b.input.lam = lam

    results = {
        'gc': b.complete.gc,
        'gct': b.complete.gct,
        'd': b.complete.d,
        'D': b.complete.D,
        'gcr': b.complete.gcr,
        'phi': b.complete.phi,
        'muE': b.complete.muE,
        'muECT': b.complete.muECT,
        'muER': b.complete.muER,
        'phiE': b.complete.phiE,
        'decision_output': b.complete.decision_output
    }

    return results

def compare_with_tolerance(actual, expected, tolerance=0.001):
    """Compara valores com tolerância"""
    if expected is None or pd.isna(expected):
        return True, 0.0  # Skip if no expected value

    diff = abs(actual - expected)
    passed = diff < tolerance
    return passed, diff

def main():
    excel_path = r'C:\Users\SERVIDOR1\Downloads\PAL2v.xlsx'

    print("=" * 80)
    print("VALIDACAO CONTRA PLANILHA PAL2v.xlsx")
    print("=" * 80)

    df, df_headers = load_test_cases(excel_path)

    # Mapear índices de colunas
    # Baseado na análise: linha 1 tem as abreviações
    col_map = {
        'FtC': 1,    # Fator de Tolerância à Certeza
        'mu': 11,    # μ
        'lam': 12,   # λ
        'gc': 13,    # GC
        'gct': 14,   # GCT
        'd': 16,     # d
        'D': 17,     # D
        'gcr': 18,   # GCR
        'phi': 19,   # φ
        'muE': 20,   # μE
        'muECT': 22, # μECT
        'muER': 23,  # μER
        'phiE': 24   # φE
    }

    total_tests = len(df)
    passed_tests = 0
    failed_tests = []

    print(f"\nTotal de casos na planilha: {total_tests}")
    print(f"Validando apenas casos com valores de mu e lambda...\n")

    tested_count = 0
    for idx, row in df.iterrows():
        mu = row[col_map['mu']]
        lam = row[col_map['lam']]
        ftc = row[col_map['FtC']]

        # Pular linhas sem dados de teste
        if pd.isna(mu) or pd.isna(lam):
            continue

        tested_count += 1

        # Executar teste
        try:
            results = run_test_case(mu=mu, lam=lam, ftc=ftc if pd.notna(ftc) else 0.5)
        except Exception as e:
            print(f"[ERROR] Linha {idx+3}: Erro ao executar teste: {e}")
            failed_tests.append({
                'line': idx+3,
                'mu': mu,
                'lam': lam,
                'error': str(e),
                'errors': []
            })
            continue

        # Validar cada campo
        test_passed = True
        errors = []
        max_diff = 0.0

        for field, col_idx in col_map.items():
            if field in ['FtC', 'mu', 'lam']:  # Inputs
                continue

            expected = row[col_idx]

            if pd.notna(expected):
                actual = results[field]
                passed, diff = compare_with_tolerance(actual, expected)
                max_diff = max(max_diff, diff)

                if not passed:
                    test_passed = False
                    errors.append({
                        'field': field,
                        'actual': actual,
                        'expected': expected,
                        'diff': diff
                    })

        if test_passed:
            passed_tests += 1
            print(f"[OK] Linha {idx+3}: mu={mu:.4f}, lam={lam:.4f} (max diff: {max_diff:.6f})")
        else:
            failed_tests.append({
                'line': idx+3,
                'mu': mu,
                'lam': lam,
                'ftc': ftc if pd.notna(ftc) else 0.5,
                'errors': errors
            })
            print(f"[FAIL] Linha {idx+3}: mu={mu:.4f}, lam={lam:.4f}")
            for error in errors:
                print(f"  - {error['field']}: got {error['actual']:.6f}, "
                      f"expected {error['expected']:.6f} (diff: {error['diff']:.6f})")

    # Relatório final
    print("\n" + "=" * 80)
    print(f"RESULTADOS FINAIS")
    print("=" * 80)
    print(f"Total de linhas na planilha: {total_tests}")
    print(f"Casos testados (com mu e lambda): {tested_count}")
    print(f"Passaram: {passed_tests}")
    print(f"Falharam: {len(failed_tests)}")
    if tested_count > 0:
        print(f"Taxa de sucesso: {(passed_tests/tested_count)*100:.2f}%")

    if failed_tests:
        print("\n" + "=" * 80)
        print("DETALHES DOS TESTES QUE FALHARAM")
        print("=" * 80)
        for failed in failed_tests:
            print(f"\nLinha {failed['line']}:")
            # Converter para float se for string
            mu_val = float(failed['mu']) if not isinstance(failed['mu'], str) else failed['mu']
            lam_val = float(failed['lam']) if not isinstance(failed['lam'], str) else failed['lam']
            ftc_val = float(failed.get('ftc', 0.5)) if not isinstance(failed.get('ftc', 0.5), str) else 0.5

            if isinstance(mu_val, str) or isinstance(lam_val, str):
                mu_safe = str(failed['mu']).encode('ascii', 'replace').decode('ascii')
                lam_safe = str(failed['lam']).encode('ascii', 'replace').decode('ascii')
                print(f"  Inputs: mu={mu_safe}, lam={lam_safe} (valores nao numericos)")
            else:
                print(f"  Inputs: mu={mu_val:.4f}, lam={lam_val:.4f}, FtC={ftc_val:.4f}")

            if 'error' in failed:
                print(f"  Erro de execucao: {failed['error']}")
            else:
                print(f"  Campos divergentes: {len(failed['errors'])}")
                for error in failed['errors']:
                    print(f"    {error['field']}: got {error['actual']:.6f}, "
                          f"expected {error['expected']:.6f} (diff: {error['diff']:.6f})")

    return len(failed_tests) == 0

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
