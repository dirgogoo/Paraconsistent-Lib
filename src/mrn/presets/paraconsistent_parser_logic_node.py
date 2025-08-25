from mrn.nodes.logic_node import LogicNode
from mrn.operations.result_each_signal_operation import ResultEachSignalOperation
from mrn.calculations.simple_to_complete_paraconsistent_calculation import SimpleToCompleteParaconsistentCalculation

def ParaconsistentParserLogicNode() -> LogicNode:
    calculator = SimpleToCompleteParaconsistentCalculation(nd=6, clamp=True)
    operation = ResultEachSignalOperation(calculator)
    return LogicNode(None, operation=operation)