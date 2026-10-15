# wsgi.py: porta de entrada do projeto para servidores WSGI. WSGI é o padrão de como um servidor web
# conversa com uma aplicação Python. O "application" daqui é o site inteiro empacotado num objeto.
# O runserver usa ele (o settings.py aponta pra cá no WSGI_APPLICATION), e num servidor de verdade
# (tipo gunicorn) também é por aqui que o site começa. Foi criado pelo startproject e eu não mexi.

"""
WSGI config for gamedex project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamedex.settings')

application = get_wsgi_application()
