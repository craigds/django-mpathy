from __future__ import print_function, unicode_literals
import os

import django


def pytest_configure():
    from django.conf import settings

    # Best-guess the db user name
    db_user = os.environ.get('PGUSER')
    if not db_user:
        # On MacOS, brew installs postgres with the superuser account called $USER
        db_user = os.environ.get('USER')
        if os.environ.get('CI'):
            # On travis superuser is called postgres
            db_user = 'postgres'

    if not db_user:
        db_user = 'postgres'

    print(f"pytest_configure - using db user: {db_user}")

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'mpathy_tests',
                'USER': db_user,
                'PASSWORD': '',
                'HOST': 'localhost',
                'TEST': {'NAME': 'mpathy_tests',},
            }
        },
        SECRET_KEY='hunter2',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
            },
        ],
        MIDDLEWARE=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=('mpathy', 'tests',),
    )
    django.setup()
