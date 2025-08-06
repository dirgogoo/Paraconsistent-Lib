from mrn.nodes.output_node import OutputNode
from mrn.operations.classifier_operation import ClassifierOperation
from mrn.calculations.threshold_classifier_calculation import ThresholdClassifierCalculation

def ParaconsistentClassifierOutputNode(node_id: str = "classifier", threshold: float = 0.3) -> OutputNode:
    calc = ThresholdClassifierCalculation(threshold)
    operation = ClassifierOperation(calc)
    return OutputNode(node_id=node_id, operation=operation)