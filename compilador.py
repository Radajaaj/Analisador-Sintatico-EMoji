import sys
import os

# Importa os módulos
from analise_lexica import analisar as analisar_lexicamente
from AnalisadorSintatico import analisar_sintaticamente, print_tree
# Importa o novo módulo semântico
from semantico import AnalisadorSemantico

def salvar_arquivo(conteudo, nome_original, extensao):
    base = os.path.splitext(nome_original)[0]
    nome_saida = base + extensao
    try:
        with open(nome_saida, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"Arquivo gerado: {nome_saida}")
    except Exception as e:
        print(f"Erro ao salvar {extensao}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python compilador.py <arquivo_fonte.emoji>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        sys.exit(1)

    print(f"Compilando: {caminho_arquivo}\n")

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo_fonte = f.read()

        # Léxico
        print("1. Análise Léxica")
        tokens, sucesso_lexico = analisar_lexicamente(codigo_fonte)
        
        if not sucesso_lexico:
            print("❌ Falha na Análise Léxica.")
            sys.exit(1)
        
        # Salva tokens (opcional)
        lex_content = "\n".join([str(t) for t in tokens])
        salvar_arquivo(lex_content, caminho_arquivo, ".emojilex")

        # Sintático
        print("\n2. Análise Sintática")
        tokens_fmt = [{'tipo': t[0], 'valor': t[1], 'linha': t[2], 'coluna': t[3]} for t in tokens]
        arvore = analisar_sintaticamente(tokens_fmt)
        
        if not arvore:
            print("❌ Falha na Análise Sintática.")
            sys.exit(1)
        
        print("✅ Sintaxe Correta!")

        # Semântico e Geração de Código
        print("\n3. Análise Semântica e Geração de Código")
        analisador = AnalisadorSemantico()
        sucesso_semantico = analisador.visitar(arvore)

        if sucesso_semantico:
            print("✅ Semântica Correta!")
            codigo_tac = analisador.gerador.obter_codigo()
            print("\n" + codigo_tac)
            salvar_arquivo(codigo_tac, caminho_arquivo, ".tac")
            print("\n🎉 COMPILAÇÃO CONCLUÍDA COM SUCESSO! 🎉")
        else:
            print(f"\n❌ Falha na Semântica ({len(analisador.erros)} erros encontrados).")
            for erro in analisador.erros:
                print(f"   - {erro}")
            sys.exit(1)

    except Exception as e:
        print(f"Erro inesperado no compilador: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()