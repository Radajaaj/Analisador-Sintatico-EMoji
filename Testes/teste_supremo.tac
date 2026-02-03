========================================
 CÓDIGO INTERMEDIÁRIO (TAC)
========================================
    max_iter = '10'
    numero_secreto = '7'
    achou = 0
    mensagem = 'Iniciando o teste supremo...'
    i = '0'
L0:
    t0 = i < max_iter
    if_false t0 goto L1
    t1 = achou == 0
    if_false t1 goto L2
    t2 = i == numero_secreto
    if_false t2 goto L4
    achou = 0
    mensagem = 'O numero foi encontrado com sucesso!'
    goto L5
L4:
L5:
    goto L3
L2:
L3:
    t3 = i + '1'
    i = t3
    goto L0
L1:
========================================