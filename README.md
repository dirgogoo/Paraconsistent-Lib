# MRN — Modular Reasoning Network

Biblioteca Python modular para criação, execução e gerenciamento de redes de raciocínio lógico.

## Sobre

O MRN é uma biblioteca modular projetada para construir redes de raciocínio lógico, com foco inicial na lógica paraconsistente — que lida com informações contraditórias e incertas. A arquitetura flexível permite a extensão para suportar múltiplos sistemas lógicos no futuro, como lógica fuzzy, probabilística e outras.

## Funcionalidades principais

- Modelagem de nodos de rede lógicos com diferentes perfis (entrada, lógica, classificação).
- Implementação de operações lógicas usando o padrão Strategy.
- Builder para facilitar a criação e configuração de nodos e redes.
- Suporte a múltiplas estratégias de propagação e sincronização.
- Estrutura modular que facilita extensão, manutenção e integração.

## Como usar

Clone o repositório e instale as dependências via Poetry:

```bash
git clone https://github.com/seu-usuario/mrn.git
cd mrn
poetry install
