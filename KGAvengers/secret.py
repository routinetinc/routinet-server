class LocalDB:
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'USER': 'postgres',
        'PASSWORD': '****',
        'NAME': 'KGAvengers',
    }   
  } 

class RemoteDB:
  pass