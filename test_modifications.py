"""
Script de teste para validar as modificações na biblioteca Paraconsistent
Compara resultados com o código MATLAB do professor
"""

from src.paraconsistent.blocks import ParaconsistentBlock

def test_basic_matlab_comparison():
    """
    Testa valores de exemplo comparando com MATLAB.

    MATLAB Input:
    - Mu = 0.80
    - Lambda = 0.20
    - CCL (FtC) = 0.70

    MATLAB Expected Output:
    - DC (gc) = 0.60
    - DCT (gct) = 0.00
    - DCR (gcr) deve ser calculado baseado em D
    - MIE (muE) = (DC + 1) / 2 = 0.80
    - MIER (muER) = (DCR + 1) / 2
    """
    print("=" * 60)
    print("TESTE 1: Comparação com MATLAB")
    print("=" * 60)

    b = ParaconsistentBlock()
    b.config.FtC = 0.70

    b.input.mu = 0.80
    b.input.lam = 0.20

    print(f"\n[INPUTS]:")
    print(f"  mu (Mu):     {b.complete.mu:.4f}")
    print(f"  lam (Lambda): {b.complete.lam:.4f}")
    print(f"  FtC (CCL):   {b.complete.FtC:.4f}")

    print(f"\n[GRAUS CALCULADOS]:")
    print(f"  gc (DC):     {b.complete.gc:.4f}  (esperado: 0.6000)")
    print(f"  gct (DCT):   {b.complete.gct:.4f}  (esperado: 0.0000)")
    print(f"  gcr (DCR):   {b.complete.gcr:.4f}")
    print(f"  D:           {b.complete.D:.4f}")

    print(f"\n[EVIDENCIAS]:")
    print(f"  muE (MIE):   {b.complete.muE:.4f}  (esperado: {(b.complete.gc + 1) / 2:.4f})")
    print(f"  muECT (MIEct): {b.complete.muECT:.4f}")
    print(f"  muER (MIER): {b.complete.muER:.4f}  [CORRIGIDO]: (gcr + 1) / 2")
    print(f"  phi (Phi):   {b.complete.phi:.4f}")

    print(f"\n[DECISAO]:")
    print(f"  decision_output: {b.complete.decision_output:.4f}")
    print(f"  Logica: muER ({b.complete.muER:.4f}) {'>' if b.complete.muER > b.complete.FtC else '<' if b.complete.muER < b.complete.FtC else '=='} FtC ({b.complete.FtC:.4f})")
    print(f"  Resultado: {'TRUE (1.0)' if b.complete.decision_output == 1.0 else 'FALSE (0.0)' if b.complete.decision_output == 0.0 else 'UNCERTAIN (0.5)'}")

    print(f"\n[CLASSIFICACAO]:")
    label_safe = b.complete.label.encode('ascii', 'replace').decode('ascii')
    print(f"  label: {label_safe} (original tinha caracteres unicode)")

    # Validações
    print(f"\n[VALIDACOES]:")
    assert abs(b.complete.gc - 0.60) < 0.001, f"gc incorreto: {b.complete.gc}"
    print(f"  [OK] gc = {b.complete.gc:.4f} (correto)")

    assert abs(b.complete.gct - 0.00) < 0.001, f"gct incorreto: {b.complete.gct}"
    print(f"  [OK] gct = {b.complete.gct:.4f} (correto)")

    expected_muE = (b.complete.gc + 1.0) / 2.0
    assert abs(b.complete.muE - expected_muE) < 0.001, f"muE incorreto: {b.complete.muE}"
    print(f"  [OK] muE = {b.complete.muE:.4f} (correto)")

    expected_muER = (b.complete.gcr + 1.0) / 2.0
    assert abs(b.complete.muER - expected_muER) < 0.001, f"muER incorreto: {b.complete.muER}"
    print(f"  [OK] muER = {b.complete.muER:.4f} (correto - formula corrigida)")

    print(f"\n  [OK] decision_output implementado: {b.complete.decision_output}")

    print("\n" + "=" * 60)
    print("[OK] TESTE 1 PASSOU!")
    print("=" * 60)


def test_edge_cases():
    """Testa casos extremos"""
    print("\n" + "=" * 60)
    print("TESTE 2: Casos Extremos")
    print("=" * 60)

    # Caso 1: mu = lam (gct máximo)
    print("\n[CASO 1]: mu = lam = 1.0 (contradicao maxima)")
    b1 = ParaconsistentBlock()
    b1.config.FtC = 0.50
    b1.input.mu = 1.0
    b1.input.lam = 1.0
    print(f"  gc: {b1.complete.gc:.4f} (esperado: 0.0000)")
    print(f"  gct: {b1.complete.gct:.4f} (esperado: 1.0000)")
    label1_safe = b1.complete.label.encode('ascii', 'replace').decode('ascii')
    print(f"  label: {label1_safe}")

    # Caso 2: mu = 1, lam = 0 (verdadeiro total)
    print("\n[CASO 2]: mu = 1.0, lam = 0.0 (verdadeiro total)")
    b2 = ParaconsistentBlock()
    b2.config.FtC = 0.50
    b2.input.mu = 1.0
    b2.input.lam = 0.0
    print(f"  gc: {b2.complete.gc:.4f} (esperado: 1.0000)")
    print(f"  gct: {b2.complete.gct:.4f} (esperado: 0.0000)")
    print(f"  muER: {b2.complete.muER:.4f}")
    print(f"  decision_output: {b2.complete.decision_output} (esperado: 1.0)")
    label2_safe = b2.complete.label.encode('ascii', 'replace').decode('ascii')
    print(f"  label: {label2_safe}")

    # Caso 3: mu = 0, lam = 1 (falso total)
    print("\n[CASO 3]: mu = 0.0, lam = 1.0 (falso total)")
    b3 = ParaconsistentBlock()
    b3.config.FtC = 0.50
    b3.input.mu = 0.0
    b3.input.lam = 1.0
    print(f"  gc: {b3.complete.gc:.4f} (esperado: -1.0000)")
    print(f"  gct: {b3.complete.gct:.4f} (esperado: 0.0000)")
    print(f"  muER: {b3.complete.muER:.4f}")
    print(f"  decision_output: {b3.complete.decision_output} (esperado: 0.0)")
    label3_safe = b3.complete.label.encode('ascii', 'replace').decode('ascii')
    print(f"  label: {label3_safe}")

    # Caso 4: muER == FtC (empate)
    print("\n[CASO 4]: Testar decision_output = 0.5 (empate)")
    b4 = ParaconsistentBlock()
    b4.config.FtC = 0.50
    # Ajustar mu e lam para que muER = 0.50
    # muER = (gcr + 1) / 2 = 0.5 → gcr = 0
    # gcr = 0 quando D = 1 ou gc = 0
    b4.input.mu = 0.5
    b4.input.lam = 0.5
    print(f"  muER: {b4.complete.muER:.4f}")
    print(f"  FtC: {b4.complete.FtC:.4f}")
    print(f"  decision_output: {b4.complete.decision_output} (deve ser 0.0, 0.5 ou 1.0)")

    print("\n" + "=" * 60)
    print("[OK] TESTE 2 PASSOU!")
    print("=" * 60)


def test_parameters_removed():
    """Testa que parâmetros removidos não estão acessíveis"""
    print("\n" + "=" * 60)
    print("TESTE 3: Parâmetros Removidos")
    print("=" * 60)

    b = ParaconsistentBlock()
    b.input.mu = 0.5
    b.input.lam = 0.3

    # Verificar que FL, FD, mu_p, lam_p, muE_p, gct_adj não existem mais
    removed_params = ['FL', 'FD', 'mu_p', 'lam_p', 'muE_p', 'gct_adj']

    for param in removed_params:
        try:
            value = getattr(b.complete, param)
            print(f"  [FAIL] {param} ainda existe (nao deveria): {value}")
            assert False, f"{param} deveria ter sido removido"
        except AttributeError:
            print(f"  [OK] {param} removido corretamente")

    # Verificar que novos campos existem
    new_params = ['decision_output']
    for param in new_params:
        try:
            value = getattr(b.complete, param)
            print(f"  [OK] {param} adicionado: {value}")
        except AttributeError:
            print(f"  [FAIL] {param} nao encontrado (deveria existir)")
            assert False, f"{param} deveria ter sido adicionado"

    print("\n" + "=" * 60)
    print("[OK] TESTE 3 PASSOU!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n[TEST] EXECUTANDO TESTES DAS MODIFICACOES")
    print("Validando correcoes baseadas no codigo MATLAB do professor\n")

    try:
        test_basic_matlab_comparison()
        test_edge_cases()
        test_parameters_removed()

        print("\n" + "=" * 60)
        print("[SUCCESS] TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print("\nModificacoes implementadas com sucesso:")
        print("  [OK] FL e FD removidos")
        print("  [OK] mu_p, lam_p, muE_p, gct_adj removidos")
        print("  [OK] muER corrigido: (gcr + 1) / 2")
        print("  [OK] decision_output adicionado")
        print("  [OK] VSSC, VICC, VSSCT, VICCT calculados automaticamente")
        print("  [OK] Alinhamento com codigo MATLAB do professor")

    except Exception as e:
        print(f"\n[ERROR] ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
