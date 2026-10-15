#!/usr/bin/env python
# manage.py: é por ele que eu rodo os comandos do Django no terminal. Os que usei no projeto:
#   python manage.py runserver         -> liga o site em http://127.0.0.1:8000/
#   python manage.py makemigrations    -> cria as migrations a partir das mudanças no models.py
#   python manage.py migrate           -> aplica as migrations no banco (cria/altera as tabelas)
#   python manage.py createsuperuser   -> cria o usuário que entra no /admin/
#   python manage.py check             -> procura erros de configuração sem precisar abrir o site
# Ele só avisa ao Django qual settings usar (DJANGO_SETTINGS_MODULE = 'gamedex.settings')
# e passa o comando pra frente. Foi criado pelo startproject e eu não mexi.
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamedex.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
