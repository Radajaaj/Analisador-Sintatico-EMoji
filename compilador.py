import sys
import os

# Importa a função de análise do seu analisador léxico
from analise_lexica import analisar as analisar_lexicamente

# Importa a função e as classes do seu novo analisador sintático
from AnalisadorSintatico import analisar_sintaticamente, print_tree, TreeNode

#Função para salvar os tokens em um arquivo .emojilex
def salvar_tokens_em_arquivo(tokens, nome_arquivo_entrada):
    """
    Salva a lista de tokens gerada em um arquivo com extensão .emojilex.
    """
    if not tokens:
        print("Nenhum token foi gerado, arquivo .emojilex não será criado.")
        return

    # Cria o nome do arquivo de saida, trocando a extensão .emoji por .emojilex
    base_name = os.path.splitext(nome_arquivo_entrada)[0]
    nome_arquivo_saida = base_name + ".emojilex"

    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f_out:
            f_out.write("-" * 50 + "\n")
            f_out.write("ANÁLISE LÉXICA CONCLUÍDA - TOKENS GERADOS\n")
            f_out.write("-" * 50 + "\n")
            
            # Itera sobre a lista de tokens (tuplas) e escreve cada um no arquivo
            for token in tokens:
                tipo, valor, linha, col = token
                f_out.write(f"[{tipo}, '{valor}', L:{linha}, C:{col}]\n")
            
            f_out.write("-" * 50 + "\n")
        
        print(f"Resultado da análise léxica salvo em '{nome_arquivo_saida}'")
    except IOError as e:
        print(f"Erro ao salvar o arquivo de tokens: {e}", file=sys.stderr)


def main():
    # Verifica se o nome do arquivo de entrada foi fornecido na linha de comando
    if len(sys.argv) != 2:
        print("Uso: python compilador.py <caminho_para_seu_arquivo.emoji>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]

    # Garante que o arquivo existe e tem a extensão correta
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        sys.exit(1)
    if not caminho_arquivo.endswith(".emoji"):
        print("Erro: O arquivo de entrada deve ter a extensão .emoji")
        sys.exit(1)

    print(f"--- Iniciando compilação do arquivo: {caminho_arquivo} ---\n")

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo_fonte = f.read()

        # --- FASE 1: Análise Léxica ---
        print("--- Fase 1: Análise Léxica ---")
        tokens, sucesso_lexico = analisar_lexicamente(codigo_fonte)
        
        if not sucesso_lexico:
            print("\nErro durante a análise léxica. Compilação abortada.")
            sys.exit(1)
        
        print("Análise léxica concluída com sucesso.")
        
        # Salva o resultado da análise léxica em um arquivo
        salvar_tokens_em_arquivo(tokens, caminho_arquivo)
        
        # --- FASE 2: Análise Sintática ---
        print("\n--- Fase 2: Análise Sintática ---")
        
        # O analisador sintático precisa de uma lista de dicionários,
        # então vamos converter a lista de tuplas do léxico.
        tokens_formatados = [
            {'tipo': t[0], 'valor': t[1], 'linha': t[2], 'coluna': t[3]} for t in tokens
        ]
        
        arvore_sintatica = analisar_sintaticamente(tokens_formatados)
        
        if arvore_sintatica:
            print("\n--- Árvore Sintática Gerada ---")
            print_tree(arvore_sintatica)
            print("\n--- Compilação finalizada com sucesso! ---")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        sys.exit(1)

# Ponto de entrada do programa
if __name__ == "__main__":
    main()