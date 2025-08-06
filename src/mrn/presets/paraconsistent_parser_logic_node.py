from mrn.nodes.logic_node import LogicNode
from mrn.operations.calculate_each_signal_operation import CalculateEachSignalOperation
from mrn.calculations.paraconsistent_signal_parser_calculation import ParaconsistentSignalParser

def ParaconsistentParserLogicNode(node_id: str = "parser") -> LogicNode:
    calculator = ParaconsistentSignalParser()
    operation = CalculateEachSignalOperation(calculator)
    return LogicNode(node_id=node_id, operation=operation)