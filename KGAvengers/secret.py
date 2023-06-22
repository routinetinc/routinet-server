class LocalDB:
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'USER': '####',
        'PASSWORD': '####',
        'NAME': 'KGAvengers',
    }   
  } 

class RemoteDB:
  pass