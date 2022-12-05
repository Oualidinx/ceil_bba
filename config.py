class Config:
    SECRET_KEY = '43be06758c598379d184b0dccfa1968cd5444c608c7cb8dfb4298dcf56febd75'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    @staticmethod
    def init_app():
        pass

class Development(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1091eb5a6c62@localhost/ceil_bba"


class Testing(Config):
    SQLALCHEMY_DATABASE_URI="sqlite:///database.db"

config = {
    "dev": Development,
    'test': Testing
}
