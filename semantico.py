# -*- coding: utf-8 -*-
import sys

# Tabela de Símbolos
class TabelaSimbolos:
    def __init__(self):
        self.pilha_escopos = [{}]

    def entrar_bloco(self):
        self.pilha_escopos.append({})

    def sair_bloco(self):
        if len(self.pilha_escopos) > 1:
            self.pilha_escopos.pop()

    def declarar(self, nome, tipo):
        # Verifica se já existe no escopo atual (o último da pilha)
        if nome in self.pilha_escopos[-1]:
            return False 
        self.pilha_escopos[-1][nome] = {"tipo": tipo}
        return True

    def buscar(self, nome):
        # Busca do escopo mais interno para o mais externo
        for escopo in reversed(self.pilha_escopos):
            if nome in escopo:
                return escopo[nome]
        return None

# Gerador de Código Intermediário (TAC)
class GeradorTAC:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
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
        buffer = []
        buffer.append("="*40)
        buffer.append(" Código Intermediário (TAC)")
        buffer.append("="*40)
        for linha in self.instrucoes:
            # Identação simples para labels
            if ":" in linha and "goto" not in linha:
                buffer.append(linha)
            else:
                buffer.append(f"    {linha}")
        buffer.append("="*40)
        return "\n".join(buffer)

# Analisador Semântico
class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.gerador = GeradorTAC()
        self.erros = []

    def erro(self, msg):
        print(f"❌ ERRO SEMÂNTICO: {msg}")
        self.erros.append(msg)

    def pegar_valor_folha(self, no):
        if no is None: 
            return None
        if isinstance(no.value, dict): 
            return no.value.get('valor')

        val = str(no.value)
        if not hasattr(no, 'children') or not no.children: 
            return val

        for filho in no.children:
            res = self.pegar_valor_folha(filho)
            if res and res not in ['epsilon', ';', '(', ')', '{', '}', 'EOF']: 
                return res
        return None

    def normalizar_tipo(self, texto_ou_token):
        if not texto_ou_token: return 'UNKNOWN'
        # Remove aspas e espaços
        s = str(texto_ou_token).strip().replace("'", "").replace('"', '').upper()
        
        if s in ['🔢', 'INT', 'NUMERO_INT', 'INTEGER']: 
            return 'INT'
        if s in ['🔤', 'STRING', 'STRING_TYPE', 'STRING_LITERAL', 'STR']: 
            return 'STRING'
        if s in ['🤥', 'BOOL', 'VALOR_BOOL', 'TRUE', 'FALSE', '👍', '👎', 'BOOLEAN']: 
            return 'BOOL'
        return 'UNKNOWN'

    # Mapa de tradução de operadores
    def traduzir_operador(self, op_emoji):
        mapa = {
            # Relacionais
            '🐣': '<',
            '🐓': '>',
            '🥚': '==',
            '🤏': '<=',
            '✌️': '>=',
            '👎': '!=',
            '🤝': '==',
            'OP_IGUAL_COMP': '==',
            
            # Lógicos
            'OP_AND': '&&',
            'OP_OR': '||',
            
            # Matemáticos
            '➕': '+',
            '➖': '-',
            '✖️': '*',
            '➗': '/'
        }
        return mapa.get(op_emoji, op_emoji)

    # Roteamento
    def visitar(self, no):
        if no is None: return None
        
        rotulo = str(no.value) if not isinstance(no.value, dict) else no.value.get('tipo')
        if rotulo == 'epsilon': 
            return None

        if rotulo == "PROGRAMA":
            self.visitar_filhos(no)
            return len(self.erros) == 0

        elif rotulo in ["BLOCO_COMANDOS", "BLOCO_COMANDOS_", "LISTA_DECLARACOES"]:
            self.visitar_filhos(no)

        elif rotulo == "DECLARACAO_VAR": 
            self.visitar_declaracao(no)
        elif rotulo == "ATRIBUICAO": 
            self.visitar_atribuicao(no)
        elif rotulo == "ESTRUTURA_IF": 
            self.visitar_if(no)
        elif rotulo == "ESTRUTURA_WHILE": 
            self.visitar_while(no)
        elif rotulo == "ESTRUTURA_FOR": 
            self.visitar_for(no)
        elif rotulo == "COMANDO_SAIDA": 
            self.visitar_io(no, "PRINT")
        elif rotulo == "COMANDO_ENTRADA": 
            self.visitar_io(no, "SCAN")
        elif rotulo == "EXPRESSAO": 
            return self.visitar_expressao_completa(no)
        else: 
            self.visitar_filhos(no)

    def visitar_filhos(self, no):
        for filho in no.children:
            self.visitar(filho)

    # Regras
    def visitar_declaracao(self, no):
        if len(no.children) < 2: return
        raw_tipo = self.pegar_valor_folha(no.children[0])
        nome_id = self.pegar_valor_folha(no.children[1])
        # Limpa aspas do nome da variavel
        nome_id = str(nome_id).replace("'", "").replace('"', "")
        tipo = self.normalizar_tipo(raw_tipo)

        # [CORREÇÃO] Verifica se declarou com sucesso
        if not self.tabela.declarar(nome_id, tipo):
            self.erro(f"Variável '{nome_id}' já declarada neste escopo.")

    def visitar_atribuicao(self, no):
        nome = self.pegar_valor_folha(no.children[0])
        nome = str(nome).replace("'", "").replace('"', "")
        
        info = self.tabela.buscar(nome)
        if not info:
            self.erro(f"Variável '{nome}' não declarada.")
            return

        res = None
        for filho in no.children:
            if str(filho.value) == "EXPRESSAO":
                res = self.visitar(filho)
                break
        if not res and len(no.children) > 2:
             res = self.visitar_expressao_completa(no.children[2])

        if res:
            if info['tipo'] != res['tipo']:
                self.erro(f"Atribuição inválida em '{nome}'. Esperado {info['tipo']}, recebeu {res['tipo']}.")
            else:
                self.gerador.add(f"{nome} = {res['end']}")

    def visitar_if(self, no):
        res_cond = self._achar_expressao(no)
        
        if res_cond['tipo'] != 'BOOL': 
            self.erro(f"Condição do IF deve ser BOOL. Encontrado: {res_cond['tipo']}")

        l_else = self.gerador.novo_label()
        l_fim = self.gerador.novo_label()

        self.gerador.add(f"if_false {res_cond['end']} goto {l_else}")
        self.tabela.entrar_bloco()
        self._visitar_bloco_no_filho(no)
        self.tabela.sair_bloco()

        self.gerador.add(f"goto {l_fim}")
        self.gerador.add(f"{l_else}:")

        for filho in no.children:
            if str(filho.value) == "ELSE_PARTE":
                 if self.pegar_valor_folha(filho) != 'epsilon':
                    self.tabela.entrar_bloco()
                    self.visitar_filhos(filho)
                    self.tabela.sair_bloco()
        self.gerador.add(f"{l_fim}:")

    def visitar_while(self, no):
        l_ini = self.gerador.novo_label()
        l_fim = self.gerador.novo_label()
        self.gerador.add(f"{l_ini}:")
        
        res_cond = self._achar_expressao(no)
        if res_cond['tipo'] != 'BOOL': 
            self.erro(f"Condição do WHILE deve ser BOOL. Encontrado: {res_cond['tipo']}")

        self.gerador.add(f"if_false {res_cond['end']} goto {l_fim}")
        self.tabela.entrar_bloco()
        self._visitar_bloco_no_filho(no)
        self.tabela.sair_bloco()
        self.gerador.add(f"goto {l_ini}")
        self.gerador.add(f"{l_fim}:")

    def visitar_for(self, no):
        atribs = [f for f in no.children if str(f.value) == "ATRIBUICAO_FOR"]
        if atribs: self.visitar_atribuicao_for(atribs[0])
        l_ini = self.gerador.novo_label()
        l_fim = self.gerador.novo_label()
        self.gerador.add(f"{l_ini}:")
        
        res_cond = self._achar_expressao(no)
        self.gerador.add(f"if_false {res_cond['end']} goto {l_fim}")
        
        self.tabela.entrar_bloco()
        self._visitar_bloco_no_filho(no)
        self.tabela.sair_bloco()
        if len(atribs) > 1: 
            self.visitar_atribuicao_for(atribs[1])
        self.gerador.add(f"goto {l_ini}")
        self.gerador.add(f"{l_fim}:")

    def visitar_atribuicao_for(self, no):
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
        return {'end': '0', 'tipo': 'BOOL'}

    def _visitar_bloco_no_filho(self, no):
        for filho in no.children:
            if str(filho.value) in ["BLOCO_COMANDOS", "BLOCO_COMANDOS_"]: 
                self.visitar(filho)

    # --- EXPRESSÕES (COM TRADUÇÃO) ---
    def visitar_expressao_completa(self, no):
        if not no.children: 
            return None
        val_esq = self.visitar_termo(no.children[0])
        if len(no.children) > 1: 
            return self.visitar_expressao_linha(no.children[1], val_esq)
        return val_esq

    def visitar_expressao_linha(self, no, val_esq):
        if not no.children or str(no.children[0].value) == 'epsilon': 
            return val_esq

        op_node = no.children[0]
        op_emoji = self.pegar_valor_folha(op_node)
        op_emoji = str(op_emoji).strip().replace("'", "").replace('"', "")

        # [CORREÇÃO] Traduz para operador padrão (TAC)
        op_tac = self.traduzir_operador(op_emoji)

        val_dir = self.visitar_termo(no.children[1])
        
        # Define se o resultado é Booleano ou Inteiro baseando-se no operador traduzido
        ops_booleanos = ['<', '>', '==', '!=', '<=', '>=', '&&', '||']
        
        tipo_res = 'INT'
        if op_tac in ops_booleanos:
            tipo_res = 'BOOL'
        
        novo = self.gerador.novo_temp()
        self.gerador.add(f"{novo} = {val_esq['end']} {op_tac} {val_dir['end']}")
        
        res = {'end': novo, 'tipo': tipo_res}
        if len(no.children) > 2: 
            return self.visitar_expressao_linha(no.children[2], res)
        return res

    def visitar_termo(self, no):
        val_esq = self.visitar_fator(no.children[0])
        if len(no.children) > 1: 
            return self.visitar_termo_linha(no.children[1], val_esq)
        return val_esq

    def visitar_termo_linha(self, no, val_esq):
        if not no.children or str(no.children[0].value) == 'epsilon': 
            return val_esq
        
        op_emoji = self.pegar_valor_folha(no.children[0])
        op_emoji = str(op_emoji).strip().replace("'", "").replace('"', "")
        
        # [CORREÇÃO] Traduz operadores matemáticos também (➕ -> +)
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
        
        if rotulo == "ABRIR_PARENTESES": 
            return self.visitar(no.children[1])
        
        val_bruto = self.pegar_valor_folha(primeiro)
        
        if rotulo in ['NUMERO_INT', 'INT']: 
            return {'end': val_bruto, 'tipo': 'INT'}
        if rotulo in ['STRING_LITERAL', 'STRING_TYPE']: 
            return {'end': val_bruto, 'tipo': 'STRING'}
        if rotulo == 'VALOR_BOOL': 
            return {'end': ('1' if val_bruto == '👍' else '0'), 'tipo': 'BOOL'}
        
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