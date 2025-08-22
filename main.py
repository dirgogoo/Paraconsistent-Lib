from src.mrn.operations.none_operation import NoneOperation
from src.mrn.builders.output_node_builder import OutputNodeBuilder
from src.mrn.presets.paraconsistent_aggregator_logic_node import ParaconsistentAggregatorLogicNode
from src.mrn.builders.input_node_builder import InputNodeBuilder
from src.mrn.core.network_manager import Network_Manager
from src.mrn.presets.paraconsistent_parser_logic_node import ParaconsistentParserLogicNode
from src.mrn.presets.paraconsistent_classifier_output_node import ParaconsistentClassifierOutputNode
from src.mrn.signals.simple_paraconsistent_signal import SimpleParaconsistentSignal

def exemplo1():
    # Criar os nós
    input_node = InputNodeBuilder().build()

    #ambos presets
    parser_node = ParaconsistentParserLogicNode()
    #forma manual:
    #parse_node = LogicNodeBuilder().set_operation(ResultEachSignalOperation(SimpleToCompleteParaconsistentCalculation())).build()
    classifier_node = ParaconsistentClassifierOutputNode()
    #classifier_node = OutputNodeBuilder().set_operation(ResultEachSignalOperation(ThresholdClassifierCalculation(0.3)))).build()

    # Criar e configurar a rede
    network = Network_Manager()
    network.add_node(input_node)
    network.add_node(parser_node)
    network.add_node(classifier_node)

    network.connect(input_node, parser_node)
    network.connect(parser_node, classifier_node)

    # Inserir sinal de entrada
    signal = SimpleParaconsistentSignal(mu=0.9, lam=0.1, source_id="sensorX")
    input_node.receive(signal)

    # Executar a rede
    network.propagate_all()

    # Obter resultado
    outputs = network.get_outputs(classifier_node)

    print("\n📤 Sinal de saída final:")
    for s in outputs:
        print(s.to_dict())

    #RESULTADO: {'type': 'paraconsistent', 'mu': 0.7, 'lambda': 0.2, 'source': 'aggregated', 'certainty': 0.49999999999999994}

def exemplo2():
     # Criar os nós
     #Construção com builder é manual diferente dos presets
    input_node = InputNodeBuilder().build()
    input_node2 = InputNodeBuilder().build()

    #Isso é um preset de um node que equivale o mesmo que: -->
    #
    #calculator = AggregationSimpleParaconsistentCalculation()
    #operation = UniqueResultAllSignalOperation(calculator)
    #return LogicNode(None, operation=operation)
    #
    aggregator_node = ParaconsistentAggregatorLogicNode()

    #modo manual ficaria: 
    #aggregator_node = LogicNodeBuilder().set_operation(UniqueResultAllSignalOperation(AggregationSimpleParaconsistentCalculation())).build()

    output_node = OutputNodeBuilder().set_operation(NoneOperation()).build()

    network = Network_Manager()
    network.add_node(input_node)
    network.add_node(input_node2)
    network.add_node(aggregator_node)
    network.add_node(output_node)

    network.connect(input_node,aggregator_node)
    network.connect(input_node2,aggregator_node)
    network.connect(aggregator_node,output_node)

    signal = SimpleParaconsistentSignal(mu=0.9, lam=0.1)
    signal2 = SimpleParaconsistentSignal(mu=0.5, lam=0.3)

    input_node.receive(signal)
    input_node2.receive(signal2)

    network.propagate_all()

    # Obter resultado
    outputs = network.get_outputs(output_node)

    print("\n📤 Sinal de saída final:")
    for s in outputs:
        print(s.to_dict())

    #RESULTADO: {'type': 'paraconsistent', 'mu': 0.7, 'lambda': 0.2, 'source': 'aggregated', 'certainty': 0.49999999999999994}

def main():
   exemplo1()








if __name__ == "__main__":
    main()