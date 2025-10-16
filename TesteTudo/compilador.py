import sys
import os

# Importa a função de análise do seu analisador léxico
# (Certifique-se que o nome do arquivo é analise_lexica.py)
from analise_lexica import analisar as analisar_lexicamente

# Importa a função e as classes do seu novo analisador sintático
from AnalisadorSintatico import analisar_sintaticamente, print_tree, TreeNode

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
            
        print("Análise léxica concluída com sucesso. Tokens gerados:")
        for token in tokens:
            print(f"  > Tipo: {token[0]}, Valor: '{token[1]}', Linha: {token[2]}")
        
        # --- FASE 2: Análise Sintática ---
        print("\n--- Fase 2: Análise Sintática ---")
        
        # O analisador sintático precisa de uma lista de dicionários,
        # então vamos converter a lista de tuplas do léxico.
        tokens_formatados = [
            {'tipo': t[0], 'valor': t[1], 'linha': t[2]} for t in tokens
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