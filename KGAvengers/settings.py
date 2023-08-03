import psycopg2
from pathlib import Path
import os
# from KGAvengers import secret
import secret

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ub1*^9=4k2um)a(#nux@vjy589fw@dlvz32acydetohnach9q-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"] # ワイルドカードを追加


# アプリケーション定義

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",
    "rest_framework.authtoken",
    "routine.apps.RoutineConfig",
    "supplyAuth.apps.SupplyauthConfig",
    'social_django',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2',
]

SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',# ユーザ名、メールアドレスなど詳細情報をkwargsにdetailsとして格納
    'social_core.pipeline.social_auth.social_uid',# 一意識別子のuidをkwargsにuidとして格納
    'supplyAuth.views.get_user',# uidからユーザを取得
    'social_core.pipeline.social_auth.auth_allowed',# 特定のソーシャルプロバイダを通じたユーザーの認証が許可されているかどうかをチェック
    'social_core.pipeline.social_auth.social_user',# 既存のソーシャルユーザーの存在をチェック
    'social_core.pipeline.social_auth.associate_user',# ソーシャルアカウントとDjangoのユーザーアカウントを関連付ける
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'supplyAuth.views.save_profile',# ユーザの新規作成
    'supplyAuth.views.get_user',# uidからユーザを取得
]

SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = secret.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = secret.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'hello'


AUTH_USER_MODEL = "supplyAuth.User" # accountアプリのUserモデルをデフォルトで使用する認証ユーザーモデルとして設定する

""" # APIにアクセス制限を適用する
# 認証方式はアクセストークン
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
} """

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'KGAvengers.middleware_myself.MyCustomMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware', 
]

ROOT_URLCONF = 'KGAvengers.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends', 
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'KGAvengers.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

""" DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
} """

"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '/cloudsql/my-project-test-385602:asia-northeast2:test',
        'USER': 'superuser',
        'PASSWORD': 'postgres',
        'NAME': 'test',
    }   
}  -> secret.RemoteDB.DATABASES に移動 """

DATABASES = secret.LocalDB.DATABASES

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'HOST': 'localhost',
#         'USER': '####',
#         'PASSWORD': '####',
#         'NAME': 'KGAvengers',
#     }   
# } 

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
