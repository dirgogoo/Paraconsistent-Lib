from mrn.nodes.output_node import OutputNode
from mrn.operations.result_each_signal_operation import ResultEachSignalOperation
from mrn.calculations.threshold_classifier_calculation import ThresholdClassifierCalculation

def ParaconsistentClassifierOutputNode(threshold: float = 0.3) -> OutputNode:
    calc = ThresholdClassifierCalculation(threshold)
    operation = ResultEachSignalOperation(calc)
    return OutputNode(None, operation=operation)