from mrn.nodes.logic_node import LogicNode
from mrn.operations.paraconsistent_parser_operation import ParaconsistentParserOperation
from mrn.calculations.paraconsistent_signal_parser_calculation import ParaconsistentSignalParser

def ParaconsistentParserLogicNode(node_id: str = "parser") -> LogicNode:
    calculator = ParaconsistentSignalParser()
    operation = ParaconsistentParserOperation(calculator)
    return LogicNode(node_id=node_id, operation=operation)