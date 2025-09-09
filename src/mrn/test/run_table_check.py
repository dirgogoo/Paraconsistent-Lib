# tests/run_table_check.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import math
from typing import Dict, Any, List, Optional, Tuple

# ====== IMPORTA O SEU BLOCO ======
# Ajuste o import conforme seu projeto
from mrn.paraconsistent.block import ParaconsistentBlock

# ====== CONFIG ======

# Coloque aqui sua tabela como CSV. Pode usar vírgula OU ponto decimal.
# Cabeçalho esperado (ordem é importante):
# FL,FtC,FD,VSSC,VICC,VSSCT,VICCT,VlV,VlF,mu_p,lam_p,mu,lam,GC,GCT,S1,d,D,GCR,phi,muE,muE_p,muECT,muER,phiE,label
USER_CSV = r"""
FL,FtC,FD,VSSC,VICC,VSSCT,VICCT,VlV,VlF,mu_p,lam_p,mu,lam,GC,GCT,S1,d,D,GCR,phi,muE,muE_p,muECT,muER,phiE,label
,0,5,,0,5,-0,5,0,5,-0,5,0,5,0,5,,1,00,0,00,1,00,0,00,V,0,00,0,00,1,00,1,00,1,00,,0,50,1,00,1,00
,0,5,,0,5,-0,5,0,5,-0,5,0,5,0,5,,0,00,1,00,-1,00,0,00,F,0,00,0,00,-1,00,1,00,0,00,,0,50,0,00,1,00
,0,5,,0,5,-0,5,0,5,-0,5,0,5,0,5,,0,70,0,60,0,10,0,30,Q┬ → V,0,95,0,95,0,05,0,70,0,55,,0,65,0,53,0,70
,0,5,,0,5,-0,5,0,5,-0,5,0,5,0,5,,0,50,0,80,-0,30,0,30,QF→ ┬,0,76,0,76,-0,24,0,70,0,35,,0,65,0,38,0,70
,0,5,,0,5,-0,5,0,5,-0,5,0,5,0,5,,0,30,0,75,-0,45,0,05,QF→ ┬,0,55,0,55,-0,45,0,95,0,28,,0,53,0,28,0,95
,0,5,,0,5,-0,5,0,5,-0,5,0,5,0,5,,0,85,0,36,0,49,0,21,Qv→ ┬,0,55,0,55,0,45,0,79,0,75,,0,61,0,72,0,79
,0,5,,0,5,-0,5,0,5,-0,5,0,5,0,5,,0,5,0,5,0,00,0,00,I,1,00,1,00,0,00,1,00,0,50,,0,50,0,50,1,00
,0,4,,0,4,-0,4,0,6,-0,6,0,5,0,5,,0,85,0,67,0,18,0,52,Q┴→V,0,97,0,97,0,03,0,48,0,59,,0,76,0,51,0,48
,0,2,,0,2,-0,2,0,8,-0,8,0,5,0,5,,0,7,0,8,-0,10,0,50,Q┬ → F,1,03,1,00,0,00,0,50,0,45,,0,75,0,50,0,50
,0,6,,0,6,-0,6,0,4,-0,4,0,5,0,5,,0,2,0,3,-0,10,-0,50,┴,1,03,1,00,0,00,0,50,0,45,,0,25,0,50,0,50
"""

# Campos numéricos que iremos conferir
NUM_FIELDS = [
    "mu_p","lam_p","mu","lam","GC","GCT","S1","d","D","GCR","phi","muE","muE_p","muECT","muER","phiE"
]
# Mapear cabeçalhos (com e sem “prime”)
HEADER_MAP = {
    "mu_p": "mu_p", "lam_p": "lam_p",
    "μ’": "mu_p", "λ’": "lam_p",
    "mu": "mu", "lam": "lam", "μ": "mu", "λ": "lam",
    "GC":"GC","GCT":"GCT","S1":"S1","d":"d","D":"D","GCR":"GCR","φ":"phi","phi":"phi",
    "μE":"muE","muE":"muE","μE’":"muE_p","muE_p":"muE_p","μECT":"muECT","muECT":"muECT",
    "μER":"muER","muER":"muER","φE":"phiE","phiE":"phiE",
    "label":"label"
}
# Parâmetros configuráveis do bloco
PARAM_FIELDS = ["FL","FtC","FD","VSSC","VICC","VSSCT","VICCT","VlV","VlF"]

# Tolerância numérica para comparação
TOL = 1e-2


# ====== Helpers ======

def dec(x: str) -> str:
    """Converte decimal brasileiro -> ponto e remove espaços finos."""
    return x.replace('\u202f','').replace(',', '.').strip()

def try_float(s: str) -> Optional[float]:
    s = dec(s)
    if s == "" or s == " ":
        return None
    try:
        return float(s)
    except ValueError:
        return None

def normalize_header(h: str) -> str:
    h = h.strip()
    return HEADER_MAP.get(h, h)

def parse_csv_block(csv_text: str) -> List[Dict[str, Any]]:
    """
    Lê USER_CSV (com vírgula decimal opcional), retorna lista de dicts por linha.
    Só processa colunas conhecidas (PARAM_FIELDS, NUM_FIELDS, 'label').
    """
    # normaliza separadores: substitui ; por , e colchetes/brancos extras
    raw = [ln for ln in csv_text.strip().splitlines() if ln.strip()]
    if not raw:
        return []

    # separa por vírgula; se detectar que a linha tem mais tokens separados por espaço,
    # tenta também split por múltiplos espaços. Aqui vamos usar split por vírgula como base.
    header = [normalize_header(h) for h in [c.strip() for c in raw[0].split(',')]]
    rows = []
    for ln in raw[1:]:
        cols = [c for c in ln.split(',')]
        # se a linha tiver menos colunas que o header, preenche com vazios
        if len(cols) < len(header):
            cols += [""] * (len(header) - len(cols))
        data: Dict[str, Any] = {}
        for name, val in zip(header, cols):
            key = normalize_header(name)
            if key in PARAM_FIELDS:
                f = try_float(val)
                if f is not None:
                    data[key] = f
            elif key in NUM_FIELDS:
                f = try_float(val)
                if f is not None:
                    data[key] = f
            elif key == "label":
                lab = val.strip()
                if lab:
                    data["label"] = lab
            else:
                # ignora demais cabeçalhos
                pass
        # só considera linhas que tenham pelo menos mu e lam definidos
        if "mu" in data and "lam" in data:
            rows.append(data)
    return rows

def compute_row(expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Instancia ParaconsistentBlock com os parâmetros, coloca mu/lam,
    computa e retorna um dict com todos os campos calculados + label.
    """
    # parâmetros (com defaults que batem com sua spec)
    params = {k: expected.get(k, None) for k in PARAM_FIELDS}
    # Limpa None e aplica defaults do bloco (FtCT = FtC se não vier)
    clean = {}
    for k, v in params.items():
        if v is not None:
            clean[k] = v

    blk = ParaconsistentBlock("T")
    if clean:
        blk.set_params(**clean)

    # set das entradas
    blk.set_input(mu=expected["mu"], lam=expected["lam"])
    blk.compute()  # como não estamos em grafo, chamamos compute() direto

    comp = blk.read_port("complete").__dict__
    klass = blk.read_port("classified").__dict__

    # construir saída normalizada
    out: Dict[str, Any] = {
        "mu_p": comp.get("μ’", comp.get("mu_p", None)),
        "lam_p": comp.get("λ’", comp.get("lam_p", None)),
        "mu": comp.get("μ", comp.get("mu", None)),
        "lam": comp.get("λ", comp.get("lam", None)),
        "GC": comp.get("GC", None),
        "GCT": comp.get("GCT", None),
        "S1": comp.get("S1", None),
        "d": comp.get("d", None),
        "D": comp.get("D", None),
        "GCR": comp.get("GCR", None),
        "phi": comp.get("φ", comp.get("phi", None)),
        "muE": comp.get("μE", comp.get("muE", None)),
        "muE_p": comp.get("μE’", comp.get("muE_p", None)),
        "muECT": comp.get("μECT", comp.get("muECT", None)),
        "muER": comp.get("μER", comp.get("muER", None)),
        "phiE": comp.get("φE", comp.get("phiE", None)),
        "label": comp.get("label", None),  # mesmo label também está em classified
        "confidence": klass.get("confidence", None),
    }
    # alguns campos podem não existir dependendo da versão; tenta preencher por fallback
    if out["mu"] is None and "mu" in comp: out["mu"] = comp["mu"]
    if out["lam"] is None and "lam" in comp: out["lam"] = comp["lam"]
    if out["label"] is None and "label" in klass: out["label"] = klass["label"]
    return out

def almost_equal(a: Optional[float], b: Optional[float], tol: float = TOL) -> bool:
    if a is None or b is None:  # se não temos um dos lados, considera como não comparável
        return False
    return abs(a - b) <= tol

def show_result_table(idx: int, expected: Dict[str, Any], got: Dict[str, Any]) -> None:
    # imprime uma mini tabela por linha
    print(f"\n=== Caso #{idx+1} ===")
    # parâmetros relevantes
    pars = ", ".join(f"{k}={expected[k]}" for k in PARAM_FIELDS if k in expected)
    print(f"Params: {pars if pars else '(defaults)'} | Input: mu={expected['mu']}, lam={expected['lam']}")
    # label
    ok_label = (("label" not in expected) or (expected["label"].strip() == str(got.get("label","")).strip()))
    print(f"Label:  exp={expected.get('label','(n/a)')}  got={got.get('label')}  -> {'PASS' if ok_label else 'FAIL'}")
    # campos numéricos
    any_fail = False
    print(f"{'Campo':<8} {'exp':>10} {'got':>10} {'Δ':>10}  OK")
    for f in NUM_FIELDS:
        if f in expected:
            exp = expected[f]
            gotv = got.get(f, None)
            if gotv is None:
                ok = False
                delta = None
            else:
                ok = almost_equal(exp, gotv, TOL)
                delta = None if exp is None or gotv is None else (gotv - exp)
            any_fail = any_fail or (not ok)
            print(f"{f:<8} {exp:>10.4f} {gotv if gotv is not None else float('nan'):>10.4f} {delta if delta is not None else float('nan'):>10.4f}  {'PASS' if ok else 'FAIL'}")
    print("Resultado geral:", "PASS" if (ok_label and not any_fail) else "FAIL")

# ====== MAIN ======
def main():
    rows = parse_csv_block(USER_CSV)
    if not rows:
        print("Nenhuma linha válida encontrada. Verifique o cabeçalho e os valores de mu/lam.")
        return

    total = len(rows)
    pass_count = 0
    for i, row in enumerate(rows):
        got = compute_row(row)

        # checagem de label
        label_ok = ("label" not in row) or (str(row["label"]).strip() == str(got.get("label","")).strip())

        # checagem numérica
        numeric_ok = True
        for f in NUM_FIELDS:
            if f in row:
                if not almost_equal(row[f], got.get(f), TOL):
                    numeric_ok = False
        if label_ok and numeric_ok:
            pass_count += 1

        show_result_table(i, row, got)

    print(f"\n==== Resumo ====")
    print(f"Casos: {total} | PASS: {pass_count} | FAIL: {total - pass_count}")

if __name__ == "__main__":
    main()
