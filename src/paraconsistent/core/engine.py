from __future__ import annotations
from types import SimpleNamespace
from typing import Dict, Tuple


from paraconsistent.core.metrics import clamp01, radial_d_to_nearest_apex
from paraconsistent.core.config import BlockParams
from paraconsistent.core.types import Complete


__all__ = ["ParaconsistentEngine"]


class ParaconsistentEngine:


    @staticmethod
    def preprocess_inputs(mu: float, lam: float, P: BlockParams) -> Tuple[float, float, float, float]:
        mu = clamp01(mu)
        lam = clamp01(lam)
        mu_p = clamp01(mu / P.FL if P.FL != 0 else mu)
        lam_p = clamp01(lam / P.FL if P.FL != 0 else lam)
        return mu, lam, mu_p, lam_p


    @staticmethod
    def core_degrees(mu: float, lam: float) -> Tuple[float, float]:
        gc = mu - lam
        gct = mu + lam - 1.0
        return gc, gct


    @staticmethod
    def adjust_contradiction(gct: float, P: BlockParams) -> float:
        return max(-1.0, min(1.0, gct + P.FL * (P.VSSCT + P.VICCT) * 0.5))


    @staticmethod
    def geometry(mu: float, lam: float, gc: float) -> Tuple[float, float, float]:
        d = radial_d_to_nearest_apex(mu, lam)
        D = d
        gcr = (1.0 - D) * (1.0 if gc >= 0 else -1.0)
        return d, D, gcr


    @staticmethod
    def evidences(mu_p: float, lam_p: float, gc: float, gct: float, gcr: float) -> Dict[str, float]:
        phi = 1.0 - abs(gct)
        muE = (gc + 1.0) / 2.0
        muECT = (gct + 1.0) / 2.0
        muER = (gcr + 1.0) / 2.0
        muE_p = ((mu_p - lam_p) + 1.0) / 2.0
        phiE = phi
        return {"phi": phi, "muE": muE, "muECT": muECT, "muER": muER, "muE_p": muE_p, "phiE": phiE}


    @classmethod
    def compute(cls, *, mu: float, lam: float, params: BlockParams) -> SimpleNamespace:
        mu, lam, mu_p, lam_p = cls.preprocess_inputs(mu, lam, params)
        gc, gct = cls.core_degrees(mu, lam)
        gct_adj = cls.adjust_contradiction(gct, params)
        d, D, gcr = cls.geometry(mu, lam, gc)
        ev = cls.evidences(mu_p, lam_p, gc, gct, gcr)
        complete: Complete = {
            # parâmetros
            "FL": params.FL, "FtC": params.FtC, "FD": params.FD,
            "VSSC": params.VSSC, "VICC": params.VICC, "VSSCT": params.VSSCT, "VICCT": params.VICCT,
            "VlV": params.VlV, "VlF": params.VlF, "L": params.L,
            # entradas
            "mu": mu, "lam": lam, "mu_p": mu_p, "lam_p": lam_p,
            # graus / derivados
            "gc": gc, "gct": gct, "gct_adj": gct_adj,
            "d": d, "D": D, "gcr": gcr,
            # evidências
            **ev,
        }
        return SimpleNamespace(**complete)