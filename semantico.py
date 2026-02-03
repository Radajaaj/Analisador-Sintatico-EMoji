import sys

# ------ TABELA DE SÍMBOLOS ------
class TabelaSimbolos:
    def __init__(self):
        # A pilha de escopos permite o aninhamento (ex: variáveis dentro de um IF não vazam para fora)
        # O índice [-1] sempre representa o escopo atual/topo da pilha
        self.pilha_escopos = [{}]

    def entrar_bloco(self):
        # Cria um novo dicionário vazio para o novo bloco e empilha
        self.pilha_escopos.append({})

    def sair_bloco(self):
        # Descarta as variáveis do bloco atual ao sair dele
        if len(self.pilha_escopos) > 1:
            self.pilha_escopos.pop()

    def declarar(self, nome, tipo):
        # Verifica apenas o escopo atual (topo) para impedir redeclaração no mesmo nível
        if nome in self.pilha_escopos[-1]:
            return False 
        self.pilha_escopos[-1][nome] = {"tipo": tipo}
        return True

    def buscar(self, nome):
        # Busca do escopo mais interno (topo) para o mais externo (global)
        # Necessário para encontrar variáveis declaradas antes de blocos aninhados
        for escopo in reversed(self.pilha_escopos):
            if nome in escopo:
                return escopo[nome]
        return None

# ------ GERADOR DE CÓDIGO INTERMEDIÁRIO (TAC) ------
class GeradorTAC:
    def __init__(self):
        self.temp_count = 0             # Contador para variáveis temporárias (t0, t1...)
        self.label_count = 0            # Contador para rótulos de desvio (L0, L1...)
        self.instrucoes = []

    def novo_temp(self):
        t = f"t{self.temp_count}"
        self.temp_count += 1
        return t

    def novo_label(self):
        l = f"L{self.label_count}"
        self.label_count += 1
        return l

    def add(self, instr):
        self.instrucoes.append(instr)

    def obter_codigo(self):
        # Formata a lista de instruções para uma string legível
        buffer = []
        buffer.append("="*40)
        buffer.append(" Código Intermediário (TAC)")
        buffer.append("="*40)
        for linha in self.instrucoes:
            # Labels ficam colados na margem, instruções ganham indentação visual
            if ":" in linha and "goto" not in linha:
                buffer.append(linha)
            else:
                buffer.append(f"    {linha}")
        buffer.append("="*40)
        return "\n".join(buffer)

# ------ ANALISADOR SEMÂNTICO ------
class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.gerador = GeradorTAC()
        self.erros = []

    def erro(self, msg):
        print(f"❌ ERRO SEMÂNTICO: {msg}")
        self.erros.append(msg)

    def pegar_valor_folha(self, no):
        """
        Navega recursivamente pela árvore sintática (CST) ignorando nós
        estruturais (não-terminais) até encontrar o token real (folha).
        Essencial porque a gramática gera muitos nós intermediários.
        """
        if no is None: 
            return None
        # Se o nó já é um token vindo do léxico (dicionário)
        if isinstance(no.value, dict): 
            return no.value.get('valor')

        val = str(no.value)
        # Se é um nó terminal simples (string) sem filhos
        if not hasattr(no, 'children') or not no.children: 
            return val

        # Busca em profundidade nos filhos
        for filho in no.children:
            res = self.pegar_valor_folha(filho)
            # Filtra tokens estruturais que não carregam valor semântico
            if res and res not in ['epsilon', ';', '(', ')', '{', '}', 'EOF']: 
                return res
        return None

    def normalizar_tipo(self, texto_ou_token):
        """
        Converte as diversas representações (Emoji, Token Name, String)
        para um padrão interno único (INT, STRING, BOOL) facilitando comparações.
        """
        if not texto_ou_token: return 'UNKNOWN'
        # Limpeza de aspas e espaços que podem vir do analisador léxico
        s = str(texto_ou_token).strip().replace("'", "").replace('"', '').upper()
        
        if s in ['🔢', 'INT', 'NUMERO_INT', 'INTEGER']: 
            return 'INT'
        if s in ['🔤', 'STRING', 'STRING_TYPE', 'STRING_LITERAL', 'STR']: 
            return 'STRING'
        if s in ['🤥', 'BOOL', 'VALOR_BOOL', 'TRUE', 'FALSE', '👍', '👎', 'BOOLEAN']: 
            return 'BOOL'
        return 'UNKNOWN'

    def traduzir_operador(self, op_emoji):
        """
        Traduz emojis para operadores padrão (C-like) para que o TAC 
        fique legível e universal (ex: ➕ vira +).
        """
        mapa = {
            # Relacionais
            '🐣': '<', '🐓': '>', '🥚': '==',
            '🤏': '<=', '✌️': '>=', '👎': '!=',
            '🤝': '==', 'OP_IGUAL_COMP': '==',
            # Lógicos
            'OP_AND': '&&', 'OP_OR': '||',
            # Matemáticos
            '➕': '+', '➖': '-', '✖️': '*', '➗': '/'
        }
        return mapa.get(op_emoji, op_emoji)

    # ------ ROTEAMENTO (DISPATCHER) ------
    def visitar(self, no):
        if no is None: return None
        
        # Identifica o tipo do nó (pode ser string ou dict dependendo da origem)
        rotulo = str(no.value) if not isinstance(no.value, dict) else no.value.get('tipo')
        if rotulo == 'epsilon': 
            return None

        # Redireciona para o método específico de tratamento
        if rotulo == "PROGRAMA":
            self.visitar_filhos(no)
            return len(self.erros) == 0     # Retorna sucesso apenas se sem erros

        elif rotulo in ["BLOCO_COMANDOS", "BLOCO_COMANDOS_", "LISTA_DECLARACOES"]:
            self.visitar_filhos(no)

        elif rotulo == "DECLARACAO_VAR": self.visitar_declaracao(no)
        elif rotulo == "ATRIBUICAO": self.visitar_atribuicao(no)
        elif rotulo == "ESTRUTURA_IF": self.visitar_if(no)
        elif rotulo == "ESTRUTURA_WHILE": self.visitar_while(no)
        elif rotulo == "ESTRUTURA_FOR": self.visitar_for(no)
        elif rotulo == "COMANDO_SAIDA": self.visitar_io(no, "PRINT")
        elif rotulo == "COMANDO_ENTRADA": self.visitar_io(no, "SCAN")
        elif rotulo == "EXPRESSAO": return self.visitar_expressao_completa(no)
        else: self.visitar_filhos(no)

    def visitar_filhos(self, no):
        for filho in no.children:
            self.visitar(filho)

    # ------ REGRAS SEMÂNTICAS E GERAÇÃO DE CÓDIGO ------

    def visitar_declaracao(self, no):
        if len(no.children) < 2: return
        raw_tipo = self.pegar_valor_folha(no.children[0])
        nome_id = self.pegar_valor_folha(no.children[1])
        
        # Limpeza preventiva de aspas que podem ter vindo da árvore
        nome_id = str(nome_id).replace("'", "").replace('"', "")
        tipo = self.normalizar_tipo(raw_tipo)

        # Regra Semântica: Unicidade de nome no escopo
        if not self.tabela.declarar(nome_id, tipo):
            self.erro(f"Variável '{nome_id}' já declarada neste escopo.")

    def visitar_atribuicao(self, no):
        nome = self.pegar_valor_folha(no.children[0])
        nome = str(nome).replace("'", "").replace('"', "")
        
        # Regra Semântica: Variável deve existir
        info = self.tabela.buscar(nome)
        if not info:
            self.erro(f"Variável '{nome}' não declarada.")
            return

        # Resolve a expressão do lado direito (RHS)
        res = None
        for filho in no.children:
            if str(filho.value) == "EXPRESSAO":
                res = self.visitar(filho)
                break
        
        # Fallback para gramáticas onde EXPRESSAO não é filho direto
        if not res and len(no.children) > 2:
             res = self.visitar_expressao_completa(no.children[2])

        if res:
            # Regra Semântica: Tipagem Forte (LHS type == RHS type)
            if info['tipo'] != res['tipo']:
                self.erro(f"Atribuição inválida em '{nome}'. Esperado {info['tipo']}, recebeu {res['tipo']}.")
            else:
                # Gera código: variável recebe o temporário da expressão
                self.gerador.add(f"{nome} = {res['end']}")

    def visitar_if(self, no):
        # 1. Resolve a condição
        res_cond = self._achar_expressao(no)
        
        # Regra Semântica: Condição deve ser Booleana
        if res_cond['tipo'] != 'BOOL': 
            self.erro(f"Condição do IF deve ser BOOL. Encontrado: {res_cond['tipo']}")

        # 2. Prepara os Labels para controle de fluxo
        l_else = self.gerador.novo_label()
        l_fim = self.gerador.novo_label()

        # 3. Gera salto condicional: Se Falso, pula pro Else
        self.gerador.add(f"if_false {res_cond['end']} goto {l_else}")
        
        # 4. Processa bloco TRUE (novo escopo)
        self.tabela.entrar_bloco()
        self._visitar_bloco_no_filho(no)
        self.tabela.sair_bloco()

        # 5. Pula o bloco Else ao terminar o True
        self.gerador.add(f"goto {l_fim}")
        
        # 6. Processa bloco ELSE (se existir)
        self.gerador.add(f"{l_else}:")
        for filho in no.children:
            if str(filho.value) == "ELSE_PARTE":
                 if self.pegar_valor_folha(filho) != 'epsilon':
                    self.tabela.entrar_bloco()
                    self.visitar_filhos(filho)
                    self.tabela.sair_bloco()
        
        # 7. Marca o fim da estrutura
        self.gerador.add(f"{l_fim}:")

    def visitar_while(self, no):
        l_ini = self.gerador.novo_label()       # Label para voltar ao início (loop)
        l_fim = self.gerador.novo_label()       # Label para sair do loop
        
        self.gerador.add(f"{l_ini}:")
        
        res_cond = self._achar_expressao(no)
        if res_cond['tipo'] != 'BOOL': 
            self.erro(f"Condição do WHILE deve ser BOOL. Encontrado: {res_cond['tipo']}")

        # Condição de saída
        self.gerador.add(f"if_false {res_cond['end']} goto {l_fim}")
        
        self.tabela.entrar_bloco()
        self._visitar_bloco_no_filho(no)
        self.tabela.sair_bloco()
        
        # Loop: volta para testar a condição
        self.gerador.add(f"goto {l_ini}")
        self.gerador.add(f"{l_fim}:")

    def visitar_for(self, no):
        # Pega as cláusulas do for (init; cond; inc)
        atribs = [f for f in no.children if str(f.value) == "ATRIBUICAO_FOR"]
        
        # 1. Executa a inicialização (antes do label)
        if atribs: self.visitar_atribuicao_for(atribs[0])
        
        l_ini = self.gerador.novo_label()
        l_fim = self.gerador.novo_label()
        
        self.gerador.add(f"{l_ini}:")
        
        # 2. Testa condição
        res_cond = self._achar_expressao(no)
        self.gerador.add(f"if_false {res_cond['end']} goto {l_fim}")
        
        # 3. Executa bloco
        self.tabela.entrar_bloco()
        self._visitar_bloco_no_filho(no)
        self.tabela.sair_bloco()
        
        # 4. Executa incremento (segunda atribuição)
        if len(atribs) > 1: 
            self.visitar_atribuicao_for(atribs[1])
        
        # 5. Volta pro teste
        self.gerador.add(f"goto {l_ini}")
        self.gerador.add(f"{l_fim}:")

    def visitar_atribuicao_for(self, no):
        # Versão simplificada da atribuição usada no cabeçalho do for
        nome = self.pegar_valor_folha(no.children[0])
        nome = str(nome).replace("'", "").replace('"', "")
        res = self.visitar(no.children[2])
        if res: self.gerador.add(f"{nome} = {res['end']}")

    def visitar_io(self, no, cmd):
        res = None
        for filho in no.children:
            val = str(filho.value)
            if val == "EXPRESSAO": 
                res = self.visitar(filho)
            elif val == "STRING_LITERAL":
                res = {'end': self.pegar_valor_folha(filho), 'tipo': 'STRING'}
            elif val == "ID": 
                nome = self.pegar_valor_folha(filho)
                nome = str(nome).replace("'", "").replace('"', "")
                res = {'end': nome, 'tipo': 'VAR'}
        if res: self.gerador.add(f"{cmd} {res['end']}")

    def _achar_expressao(self, no):
        for filho in no.children:
            if str(filho.value) == "EXPRESSAO": 
                return self.visitar(filho)
        return {'end': '0', 'tipo': 'BOOL'}     # Fallback seguro

    def _visitar_bloco_no_filho(self, no):
        for filho in no.children:
            if str(filho.value) in ["BLOCO_COMANDOS", "BLOCO_COMANDOS_"]: 
                self.visitar(filho)

    # ------ EXPRESSÕES ------
    # Implementa a recursão à direita da gramática (E -> T E')
    
    def visitar_expressao_completa(self, no):
        if not no.children: 
            return None
        # Visita o primeiro termo (lado esquerdo)
        val_esq = self.visitar_termo(no.children[0])
        
        # Se houver continuação (operador + outro termo), visita a "cauda"
        if len(no.children) > 1: 
            return self.visitar_expressao_linha(no.children[1], val_esq)
        return val_esq

    def visitar_expressao_linha(self, no, val_esq):
        # Caso base da recursão à direita (epsilon)
        if not no.children or str(no.children[0].value) == 'epsilon': 
            return val_esq

        # Pega e traduz o operador (ex: 🐓 -> >)
        op_node = no.children[0]
        op_emoji = self.pegar_valor_folha(op_node)
        op_emoji = str(op_emoji).strip().replace("'", "").replace('"', "")
        op_tac = self.traduzir_operador(op_emoji)

        val_dir = self.visitar_termo(no.children[1])
        
        # Define se o resultado é Booleano ou Inteiro com base no operador
        # Isso é crucial para validar condições de IF/WHILE
        ops_booleanos = ['<', '>', '==', '!=', '<=', '>=', '&&', '||']
        
        tipo_res = 'INT'
        if op_tac in ops_booleanos:
            tipo_res = 'BOOL'
        
        # Gera o código TAC: tX = op1 OPERADOR op2
        novo = self.gerador.novo_temp()
        self.gerador.add(f"{novo} = {val_esq['end']} {op_tac} {val_dir['end']}")
        
        res = {'end': novo, 'tipo': tipo_res}
        
        # Continua a recursão se houver mais operações encadeadas
        if len(no.children) > 2: 
            return self.visitar_expressao_linha(no.children[2], res)
        return res

    def visitar_termo(self, no):
        val_esq = self.visitar_fator(no.children[0])
        if len(no.children) > 1: 
            return self.visitar_termo_linha(no.children[1], val_esq)
        return val_esq

    def visitar_termo_linha(self, no, val_esq):
        # Similar a expressao_linha, mas para operadores de Termo (*, /)
        if not no.children or str(no.children[0].value) == 'epsilon': 
            return val_esq
        
        op_emoji = self.pegar_valor_folha(no.children[0])
        op_emoji = str(op_emoji).strip().replace("'", "").replace('"', "")
        op_tac = self.traduzir_operador(op_emoji)
        
        val_dir = self.visitar_fator(no.children[1])
        
        novo = self.gerador.novo_temp()
        self.gerador.add(f"{novo} = {val_esq['end']} {op_tac} {val_dir['end']}")
        res = {'end': novo, 'tipo': 'INT'}
        
        if len(no.children) > 2: 
            return self.visitar_termo_linha(no.children[2], res)
        return res

    def visitar_fator(self, no):
        primeiro = no.children[0]
        rotulo = str(primeiro.value)
        
        # Tratamento de parênteses (prioridade na expressão)
        if rotulo == "ABRIR_PARENTESES": 
            return self.visitar(no.children[1])
        
        val_bruto = self.pegar_valor_folha(primeiro)
        
        # Identificação de Tipos Literais
        if rotulo in ['NUMERO_INT', 'INT']: 
            return {'end': val_bruto, 'tipo': 'INT'}
        if rotulo in ['STRING_LITERAL', 'STRING_TYPE']: 
            return {'end': val_bruto, 'tipo': 'STRING'}
        if rotulo == 'VALOR_BOOL': 
            # TAC usa 0 e 1, mas a linguagem usa emojis
            return {'end': ('1' if val_bruto == '👍' else '0'), 'tipo': 'BOOL'}
        
        # Identificação de Variáveis
        if rotulo == 'ID':
            nome = str(val_bruto).replace("'", "").replace('"', "")
            info = self.tabela.buscar(nome)
            if not info:
                self.erro(f"Variável '{nome}' não declarada.")
                return {'end': nome, 'tipo': 'UNKNOWN'}
            return {'end': nome, 'tipo': info['tipo']}
            
        norm = self.normalizar_tipo(rotulo)
        if norm != 'UNKNOWN': 
            return {'end': val_bruto, 'tipo': norm}
        
        return {'end': val_bruto, 'tipo': 'UNKNOWN'}