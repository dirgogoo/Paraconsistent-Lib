# mrn/examples/demo.py
from mrn.core.graph import BlockGraph
from mrn.paraconsistent.block import ParaconsistentBlock

def main():
    g = BlockGraph()
    b1 = ParaconsistentBlock("B1")

    g.add_block(b1)

    # entradas no início da rede
    b1.input.mu = 0.5  # ou: b1.input.mu = 0.6 ; b1.input.lam = 0.2
    b1.input.lam = 0.5

    b1.config.FtC = 0.5
    b1.config.VSSC = 0.5
    b1.config.VICC = -0.5
    b1.config.VSSCT = 0.5
    b1.config.VICCT = -0.5
    b1.config.VlV = 0.5
    b1.config.VlF = 0.5


    g.run()
    print(b1.read_port("complete").__dict__)
    print(b1.read_port("classified").__dict__)




if __name__ == "__main__":
    main()
