# 🔷 MRN - Modular Reasoning Network

**MRN** é uma biblioteca Python modular e extensível para a construção de **redes lógicas customizáveis**, com suporte a diferentes paradigmas lógicos — como lógica paraconsistente, fuzzy, booleana e outras.

Projetado com foco em **modularidade, liberdade de modelagem e clareza arquitetural**, o MRN permite criar nós lógicos, definir conexões, estratégias de inferência e operar com diferentes tipos de sinais lógicos de forma transparente e intuitiva.

---

## ✨ Diferenciais

MRN **não é um sistema lógico pronto**, mas sim uma ferramenta de desenvolvimento para **construção de redes lógicas** personalizadas:

- 🧱 **Abordagem modular**: você constrói blocos lógicos com builders, presets e padrões como Strategy e Bridge.
- 🌐 **Lógica multivalorada e flexível**: suporte nativo à lógica paraconsistente e arquitetura aberta para outras lógicas.
- 🧠 **Voltado ao raciocínio simbólico**, não à síntese de hardware.
- 🛠️ **Framework leve**, direto ao ponto, sem dependência de compiladores C++ ou bibliotecas externas pesadas.
- 🎓 Ideal para **pesquisadores, educadores, entusiastas de IA simbólica e lógica computacional**.

---

## 📦 Estrutura do Projeto

```text
mrn/
├── mrn/                     # Código-fonte principal
│   ├── core/               # Interfaces, ISignal, ICalculation
│   ├── nodes/              # InputNode, LogicNode, ClassifierNode
│   ├── builders/           # Builders de cada tipo de nó
│   ├── operations/         # Operações (IOperation e implementações)
│   ├── presets/            # Configurações prontas
│   └── __init__.py
├── tests/                  # Testes unitários
├── examples/               # Exemplos de uso
├── pyproject.toml          # Configuração do projeto
├── README.md               # Esta documentação
└── LICENSE
```

---

## 🚀 Começando

Instale as dependências com:

```bash
poetry install
```

E ative o ambiente com:

```bash
poetry shell
```

---

## 🧪 Exemplos

Veja a pasta `examples/` para entender como construir uma rede lógica do zero, usando:

- Builders para criar nós lógicos  
- Estratégias de propagação  
- Operações customizadas  
- Lógica paraconsistente com cálculos automáticos  

---

## 📚 Inspirações e Comparações

Embora existam frameworks de lógica como:

- [`aigverse`](https://github.com/marcelwa/aigverse) — síntese lógica em IA  
- [`LogicNG`](https://logicng.org/)  
- [`OpenCog`](https://opencog.org/)  

O **MRN** é único por ser:

- ✅ Simples e modular  
- ✅ Multilógico desde a base  
- ✅ Voltado ao desenvolvimento de soluções, não à entrega de uma só  

---

## 🧠 Idealizado para

- Desenvolvedores que desejam criar seus próprios raciocinadores  
- Pesquisadores em lógicas não clássicas  
- Estudantes que querem aprender lógica aplicada de forma prática  
- Projetos educacionais, experimentais ou de IA simbólica  

---

## 📄 Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

---

## 💬 Contribua

Contribuições, ideias e sugestões são bem-vindas! Abra uma issue ou envie um pull request.

