# Analisador Sintático E-moji (sem análise léxica)
# Alunos: Fernando Seiji Onoda Inomata, Lucas Batista Deinzer Duarte, Vitor Mayorca Camargo

import sys
import json
import re

class Token:
    """Uma classe para armazenar as informações de cada token."""
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna
    def __repr__(self):
        return f"[{self.tipo}, '{self.valor}', L:{self.linha}, C:{self.coluna}]"

def carregar_tokens_de_arquivo(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read().strip()
    if not conteudo:
        return []

    # Tenta JSON primeiro
    try:
        dados = json.loads(conteudo)
        tokens = []
        for item in dados:
            # item pode ser dict ou [tipo, valor, linha, coluna]
            if isinstance(item, dict):
                tokens.append(Token(item.get('tipo'), item.get('valor'), item.get('linha'), item.get('coluna')))
            elif isinstance(item, list) and len(item) >= 4:
                tokens.append(Token(item[0], item[1], item[2], item[3]))
            else:
                raise ValueError("Formato JSON de token inválido")
        return tokens
    except Exception:
        pass

    # Tenta formato de uma linha por token com repr: [TIPO, 'valor', L:linha, C:coluna]
    padrao = re.compile(r"\[(?P<tipo>[A-Z_0-9]+),\s*'(?P<valor>.*?)',\s*L:(?P<linha>-?\d+),\s*C:(?P<coluna>-?\d+)\]")
    tokens = []
    for linha_texto in conteudo.splitlines():
        linha_texto = linha_texto.strip()
        if not linha_texto:
            continue
        m = padrao.match(linha_texto)
        if not m:
            raise ValueError(f"Formato de token desconhecido na linha: {linha_texto!r}")
        tipo = m.group('tipo')
        valor = m.group('valor')
        linha_num = int(m.group('linha'))
        coluna_num = int(m.group('coluna'))
        tokens.append(Token(tipo, valor, linha_num, coluna_num))
    return tokens

class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao_atual = 0
        self.erros = []

    def token_atual(self):
        if self.posicao_atual < len(self.tokens):
            return self.tokens[self.posicao_atual]
        return Token('FIM_DE_ARQUIVO', None, -1, -1)

    def avancar(self):
        self.posicao_atual += 1

    def consumir(self, tipo_esperado):
        token = self.token_atual()
        if token.tipo == tipo_esperado:
            self.avancar(); 
            return token
        else:
            raise SyntaxError(f"Esperado '{tipo_esperado}' mas encontrou '{token.tipo}' na linha {token.linha}")

    def registrar_erro(self, erro):
        # Salva informação detalhada do erro (mensagem + posição do token atual) e sincroniza.
        token = self.token_atual()
        mensagem = f"{erro} (L:{token.linha}, C:{token.coluna}, token_atual:{token.tipo})"
        self.erros.append(mensagem)
        # tenta sincronizar para continuar a análise
        self.sincronizar()

    def sincronizar(self):
        TOKENS_SINCRONIZACAO = {
            'PONTO_VIRGULA',
            'IF',
            'WHILE',
            'FOR',
            'FECHAR_BLOCO',
            'FIM_DE_ARQUIVO'
            }
        # avança até encontrar um token de sincronização ou EOF
        while self.token_atual().tipo not in TOKENS_SINCRONIZACAO:
            # se estivermos no EOF, apenas retorna
            if self.token_atual().tipo == 'FIM_DE_ARQUIVO':
                return
            self.avancar()
        # consome o PONTO_VIRGULA para continuar após o erro, se presente
        if self.token_atual().tipo == 'PONTO_VIRGULA':
            self.avancar()

    def analisar(self):
        # Continua tentando analisar até chegar ao FIM_DE_ARQUIVO, coletando erros ao longo do caminho.
        # Agora chamamos analisar_comando repetidamente (em vez de analisar_lista_comandos inteira),
        # registrando erros e garantindo progresso para evitar loops infinitos.
        while self.token_atual().tipo != 'FIM_DE_ARQUIVO':
            pos_antes = self.posicao_atual
            try:
                self.analisar_comando()
            except SyntaxError as e:
                self.registrar_erro(e)
            # se não houve progresso, avançamos um token para evitar loop infinito
            if self.posicao_atual == pos_antes:
                self.avancar()
        # retorna True se não houve erros registrados
        return len(self.erros) == 0

    # Tradução da Gramática BNF
    def analisar_programa(self):
        self.analisar_lista_comandos()
        if self.token_atual().tipo != 'FIM_DE_ARQUIVO':
            self.registrar_erro(SyntaxError("Tokens inesperados no final do programa."))

    def analisar_lista_comandos(self):
        while self.token_atual().tipo not in ('FECHAR_BLOCO', 'FIM_DE_ARQUIVO', 'ELSE', 'ELSEIF'):
            self.analisar_comando()

    def analisar_comando(self):
        try:
            tipo_token = self.token_atual().tipo
            if tipo_token in ('INT', 'STRING_TYPE', 'BOOL'):
                self.analisar_declaracao_variavel()
            elif tipo_token == 'ID':
                self.analisar_atribuicao()
            elif tipo_token in ('COMANDO_SAIDA', 'COMANDO_ENTRADA'):
                self.analisar_comando_io()
            elif tipo_token == 'IF':
                self.analisar_estrutura_if()
            elif tipo_token == 'WHILE':
                self.analisar_estrutura_while()
            elif tipo_token == 'FOR':
                self.analisar_estrutura_for()
            elif tipo_token == 'ABRIR_BLOCO':
                self.analisar_bloco()
            else:
                raise SyntaxError(f"Comando inválido ou inesperado iniciado com '{tipo_token}'")
        except SyntaxError as e:
            self.registrar_erro(e)

    def analisar_bloco(self):
        self.consumir('ABRIR_BLOCO')
        self.analisar_lista_comandos()
        self.consumir('FECHAR_BLOCO')

    def analisar_declaracao_variavel(self):
        self.consumir(self.token_atual().tipo)
        self.consumir('ID')
        self.consumir('PONTO_VIRGULA')

    def analisar_atribuicao(self):
        self.consumir('ID')
        self.consumir('ATRIBUICAO')
        self.analisar_expressao()
        self.consumir('PONTO_VIRGULA')

    def analisar_comando_io(self):
        tipo_comando = self.token_atual().tipo
        self.consumir(tipo_comando)
        self.consumir('ABRIR_PARENTESES')
        if tipo_comando == 'COMANDO_SAIDA':
            self.analisar_expressao()
        else:
            self.consumir('ID')
        self.consumir('FECHAR_PARENTESES')
        self.consumir('PONTO_VIRGULA')

    def analisar_estrutura_if(self):
        self.consumir('IF')
        self.consumir('ABRIR_PARENTESES')
        self.analisar_expressao()
        self.consumir('FECHAR_PARENTESES')
        self.analisar_bloco()
        self.analisar_parte_else()

    def analisar_parte_else(self):
        if self.token_atual().tipo == 'ELSEIF':
            self.consumir('ELSEIF')
            self.consumir('ABRIR_PARENTESES')
            self.analisar_expressao()
            self.consumir('FECHAR_PARENTESES')
            self.analisar_bloco()
            self.analisar_parte_else()
        elif self.token_atual().tipo == 'ELSE':
            self.consumir('ELSE')
            self.analisar_bloco()

    def analisar_estrutura_while(self):
        self.consumir('WHILE')
        self.consumir('ABRIR_PARENTESES')
        self.analisar_expressao()
        self.consumir('FECHAR_PARENTESES')
        self.analisar_bloco()

    def analisar_estrutura_for(self):
        self.consumir('FOR')
        self.consumir('ABRIR_PARENTESES')
        self.analisar_atribuicao_sem_pv()
        self.consumir('PONTO_VIRGULA')
        self.analisar_expressao()
        self.consumir('PONTO_VIRGULA')
        self.analisar_atribuicao_sem_pv()
        self.consumir('FECHAR_PARENTESES')
        self.analisar_bloco()

    def analisar_atribuicao_sem_pv(self):
        self.consumir('ID')
        self.consumir('ATRIBUICAO')
        self.analisar_expressao()

    def analisar_expressao(self):
        self.analisar_termo_logico()
        while self.token_atual().tipo == 'OP_OR':
            self.avancar()
            self.analisar_termo_logico()

    def analisar_termo_logico(self):
        self.analisar_fator_relacional()
        while self.token_atual().tipo == 'OP_AND':
            self.avancar()
            self.analisar_fator_relacional()

    def analisar_fator_relacional(self):
        self.analisar_expressao_aritmetica()
        if self.token_atual().tipo in ('OP_MAIOR', 'OP_MENOR', 'OP_IGUAL_COMP', 'OP_IGUAL_LOGICO'):
            self.avancar()
            self.analisar_expressao_aritmetica()

    def analisar_expressao_aritmetica(self):
        self.analisar_termo()
        while self.token_atual().tipo in ('OP_SOMA', 'OP_SUB'):
            self.avancar()
            self.analisar_termo()

    def analisar_termo(self):
        self.analisar_fator()
        while self.token_atual().tipo in ('OP_MULT', 'OP_DIV'):
            self.avancar()
            self.analisar_fator()

    def analisar_fator(self):
        token = self.token_atual()
        if token.tipo in ('NUMERO_INT', 'STRING_LITERAL', 'TRUE', 'FALSE', 'ID'):
            self.avancar()
        elif token.tipo == 'ABRIR_PARENTESES':
            self.consumir('ABRIR_PARENTESES')
            self.analisar_expressao()
            self.consumir('FECHAR_PARENTESES')
        else:
            raise SyntaxError(f"Fator inválido: token '{token.tipo}' inesperado.")

# Execução Principal

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python analisador_sintatico.py <arquivo.emojilex>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    if not caminho_arquivo.lower().endswith('.emojilex'):
        print("Erro: o arquivo deve terminar com a extensão .emojilex")
        sys.exit(1)

    try:
        tokens = carregar_tokens_de_arquivo(caminho_arquivo)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao carregar tokens: {e}")
        sys.exit(1)

    # Fase 2: Análise Sintática
    print("\n--- Iniciando Análise Sintática ---")
    parser = AnalisadorSintatico(tokens)
    sintaxe_ok = parser.analisar()

    if sintaxe_ok:
        print("\nAnálise Sintática concluída com sucesso! O código é válido.")
    else:
        print("\nAnálise Sintática falhou. Erros encontrados:")
        for erro in parser.erros:
            print(f"- {erro}")
