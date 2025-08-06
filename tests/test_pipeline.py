import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from mrn.builders.input_node_builder import InputNodeBuilder
from mrn.core.network_manager import Network_Manager
from mrn.presets.paraconsistent_parser_logic_node import ParaconsistentParserLogicNode
from mrn.presets.paraconsistent_classifier_output_node import ParaconsistentClassifierOutputNode
from mrn.signals.simple_paraconsistent_signal import SimpleParaconsistentSignal
from mrn.builders.output_node_builder import OutputNodeBuilder
from mrn.operations.identity_operation import IdentityOperation


def test_network_manager_paraconsistent_pipeline():
    input_node = InputNodeBuilder().set_id("input1").build()
    parser_node = ParaconsistentParserLogicNode("parser1")
    classifier_node = OutputNodeBuilder().set_operation(IdentityOperation()).set_id("identity1").build()

    network = Network_Manager()
    network.add_node(input_node)
    network.add_node(parser_node)
    network.add_node(classifier_node)

    network.connect("input1", "parser1")
    network.connect("parser1", "identity1")

    signal = SimpleParaconsistentSignal(mu=0.9, lam=0.1)
    input_node.receive(signal)

    # 4. Propagar a rede
    network.propagate_all()

    # 5. Obter a saída final
    outputs = network.get_outputs("identity1")

    # 6. Testar e exibir resultado
    assert len(outputs) == 1
    print("Sinal de saída final:", outputs[0].to_dict())

