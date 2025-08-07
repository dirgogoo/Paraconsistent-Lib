from mrn.nodes.logic_node import LogicNode
from mrn.operations.unique_result_all_signal_operation import UniqueResultAllSignalOperation
from mrn.calculations.average_aggregation_simple_paraconsistent_calculation import AggregationSimpleParaconsistentCalculation

def ParaconsistentAggregatorLogicNode() -> LogicNode:
    calculator = AggregationSimpleParaconsistentCalculation()
    operation = UniqueResultAllSignalOperation(calculator)
    return LogicNode(None, operation=operation)