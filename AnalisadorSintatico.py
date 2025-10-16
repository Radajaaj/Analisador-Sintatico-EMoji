# Analisador Sintático E-moji
# Alunos: Fernando Seiji Onoda Inomata, Lucas Batista Deinzer Duarte, Vitor Mayorca Camargo

import sys
import os

"""
Este módulo implementa um Analisador Sintático (Parser) Top-Down Tabular
para a linguagem de programação E-moji. Ele utiliza uma tabela de análise
preditiva para validar a estrutura gramatical de uma sequência de tokens
e gerar uma Árvore Sintática (Parse Tree) como saída.
"""

# --- ESTRUTURAS DE DADOS DA ÁRVORE ---

class TreeNode:
    """
    Representa um nó na Árvore Sintática. Cada nó contém um valor (um símbolo
    terminal ou não-terminal) e uma lista de nós filhos.
    """
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, node):
        """Adiciona um nó à lista de filhos."""
        # Inserimos no início para que, ao imprimir, a ordem fique igual à da regra
        self.children.insert(0, node)

def print_tree(node, prefix="", is_last=True):
    """
    Função recursiva para imprimir a Árvore Sintática de forma legível no terminal.
    """
    print(prefix + ("└── " if is_last else "├── ") + str(node.value))
    children_count = len(node.children)
    # Percorre a lista de filhos na ordem inversa para imprimir corretamente
    for i, child in enumerate(reversed(node.children)):
        is_child_last = (i == children_count - 1)
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(child, new_prefix, is_child_last)

# --- TABELA DE ANÁLISE PREDITIVA (PARSING TABLE M) ---

# A tabela preditiva (M) define as ações do parser.
# As chaves são os não-terminais e os valores são dicionários
# mapeando tokens de entrada para a produção a ser aplicada.
tabela_preditiva = {
    'PROGRAMA': {
        'INT': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'STRING_TYPE': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'BOOL': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'],
        'ID': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'IF': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'WHILE': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'FOR': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'],
        'COMANDO_SAIDA': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'COMANDO_ENTRADA': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], '$': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS']
    },
    'LISTA_DECLARACOES': {
        'INT': ['DECLARACAO_VAR', 'LISTA_DECLARACOES'], 'STRING_TYPE': ['DECLARACAO_VAR', 'LISTA_DECLARACOES'], 'BOOL': ['DECLARACAO_VAR', 'LISTA_DECLARACOES'],
        'ID': ['epsilon'], 'IF': ['epsilon'], 'WHILE': ['epsilon'], 'FOR': ['epsilon'], 'COMANDO_SAIDA': ['epsilon'], 'COMANDO_ENTRADA': ['epsilon'], '$': ['epsilon']
    },
    'DECLARACAO_VAR': {
        'INT': ['TIPO', 'ID', 'PONTO_VIRGULA'], 'STRING_TYPE': ['TIPO', 'ID', 'PONTO_VIRGULA'], 'BOOL': ['TIPO', 'ID', 'PONTO_VIRGULA']
    },
    'TIPO': {
        'INT': ['INT'], 'STRING_TYPE': ['STRING_TYPE'], 'BOOL': ['BOOL']
    },
    'BLOCO_COMANDOS': {
        'ID': ['COMANDO', 'BLOCO_COMANDOS_'], 'IF': ['COMANDO', 'BLOCO_COMANDOS_'], 'WHILE': ['COMANDO', 'BLOCO_COMANDOS_'], 'FOR': ['COMANDO', 'BLOCO_COMANDOS_'],
        'COMANDO_SAIDA': ['COMANDO', 'BLOCO_COMANDOS_'], 'COMANDO_ENTRADA': ['COMANDO', 'BLOCO_COMANDOS_'], 'FECHAR_BLOCO': ['epsilon'], '$': ['epsilon']
    },
    'BLOCO_COMANDOS_': {
        'ID': ['COMANDO', 'BLOCO_COMANDOS_'], 'IF': ['COMANDO', 'BLOCO_COMANDOS_'], 'WHILE': ['COMANDO', 'BLOCO_COMANDOS_'], 'FOR': ['COMANDO', 'BLOCO_COMANDOS_'],
        'COMANDO_SAIDA': ['COMANDO', 'BLOCO_COMANDOS_'], 'COMANDO_ENTRADA': ['COMANDO', 'BLOCO_COMANDOS_'], 'FECHAR_BLOCO': ['epsilon'], '$': ['epsilon']
    },
    'COMANDO': {
        'ID': ['ATRIBUICAO'], 'IF': ['ESTRUTURA_IF'], 'WHILE': ['ESTRUTURA_WHILE'], 'FOR': ['ESTRUTURA_FOR'],
        'COMANDO_SAIDA': ['COMANDO_SAIDA', 'ABRIR_PARENTESES', 'EXPRESSAO', 'FECHAR_PARENTESES', 'PONTO_VIRGULA'],
        'COMANDO_ENTRADA': ['COMANDO_ENTRADA', 'ABRIR_PARENTESES', 'ID', 'FECHAR_PARENTESES', 'PONTO_VIRGULA']
    },
    'ATRIBUICAO': {
        'ID': ['ID', 'ATRIBUICAO', 'EXPRESSAO', 'PONTO_VIRGULA']
    },
    'ATRIBUICAO_FOR': {
        'ID': ['ID', 'ATRIBUICAO', 'EXPRESSAO']
    },
    'ESTRUTURA_IF': {
        'IF': ['IF', 'ABRIR_PARENTESES', 'EXPRESSAO', 'FECHAR_PARENTESES', 'ABRIR_BLOCO', 'BLOCO_COMANDOS', 'FECHAR_BLOCO', 'ELSE_PARTE']
    },
    'ESTRUTURA_WHILE': {
        'WHILE': ['WHILE', 'ABRIR_PARENTESES', 'EXPRESSAO', 'FECHAR_PARENTESES', 'ABRIR_BLOCO', 'BLOCO_COMANDOS', 'FECHAR_BLOCO']
    },
    'ESTRUTURA_FOR': {
        'FOR': ['FOR', 'ABRIR_PARENTESES', 'ATRIBUICAO_FOR', 'PONTO_VIRGULA', 'EXPRESSAO', 'PONTO_VIRGULA', 'ATRIBUICAO_FOR', 'FECHAR_PARENTESES', 'ABRIR_BLOCO', 'BLOCO_COMANDOS', 'FECHAR_BLOCO']
    },
    'ELSE_PARTE': {
        'ELSE': ['ELSE', 'ABRIR_BLOCO', 'BLOCO_COMANDOS', 'FECHAR_BLOCO'],
        'ID': ['epsilon'], 'IF': ['epsilon'], 'WHILE': ['epsilon'], 'FOR': ['epsilon'], 'COMANDO_SAIDA': ['epsilon'], 'COMANDO_ENTRADA': ['epsilon'], 'FECHAR_BLOCO': ['epsilon'], '$': ['epsilon']
    },
    'EXPRESSAO': {
        'ABRIR_PARENTESES': ['TERMO', 'EXPRESSAO_'], 'ID': ['TERMO', 'EXPRESSAO_'], 'NUMERO_INT': ['TERMO', 'EXPRESSAO_'], 'STRING_LITERAL': ['TERMO', 'EXPRESSAO_'], 'TRUE': ['TERMO', 'EXPRESSAO_'], 'FALSE': ['TERMO', 'EXPRESSAO_']
    },
    'EXPRESSAO_': {
        'OP_SOMA': ['OP_SOMA', 'TERMO', 'EXPRESSAO_'], 'OP_SUB': ['OP_SUB', 'TERMO', 'EXPRESSAO_'],
        'OP_MAIOR': ['OP_MAIOR', 'TERMO', 'EXPRESSAO_'], 'OP_MENOR': ['OP_MENOR', 'TERMO', 'EXPRESSAO_'],
        'OP_IGUAL_COMP': ['OP_IGUAL_COMP', 'TERMO', 'EXPRESSAO_'], 'OP_AND': ['OP_AND', 'TERMO', 'EXPRESSAO_'],
        'OP_OR': ['OP_OR', 'TERMO', 'EXPRESSAO_'], 'OP_IGUAL_LOGICO': ['OP_IGUAL_LOGICO', 'TERMO', 'EXPRESSAO_'],
        'FECHAR_PARENTESES': ['epsilon'], 'PONTO_VIRGULA': ['epsilon']
    },
    'TERMO': {
        'ABRIR_PARENTESES': ['FATOR', 'TERMO_'], 'ID': ['FATOR', 'TERMO_'], 'NUMERO_INT': ['FATOR', 'TERMO_'], 'STRING_LITERAL': ['FATOR', 'TERMO_'], 'TRUE': ['FATOR', 'TERMO_'], 'FALSE': ['FATOR', 'TERMO_']
    },
    'TERMO_': {
        'OP_MULT': ['OP_MULT', 'FATOR', 'TERMO_'], 'OP_DIV': ['OP_DIV', 'FATOR', 'TERMO_'],
        'OP_SOMA': ['epsilon'], 'OP_SUB': ['epsilon'], 'FECHAR_PARENTESES': ['epsilon'], 'PONTO_VIRGULA': ['epsilon'],
        'OP_MAIOR': ['epsilon'], 'OP_MENOR': ['epsilon'], 'OP_IGUAL_COMP': ['epsilon'], 'OP_AND': ['epsilon'], 'OP_OR': ['epsilon'], 'OP_IGUAL_LOGICO': ['epsilon']
    },
    'FATOR': {
        'ABRIR_PARENTESES': ['ABRIR_PARENTESES', 'EXPRESSAO', 'FECHAR_PARENTESES'], 'ID': ['ID'], 'NUMERO_INT': ['NUMERO_INT'], 'STRING_LITERAL': ['STRING_LITERAL'], 'TRUE': ['VALOR_BOOL'], 'FALSE': ['VALOR_BOOL']
    },
    'VALOR_BOOL': {
        'TRUE': ['TRUE'], 'FALSE': ['FALSE']
    }
}

# --- FUNÇÕES DO ANALISADOR ---

def erro(token_esperado, token_recebido):
    """
    Função chamada quando um erro sintático é encontrado.
    Imprime uma mensagem de erro formatada e encerra a execução.
    """
    if token_recebido and token_recebido.get('linha'):
        print(f"Erro Sintático: Esperado um dos seguintes tokens {token_esperado}, mas foi encontrado '{token_recebido.get('tipo')}' (valor: '{token_recebido.get('valor')}') na linha {token_recebido.get('linha')}.")
    else:
        print(f"Erro Sintático: Esperado um dos seguintes tokens {token_esperado}, mas o final da entrada foi alcançado.")
    # Em um compilador real, aqui entraria o modo pânico para recuperação de erro
    sys.exit(1)

def analisar_sintaticamente(tokens):
    """
    Função principal que realiza a análise sintática.
    Entrada: uma lista de tokens (dicionários) vinda do analisador léxico.
    Saída: a raiz da Árvore Sintática gerada, ou None em caso de erro.
    """
    # Adiciona o marcador de fim de fita ($) à lista de tokens
    tokens.append({'tipo': '$', 'valor': '$', 'linha': -1, 'coluna': -1})
    fita_entrada = tokens
    ponteiro = 0
    
    # Prepara a pilha com o marcador de fim e o símbolo inicial da gramática
    simbolo_inicial = 'PROGRAMA'
    no_raiz = TreeNode(simbolo_inicial)
    pilha = [('$', None), (simbolo_inicial, no_raiz)]

    # --- LOOP PRINCIPAL DA ANÁLISE ---
    while len(pilha) > 0:
        # Pega o topo da pilha e o token atual da fita, sem consumi-los
        simbolo_pilha, no_atual = pilha[-1]
        token_atual = fita_entrada[ponteiro]

        # Condição de SUCESSO: se a pilha e a fita chegaram ao fim ($)
        if simbolo_pilha == '$' and token_atual['tipo'] == '$':
            print("Análise sintática concluída com sucesso!")
            return no_raiz

        # CASO 1: Topo da pilha é um TERMINAL
        if simbolo_pilha == token_atual['tipo']:
            # Deu match! Consome o símbolo da pilha e o token da fita
            pilha.pop()
            if no_atual: # Adiciona o valor do token (ex: 'a', '10') como filho do nó
                 no_atual.add_child(TreeNode(f"'{token_atual['valor']}'"))
            ponteiro += 1
        
        # CASO 2: Topo da pilha é um NÃO-TERMINAL
        elif simbolo_pilha in tabela_preditiva:
            # Consulta a tabela de análise para decidir qual produção usar
            if token_atual['tipo'] in tabela_preditiva[simbolo_pilha]:
                producao = tabela_preditiva[simbolo_pilha][token_atual['tipo']]
                pilha.pop() # Remove o não-terminal do topo

                # Se a produção não for epsilon, empilha os símbolos da produção
                if producao[0] != 'epsilon':
                    # Empilha a produção na ordem inversa para manter a sequência correta
                    for simbolo in reversed(producao):
                        novo_no = TreeNode(simbolo)
                        if no_atual:
                            no_atual.add_child(novo_no)
                        pilha.append((simbolo, novo_no))
                else:
                    # Se for epsilon, apenas adiciona um nó 'epsilon' na árvore
                    if no_atual:
                        no_atual.add_child(TreeNode('epsilon'))
            else:
                # Erro: não há regra na tabela para essa combinação de não-terminal e token
                erro(list(tabela_preditiva[simbolo_pilha].keys()), token_atual)
        
        # CASO 3: ERRO - Topo da pilha é um terminal mas não corresponde à entrada
        else:
            erro(simbolo_pilha, token_atual)
    
    # Se sair do loop por outra razão (situação inesperada)
    print("Erro inesperado: A pilha terminou antes de processar toda a entrada.")
    return None