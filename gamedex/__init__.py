# __init__.py: avisa o Python que a pasta gamedex é um "pacote", aí dá pra importar coisas
# dela pelo nome, tipo o 'gamedex.settings' e o 'gamedex.urls' que aparecem no projeto.
# Como ele roda antes de tudo (no manage.py e no servidor), é o lugar certo pro ajuste do PyMySQL abaixo.

# O Django conecta no MySQL procurando uma biblioteca chamada "MySQLdb" (que é o mysqlclient).
# O mysqlclient às vezes precisa de compilador pra instalar, principalmente no Windows.
# Por isso usei o PyMySQL, que é feito só em Python e instala sem dor de cabeça.
# O install_as_MySQLdb() registra o PyMySQL com o nome "MySQLdb", aí o Django usa ele sem perceber a troca.
# (Se voltar pro SQLite, pode deixar essas linhas: elas não atrapalham.)
import pymysql

pymysql.install_as_MySQLdb()
