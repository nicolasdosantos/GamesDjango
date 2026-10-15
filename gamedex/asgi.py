# asgi.py: porta de entrada do projeto para servidores ASGI (o tipo "assíncrono", que aguenta coisas
# como websockets e conexões que ficam abertas). Este projeto não usa: o runserver usa o wsgi.py.
# Foi criado pelo startproject e fica aí caso um dia precise.

"""
ASGI config for gamedex project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamedex.settings')

application = get_asgi_application()
