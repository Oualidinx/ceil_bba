class Config:
    SECRET_KEY = '43be06758c598379d184b0dccfa1968cd5444c608c7cb8dfb4298dcf56febd75'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    @staticmethod
    def init_app():
        pass

class Development(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1091eb5a6c62@localhost/ceil_bba"

class Testing(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

class Production(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    credentials = dict(
        driver ="mysql",# pilote de la base de données ,  mysql ou bien postgresql
        database_name = "" ,#Nom de la base de donnée,
        host = "",
        password ="",# mot de passe de la base de données,
        user = "")
    SQLALCHEMY_DATABASE_URI = "{driver}://{user}:{password}@{host}/{database_name}".format(**credentials)

config = {
    "dev": Development,
    'prod':Production,
    'test':Testing
}
