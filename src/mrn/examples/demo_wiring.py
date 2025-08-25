from mrn.core.network_manager import Network_Manager
from mrn.blocks.paraconsistent_block import ParaconsistentBlock

def main():

    net = Network_Manager()
    b1 = ParaconsistentBlock(block_id="B1", network=net, initial_mu=0.9, initial_lam=0.1
                            ,tC=0.35, tCT=0.40, tD=0.25, L=0.07) # bloco 1 - esses são os limiares do classificador (padrão: 0.30, 0.30, 0.20, 0.05)
    b2 = ParaconsistentBlock(block_id="B2", network=net)

    # Conectando blocos
    # DSL: b1.complete.mu >> b2.input.lam
    b1.complete.mu >> b2.input.lam
    # Fórmula inline: (gc - 0.2) >> mu
    (b1.complete.gc - 0.2)*0.2/0.2 >> b2.input.mu

    net.propagate_all() # processa tudo e propaga os sinais

    print("B1 complete:", b1.get_complete())
    print("B1 classified:", b1.get_classified())

    # Outputs printados:
    #B1 complete: [{'type': 'paraconsistent_complete', 'mu': 0.9, 'lambda': 0.1, 'gc': 0.8, 'gct': 0.0, 'gcr': 0.8, 'mer': 0.9, 'phie': 1.0, 'certainty': 0.8}]
    #B1 classified: [{'type': 'paraconsistent_output', 'label': 'V', 'confidence': 0.45}]

    print("B2 complete:", b2.get_complete())
    print("B2 classified:", b2.get_classified())

    # Outputs printados:
    #B2 complete: [{'type': 'paraconsistent_complete', 'mu': 0.6, 'lambda': 0.1, 'gc': 0.5, 'gct': -0.3, 'gcr': 0.416905, 'mer': 0.708452, 'phie': 0.7, 'certainty': 0.5}]
    #B2 classified: [{'type': 'paraconsistent_output', 'label': 'C', 'confidence': 0.0}]

if __name__ == "__main__":
    main()
