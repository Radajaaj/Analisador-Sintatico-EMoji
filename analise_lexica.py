# Analisador Léxico E-moji
# Alunos: Fernando Seiji Onoda Inomata, Lucas Batista Deinzer Duarte, Vitor Mayorca Camargo

import sys
import os


# Isso ai vai mapear cada lexema/caractere/emoji para um tipo de token
#   Se fosse no C, isso seria um enum
TOKEN_MAP = {
    '🔢': 'INT',              # Int
    '🔤': 'STRING_TYPE',      # string
    '🤥': 'BOOL',             # booleano
    '👍': 'TRUE',             # true
    '👎': 'FALSE',            # false
    '➕': 'OP_SOMA',          # +
    '➖': 'OP_SUB',           # -
    '✖️': 'OP_MULT',          # *
    '➗': 'OP_DIV',           # /
    '🐓': 'OP_MAIOR',         # >
    '🐣': 'OP_MENOR',         # <
    '🥚': 'OP_IGUAL_COMP',    # == (aritmetico)
    '🤏': 'OP_AND',           # &&
    '✌️': 'OP_OR',            # ||
    '🤝': 'OP_IGUAL_LOGICO',  # == (logico)
    '👂': 'COMANDO_ENTRADA',  # scanf
    '👄': 'COMANDO_SAIDA',    # printf
    '🤨': 'IF',               # if
    '🤔': 'ELSEIF',           # elif
    '🖖': 'ELSE',             # else
    '😑': 'WHILE',            # while
    '😮': 'FOR',              # for
    '🤜': 'ABRIR_BLOCO',      # {
    '🤛': 'FECHAR_BLOCO',     # }
    '🎁': 'ATRIBUICAO',       # Atribuicao (pra nao ter ambiguidade com o 🥚)
    '(': 'ABRIR_PARENTESES',   # (
    ')': 'FECHAR_PARENTESES',  # )
    ';': 'PONTO_VIRGULA',      # ;
}


def analisar(codigo_fonte):
    """
    Função que faz a análise léxica do código
    Entrada: string contendo um código em e-moji
    Saída: tupla contendo (lista_de_tokens, status_sucesso).
    """
    tokens = []             # Lista pra guardar os tokens
    linha = 1               # Contador de linha para encontrar a posição do erro
    coluna = 1              # Contador de coluna, mesma coisa
    i = 0                   # Index que caminha pela string do codigo_fonte
    sucesso = True          # Flag, False indica erro
    
    # Loop principal, lê o código caractere por caractere
    while i < len(codigo_fonte):
        char = codigo_fonte[i]

        # Pula espaços brancos, quebra de linhas, tab, pois estes não são tokens
        if char.isspace():
            if char == '\n':    # Se for quebra de linha, incrementa a linha e reinicia a coluna
                linha += 1      
                coluna = 1      
            else:               # Se for espaço ou tab, so incrementa a coluna 
                coluna += 1     
            i += 1              #próximo caractere
            continue            #Volta pro começo do while

        # PULA COMENTÁRIOS
        # Tudo que estiver entre 🤫 e 👀 vai ser ignorado
        if char == '🤫':
            inicio_comentario_col = coluna
            i += 1              # Pula o emoji de início de comentário
            coluna += 1
            pos_inicial_comentario = i
            # dai lê até achar o emoji de fim de comentário
            while i < len(codigo_fonte) and codigo_fonte[i] != '👀':
                i += 1
            
            # Chama um erro caso não exista o emoji de fim de comentário
            if i == len(codigo_fonte):
                print(f"Erro Léxico: Comentário iniciado na linha {linha} coluna {inicio_comentario_col} não foi fechado.", file=sys.stderr)
                sucesso = False
                break 
            
            # Se achou o emoji, atualiza os contadores de linha/coluna
            # (para saber onde o código continua depois do comentário)
            comentario_conteudo = codigo_fonte[pos_inicial_comentario:i]
            novas_linhas = comentario_conteudo.count('\n')
            if novas_linhas > 0:
                linha += novas_linhas
                coluna = len(comentario_conteudo.split('\n')[-1]) + 1
            else:
                coluna += len(comentario_conteudo)
            
            i += 1 # Pula o '👀'
            coluna += 1
            continue # Volta pro começo do while

        # Tokens com so um simbolo (operadores, pontuação)
        # Verifica se o caractere atual pertence ao mapa de tokens
        if char in TOKEN_MAP:
            # Se sim, coloca o token na lista
            tokens.append((TOKEN_MAP[char], char, linha, coluna))
            i += 1          # vai pro próximo caractere
            coluna += 1
            continue        # volta pro começo do while
        
        # Identificadpres (variáveis)
        # ID começa com uma letra
        if char.isalpha():
            lexema = char   # Armazena o primeiro caractere
            coluna_inicio = coluna
            i += 1
            coluna += 1
            while i < len(codigo_fonte) and (codigo_fonte[i].isalnum() or codigo_fonte[i] == '_'):  # De acprdo com a especificaçao do documento
                lexema += codigo_fonte[i]
                i += 1
                coluna += 1
            # Quando o loop acabar, temos o nome completo do id
            tokens.append(('ID', lexema, linha, coluna_inicio))
            continue

        # Numeros Inteiros
        # Numero começa com um digit
        if char.isdigit():
            lexema = char   # Guarda o primeiro dígito
            coluna_inicio = coluna
            i += 1
            coluna += 1
            # Continua lendo enquanto for dígito
            while i < len(codigo_fonte) and codigo_fonte[i].isdigit():
                lexema += codigo_fonte[i]
                i += 1
                coluna += 1
            # Converte o resultado para int
            tokens.append(('NUMERO_INT', int(lexema), linha, coluna_inicio))
            continue
            
        # Strings
        # String começa com aspas duplas "
        if char == '"':
            lexema = ''
            coluna_inicio = coluna
            i += 1      # Pula a aspa inicial
            coluna += 1
            # Lê os caracteres, até a ultima aspa dupla
            while i < len(codigo_fonte) and codigo_fonte[i] != '"':
                # String nao deve ter quebra de linha (peguei o regex disso dos slides)
                if codigo_fonte[i] == '\n':
                    print(f"Erro Léxico: String não pode conter quebra de linha (erro na linha {linha}).", file=sys.stderr)
                    lexema = None
                    sucesso = False
                    break
                lexema += codigo_fonte[i]
                i += 1
                coluna += 1

            if not sucesso: break
            
            # Erro chamado no caso de não encontrar a " que fecha a string
            if i == len(codigo_fonte):
                print(f"Erro Léxico: String iniciada na linha {linha} coluna {coluna_inicio} não foi fechada.", file=sys.stderr)
                sucesso = False
                break

            i += 1      # Pula a aspa final
            coluna += 1
            tokens.append(('STRING_LITERAL', lexema, linha, coluna_inicio))
            continue

        # O caractere não se encaixa em nenhuma das regras acima. Erro
        print(f"Erro Léxico: Caractere inesperado '{char}' na linha {linha}, coluna {coluna}.", file=sys.stderr)
        sucesso = False
        i += 1
        coluna += 1

    return tokens, sucesso

# --- Execução do Analisador ---
if __name__ == "__main__":                          #   O nome do arquivo a ser analisado vai ser inserido na chamada do programa
    if len(sys.argv) != 2:                          #   Que nem em compiladores normais
        print("Uso correto: python analisador.py <nome_do_arquivo.emoji>")
        sys.exit(1)
        
    nome_arquivo_entrada = sys.argv[1]              # Pega o primeiro argumento da chamada do programa
    
    if not nome_arquivo_entrada.endswith(".emoji"): # Valida extensão
        print("Erro: O arquivo de entrada deve ter a extensão .emoji")
        sys.exit(1)

    try:
        # Tenta abrir e ler o arquivo inserido
        # O 'with' garante que o arquivo é fechado mesmo se der erro
        # O encoding tem que ser 'utf-8' para ler os emojis
        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as f:
            codigo = f.read()
            
        # Chamamos a função de analisar a string do codigo
        lista_de_tokens, analise_ok = analisar(codigo)
        
        # Gera o arquivo de saída apenas se a analise deu certo
        if analise_ok and lista_de_tokens:
            # Cria o nome do arquivo de saida, trocando a extensão
            base_name = os.path.splitext(nome_arquivo_entrada)[0]   # Pega o nome do arquivo sem a extensão
            nome_arquivo_saida = base_name + ".emojilex"
            
            # Abre o arquivo de saída em modo de escrita ('w')
            with open(nome_arquivo_saida, 'w', encoding='utf-8') as f_out:
                f_out.write("-" * 50 + "\n")
                f_out.write("ANÁLISE LÉXICA CONCLUÍDA - TOKENS GERADOS\n")
                f_out.write("-" * 50 + "\n")
                # Itera sobre a lista de tokens e escreve cada um no arquivo
                for token in lista_de_tokens:
                    tipo, valor, linha, col = token
                    f_out.write(f"[{tipo}, '{valor}', L:{linha}, C:{col}]\n")
                f_out.write("-" * 50 + "\n")
            
            print(f"Análise concluída com sucesso. Tokens salvos em '{nome_arquivo_saida}'")
        elif not analise_ok:
            print("\nAnálise léxica falhou devido a erros. Nenhum arquivo de saída foi gerado.", file=sys.stderr)
        else:
            print("Nenhum token foi encontrado no arquivo.")

    # Se o arquivo não for encontrado, erro
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo_entrada}' não encontrado.")
        sys.exit(1)