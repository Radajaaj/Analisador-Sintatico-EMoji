from compilador import analisar_lexicamente # Seu arquivo de compilador parte 1
from AnalisadorSintatico import analisar_sintaticamente # Seu parser
from semantico import AnalisadorSemantico

# Código de teste simples (sem IF/WHILE ainda)
codigo = """
🔢 a;
🔤 b;
a 🎁 10;
b 🎁 "Ola";
a 🎁 "Erro de Tipo Aqui";
c 🎁 20; 
"""

print("--- 1. LÉXICO ---")
tokens, _ = analisar_lexicamente(codigo)
tokens_fmt = [{'tipo': t[0], 'valor': t[1], 'linha': t[2], 'coluna': t[3]} for t in tokens]

print("--- 2. SINTÁTICO ---")
arvore = analisar_sintaticamente(tokens_fmt)

if arvore:
    print("--- 3. SEMÂNTICO E GERAÇÃO DE CÓDIGO ---")
    semantico = AnalisadorSemantico()
    semantico.visitar(arvore)