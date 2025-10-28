1. Introdução

Paraconsistent Lib é uma biblioteca Python para construir redes de raciocínio lógico modulares. Ela te ajuda a modelar, testar e orquestrar blocos lógicos (começando pela lógica paraconsistente) sem dor de cabeça com infraestrutura, sem grafo e sem DSL, e sem cálculos de baixo nível. Você trabalha com blocos e expressões Python diretas para conectar entradas e saídas; o Paraconsistent Lib cuida do resto (cálculos, propagação local, cache e inspeção dos resultados), permitindo composições modulares e reprodutíveis. Foi criada para substituir processos manuais e suscetíveis a erro por fluxos claros e verificáveis, úteis para pesquisadores e entusiastas da lógica paraconsistente.

2. Requisitos e Instalação

Item: Requisito
Linguagem: Python 3.9+
Dependências: Biblioteca padrão
Instalação: pip install paraconsistent
Organização: core/{metrics,config,types,engine} e paraconsistent/block

3. Guia

A ideia central do Paraconsistent Lib é que cada bloco representa uma unidade de raciocínio. No caso da lógica paraconsistente, cada bloco calcula os parâmetros principais (μ, λ, GC, GCT etc.), aplica classificações nas 12 regiões de decisão (V, F, ┬, ┴, Q┬→V, QF→┴…) e expõe saídas que podem ser ligadas a outros blocos.

3.1 Criando um Bloco

O primeiro passo para a criação do seu programa paraconsistente começa com o setup dos blocos. Basicamente, para criar o bloco, você deve importar e instanciar a classe ParaconsistentBlock.

from paraconsistent.blocks import ParaconsistentBlock
# 1) Criar o bloco
b = ParaconsistentBlock()


3.2 Configurando um Bloco

Em seguida, você deve configurar os parâmetros do bloco. Ele vem com valores padrão caso não queira alterar. A definição dessas configurações segue o padrão (<objeto do bloco>).config.<parâmetro>. Todas as configurações disponíveis estão na seção 5. API do Bloco.

from paraconsistent.blocks import ParaconsistentBlock
# 1) Criar o bloco
b = ParaconsistentBlock()
# 2) Ajustar parâmetros
b.config.FtC = 0.70  # Certainty Control Limit (CCL)


3.3 Executando um Bloco

Agora precisamos definir os valores de entrada do nosso bloco, no caso λ (lam) e μ (mu), em tempo de execução. Para isso, basta usar (<objeto do bloco>).input.<parâmetro> (o parâmetro pode ser lam ou mu). Mais informações na seção 5. API do Bloco.





from paraconsistent.blocks import ParaconsistentBlock
# 1) Criar o bloco
b = ParaconsistentBlock()
# 2) Ajustar parâmetros
b.config.FtC = 0.70  # Certainty Control Limit (CCL)
# 3) Definir entradas
b.input.mu  = 0.20
b.input.lam = 0.40


Por fim, como a execução é em tempo real, o modelo computa ao definir valores. Você pode obter os valores por (<objeto do bloco>).complete.<parâmetro> individualmente ou obter tudo com print_complete(), que é o que faremos. Todos os parâmetros disponíveis estão na seção 5. API do Bloco.

from paraconsistent.blocks import ParaconsistentBlock

# 1) Criar o bloco
b = ParaconsistentBlock()

# 2) Ajustar parâmetros
b.config.FtC = 0.70  # Certainty Control Limit (CCL)

# 3) Definir entradas
b.input.mu  = 0.20
b.input.lam = 0.40

# 4) Imprimir no console
b.print_complete()


3.4 Conectando Múltiplos Blocos

Vimos até aqui como criar blocos; porém, um bloco sozinho não faz muita coisa. Agora veremos como conectar blocos para formar uma estrutura mais complexa. Para demonstrar, criaremos o Bloco 1 (B1) e o Bloco 2 (B2), seguindo os passos de criação, configuração (preferencialmente) e alimentação de um dos blocos, no caso o B1.

from paraconsistent.blocks import ParaconsistentBlock

b1 = ParaconsistentBlock()
b2 = ParaconsistentBlock()

# Aqui escolho configurar apenas o bloco b1; no b2 uso as configs padrão
b1.config.FtC = 0.70  # Certainty Control Limit (CCL)

b1.input.lam = 0.1
b1.input.mu  = 0.2


Agora, para conectar os blocos entre si, basta utilizar diretamente os parâmetros de entrada, como mostrado na seção 3.3 Executando um Bloco. Você pode usar cálculos ou apenas o valor da saída de outro bloco, conforme a demonstração:

from paraconsistent.blocks import ParaconsistentBlock

b1 = ParaconsistentBlock()
b2 = ParaconsistentBlock()

# Aqui escolho configurar apenas o bloco b1; no b2 uso as configs padrão
b1.config.FtC = 0.70  # Certainty Control Limit (CCL)

b1.input.lam = 0.1
b1.input.mu  = 0.2

# Importante: o valor de entrada precisa existir antes.
# Se eu colocasse a linha b1.input.mu = 0.2 depois da conexão, daria erro.

# Implementando tanto o caso de cálculo quanto de conexão direta
b2.input.lam = b1.complete.gc            # Conexão direta
b2.input.mu  = (b1.input.lam - 1) / 4    # Conexão com cálculo


5. API do Bloco

5.1 Criação

ParaconsistentBlock(*, mu: float | None = None, lam: float | None = None, **param_overrides)

- mu, lam: valores iniciais (clamp em [0,1]).
- param_overrides: qualquer parâmetro listado em §6 (validação com warnings e truncamentos quando necessário).

5.2 Entradas

b.input.mu = 0.73
b.input.lam = 0.10
# ou
b.input(mu=0.73, lam=0.10)


Toda alteração invalida o cache e força recomputar na próxima leitura de b.complete.

5.3 Parâmetros

b.config.FtC = 0.70  # Certainty Control Limit (CCL)
b.config.VlV = 0.50  # Viés pró-verdadeiro
b.config.VlF = 0.50  # Viés pró-falso

# ou, em lote
b.set_params(FtC=0.7, VlV=0.5, VlF=0.5)

# Nota: VSSC, VICC, VSSCT, VICCT são calculados automaticamente baseados em FtC


Campos e faixas em §6. Valores fora da faixa são truncados com aviso.

5.4 Saídas

- b.complete: SimpleNamespace com todos os campos (ver §7).
- b.to_dict(): retorna um dict tipado (Complete) com os mesmos campos.
- b.print_complete(): imprime todos os campos formatados.

6. Parâmetros (config)

Parâmetro | Faixa esperada | Padrão | Descrição resumida
FtC       | [0,1]          | 0.50   | Certainty Control Limit (CCL) - controla limites de certeza e contradição.
VlV       | [0,1]          | 0.50   | Viés pró-Verdadeiro (puxa GC para +).
VlF       | [0,1]          | 0.50   | Viés pró-Falso (puxa GC para −).
L         | [0,1]          | 0.05   | Piso mínimo usado em algumas estratégias (reserva futura).

**Nota importante:** VSSC, VICC, VSSCT e VICCT são calculados automaticamente pelo engine baseados em FtC, seguindo a lógica do MATLAB:
- VSSC = FtC
- VICC = -FtC
- VSSCT = 1 - FtC
- VICCT = FtC - 1

Validação: se um valor sair da faixa, ele é clampado e um RuntimeWarning é emitido.

7. Campos de complete

Retornados por b.complete (como atributos) e por b.to_dict() (como chaves do dict tipado Complete).

Campo | Descrição
mu, lam | Entradas (clampadas em [0,1]).
gc | Grau de Certeza (μ − λ). Intervalo ~ [-1,1]. Equivalente a DC no MATLAB.
gct | Grau de Contradição (μ + λ − 1). Intervalo ~ [-1,1]. Equivalente a DCT no MATLAB.
d, D | Métrica geométrica de distância a vértices (ver metrics.radial_d_to_nearest_apex).
gcr | Grau de Certeza Radial: (1 − D) * sign(gc). Equivalente a DCR no MATLAB.
phi, phiE | Intervalo de certeza: 1 − |gct|. Equivalente a Phi no MATLAB.
muE | Resulting Evidence Degree: (gc + 1) / 2. Equivalente a MIE no MATLAB.
muECT | Resulting Contradiction Degree: (gct + 1) / 2. Equivalente a MIEct no MATLAB.
muER | **Resulting Real Evidence Degree: (gcr + 1) / 2. Equivalente a MIER no MATLAB.**
decision_output | **Saída de decisão:** 1.0 se muER > FtC, 0.0 se muER < FtC, 0.5 se muER == FtC.
label | Rótulo da região lógica (V, F, ┬, ┴, Q┬→V, QF→┴, etc).
Regions | Dicionário de flags booleanas por região para uso em sistemas especialistas.
Parâmetros (FtC, VlV, VlF, L) | Eco dos valores em uso no momento do cálculo para reprodutibilidade.

8. Exemplos práticos

8.1 (reservado para exemplos adicionais)

10. Licença

MIT

