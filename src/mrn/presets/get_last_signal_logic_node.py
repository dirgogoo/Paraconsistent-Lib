from __future__ import annotations
from mrn.nodes.logic_node import LogicNode
from mrn.operations.get_last_signal_operation import GetLastSignalOperation

def GetLastSignalLogicNode() -> LogicNode:
    """
    LogicNode pronto com a operação GetLastOperation.
    Uso:
        n_getlast = GetLastLogicNode()
        network.add_node(n_getlast)
        network.connect(upstream, n_getlast)
        network.connect(n_getlast, downstream)
    """
    return LogicNode(node_id=None, operation=GetLastSignalOperation())
