from __future__ import annotations
from mrn.operations.result_each_signal_operation import ResultEachSignalOperation
from mrn.calculations.paraconsistent_classifier_calculation import ParaconsistentClassifierCalculation
from mrn.nodes.output_node import OutputNode

def ParaconsistentClassifierOutputNode(
    tC: float = 0.30, tCT: float = 0.30, tD: float = 0.20, L: float = 0.05, nd: int = 6
) -> OutputNode:
    calc = ParaconsistentClassifierCalculation(tC=tC, tCT=tCT, tD=tD, L=L, nd=nd)
    op = ResultEachSignalOperation(calc)
    return OutputNode(node_id=None, operation=op)
