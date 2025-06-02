import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_machine_learning")

class config:
    JWT_SECRET_KEY = "MINHAPRIMEIRAAPIMACHINELEARNING"
    JWT_ALGORITHM = "HS256"
    JWT_EXP_DELTA_SECONDS = 3600
    CACHE_TYPE = 'simple'
    SWAGGER = {
        'title': 'API - Informações da Embrapa',
        'uiversion': 3
    }
    SQLALCHEMY_DATABASE_URI = 'sqlite:///embrapa.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_HEADLESS = True
    

