
with open('sql.txt', 'a+') as f:
    """for i in range(8,254):
        f.write('INSERT ' + 'INTO ' + 'STUDENT ' + 'VALUES ' + f'({i}, 100,' + '\'suc\');\n')"""
    for i in range(6,9):
        f.write('SELECT '+ f'* FROM STUDENT WHERE STUDENT.ID= {i};')
    f.close()
