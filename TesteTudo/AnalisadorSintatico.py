# Analisador Sintático E-moji (Versão com Gramática Corrigida)

# Classe para representar um nó na árvore sintática
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, node):
        # Inserimos no início para que, ao imprimir, a ordem fique igual à da regra
        self.children.insert(0, node)

# Função para imprimir a árvore de forma visual
def print_tree(node, prefix="", is_last=True):
    print(prefix + ("└── " if is_last else "├── ") + str(node.value))
    # Percorrer a lista de filhos na ordem inversa para imprimir corretamente
    children_count = len(node.children)
    for i, child in enumerate(reversed(node.children)):
        is_child_last = (i == children_count - 1)
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(child, new_prefix, is_child_last)

# Tabela de Análise Preditiva M ATUALIZADA
# Substitua a tabela inteira por esta versão final e corrigida:
tabela_preditiva = {
    'PROGRAMA': {
        'INT': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'STRING_TYPE': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'BOOL': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'],
        'ID': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'IF': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'COMANDO_SAIDA': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'], 'COMANDO_ENTRADA': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS'],
        '$': ['LISTA_DECLARACOES', 'BLOCO_COMANDOS']
    },
    'LISTA_DECLARACOES': {
        'INT': ['DECLARACAO_VAR', 'LISTA_DECLARACOES'], 'STRING_TYPE': ['DECLARACAO_VAR', 'LISTA_DECLARACOES'], 'BOOL': ['DECLARACAO_VAR', 'LISTA_DECLARACOES'],
        'ID': ['epsilon'], 'IF': ['epsilon'], 'COMANDO_SAIDA': ['epsilon'], 'COMANDO_ENTRADA': ['epsilon'], '$': ['epsilon']
    },
    'DECLARACAO_VAR': {
        'INT': ['TIPO', 'ID', 'PONTO_VIRGULA'], 'STRING_TYPE': ['TIPO', 'ID', 'PONTO_VIRGULA'], 'BOOL': ['TIPO', 'ID', 'PONTO_VIRGULA']
    },
    'TIPO': {
        'INT': ['INT'], 'STRING_TYPE': ['STRING_TYPE'], 'BOOL': ['BOOL']
    },
    'BLOCO_COMANDOS': {
        'ID': ['COMANDO', 'BLOCO_COMANDOS_'], 'IF': ['COMANDO', 'BLOCO_COMANDOS_'], 'COMANDO_SAIDA': ['COMANDO', 'BLOCO_COMANDOS_'], 'COMANDO_ENTRADA': ['COMANDO', 'BLOCO_COMANDOS_'],
        'FECHAR_BLOCO': ['epsilon'], '$': ['epsilon']
    },
    'BLOCO_COMANDOS_': {
        'ID': ['COMANDO', 'BLOCO_COMANDOS_'], 'IF': ['COMANDO', 'BLOCO_COMANDOS_'], 'COMANDO_SAIDA': ['COMANDO', 'BLOCO_COMANDOS_'], 'COMANDO_ENTRADA': ['COMANDO', 'BLOCO_COMANDOS_'],
        'FECHAR_BLOCO': ['epsilon'], '$': ['epsilon']
    },
    # REGRA 'COMANDO' CORRIGIDA E EXPANDIDA
    'COMANDO': {
        'ID': ['ATRIBUICAO'],
        'IF': ['ESTRUTURA_IF'],
        'COMANDO_SAIDA': ['COMANDO_SAIDA', 'ABRIR_PARENTESES', 'EXPRESSAO', 'FECHAR_PARENTESES', 'PONTO_VIRGULA'],
        'COMANDO_ENTRADA': ['COMANDO_ENTRADA', 'ABRIR_PARENTESES', 'ID', 'FECHAR_PARENTESES', 'PONTO_VIRGULA']
    },
    'ATRIBUICAO': {
        'ID': ['ID', 'ATRIBUICAO', 'EXPRESSAO', 'PONTO_VIRGULA']
    },
    'ESTRUTURA_IF': {
        'IF': ['IF', 'ABRIR_PARENTESES', 'EXPRESSAO', 'FECHAR_PARENTESES', 'ABRIR_BLOCO', 'BLOCO_COMANDOS', 'FECHAR_BLOCO', 'ELSE_PARTE']
    },
    'ELSE_PARTE': {
        'ELSE': ['ELSE', 'ABRIR_BLOCO', 'BLOCO_COMANDOS', 'FECHAR_BLOCO'],
        'ID': ['epsilon'], 'IF': ['epsilon'], 'COMANDO_SAIDA': ['epsilon'], 'COMANDO_ENTRADA': ['epsilon'], 'FECHAR_BLOCO': ['epsilon'], '$': ['epsilon']
    },
    # AS REGRAS PARA 'COMANDO_SAIDA' E 'COMANDO_ENTRADA' FORAM REMOVIDAS DAQUI
    'EXPRESSAO': {
        'ABRIR_PARENTESES': ['TERMO', 'EXPRESSAO_'], 'ID': ['TERMO', 'EXPRESSAO_'], 'NUMERO_INT': ['TERMO', 'EXPRESSAO_'], 'STRING_LITERAL': ['TERMO', 'EXPRESSAO_'], 'TRUE': ['TERMO', 'EXPRESSAO_'], 'FALSE': ['TERMO', 'EXPRESSAO_'], 'OP_MAIOR': ['TERMO', 'EXPRESSAO_']
    },
    'EXPRESSAO_': {
        'OP_SOMA': ['OP_SOMA', 'TERMO', 'EXPRESSAO_'], 'OP_SUB': ['OP_SUB', 'TERMO', 'EXPRESSAO_'], 'OP_MAIOR': ['OP_MAIOR', 'TERMO', 'EXPRESSAO_'],
        'FECHAR_PARENTESES': ['epsilon'], 'PONTO_VIRGULA': ['epsilon']
    },
    'TERMO': {
        'ABRIR_PARENTESES': ['FATOR', 'TERMO_'], 'ID': ['FATOR', 'TERMO_'], 'NUMERO_INT': ['FATOR', 'TERMO_'], 'STRING_LITERAL': ['FATOR', 'TERMO_'], 'TRUE': ['FATOR', 'TERMO_'], 'FALSE': ['FATOR', 'TERMO_']
    },
    'TERMO_': {
        'OP_MULT': ['OP_MULT', 'FATOR', 'TERMO_'], 'OP_DIV': ['OP_DIV', 'FATOR', 'TERMO_'],
        'OP_SOMA': ['epsilon'], 'OP_SUB': ['epsilon'], 'FECHAR_PARENTESES': ['epsilon'], 'PONTO_VIRGULA': ['epsilon'], 'OP_MAIOR': ['epsilon']
    },
    'FATOR': {
        'ABRIR_PARENTESES': ['ABRIR_PARENTESES', 'EXPRESSAO', 'FECHAR_PARENTESES'], 'ID': ['ID'], 'NUMERO_INT': ['NUMERO_INT'], 'STRING_LITERAL': ['STRING_LITERAL'], 'TRUE': ['VALOR_BOOL'], 'FALSE': ['VALOR_BOOL']
    },
    'VALOR_BOOL': {
        'TRUE': ['TRUE'], 'FALSE': ['FALSE']
    }
}

def erro(token_esperado, token_recebido):
    if token_recebido and token_recebido.get('linha'):
        print(f"Erro Sintático: Esperado um dos seguintes tokens {token_esperado}, mas foi encontrado '{token_recebido.get('tipo')}' (valor: '{token_recebido.get('valor')}') na linha {token_recebido.get('linha')}.")
    else:
        print(f"Erro Sintático: Esperado um dos seguintes tokens {token_esperado}, mas o final da entrada foi alcançado.")
    exit(1)

def analisar_sintaticamente(tokens):
    tokens.append({'tipo': '$', 'valor': '$', 'linha': -1, 'coluna': -1})
    fita_entrada = tokens
    ponteiro = 0
    
    simbolo_inicial = 'PROGRAMA'
    no_raiz = TreeNode(simbolo_inicial)
    pilha = [('$', None), (simbolo_inicial, no_raiz)]

    while len(pilha) > 0:
        simbolo_pilha, no_atual = pilha[-1]
        token_atual = fita_entrada[ponteiro]

        if simbolo_pilha == '$' and token_atual['tipo'] == '$':
            print("Análise sintática concluída com sucesso!")
            return no_raiz

        if simbolo_pilha == token_atual['tipo']:
            pilha.pop()
            if no_atual:
                 no_atual.add_child(TreeNode(f"'{token_atual['valor']}'"))
            ponteiro += 1
        
        elif simbolo_pilha in tabela_preditiva:
            if token_atual['tipo'] in tabela_preditiva[simbolo_pilha]:
                producao = tabela_preditiva[simbolo_pilha][token_atual['tipo']]
                pilha.pop()

                if producao[0] != 'epsilon':
                    for simbolo in reversed(producao):
                        novo_no = TreeNode(simbolo)
                        if no_atual:
                            no_atual.add_child(novo_no)
                        pilha.append((simbolo, novo_no))
                else:
                    if no_atual:
                        no_atual.add_child(TreeNode('epsilon'))
            else:
                erro(list(tabela_preditiva[simbolo_pilha].keys()), token_atual)
        
        else:
            erro(simbolo_pilha, token_atual)
    
    print("Erro inesperado: A pilha terminou antes de processar toda a entrada.")
    return None