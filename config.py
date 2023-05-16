import os
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    @staticmethod
    def init_app():
        pass

class Development(Config):
    SECRET_KEY = '43be06758c598379d184b0dccfa1968cd5444c608c7cb8dfb4298dcf56febd75'
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1091eb5a6c62@localhost:5432/ceil_bba"

class Testing(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

class Production(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    credentials = dict(
        driver ="mysql+pymysql",# pilote de la base de données ,  mysql ou bien postgresql
        database_name = "ceil_bba" ,#Nom de la base de donnée,
        host = "localhost",
        password =":1091eb5a6c62",# mot de passe de la base de données,
        user = "3306")
    SQLALCHEMY_DATABASE_URI = "{driver}://{user}{password}@{host}/{database_name}".format(**credentials)

class Testing(Config):
    SECRET_KEY = '43be06758c598379d184b0dccfa1968cd5444c608c7cb8dfb4298dcf56febd75'
    SQLALCHEMY_DATABASE_URI="sqlite:///database.db"


config = {
    "dev": Development,
    'prod':Production,
    'test':Testing
}
