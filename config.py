import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base para la aplicación."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "clave_secreta_redhuall")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or f"sqlite:///{os.path.join(BASE_DIR, 'tienda.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        """Inicialización de la aplicación (logs, extensiones, etc.)."""
        import logging
        from logging.handlers import RotatingFileHandler
        if not app.debug:
            handler = RotatingFileHandler("error.log", maxBytes=10000, backupCount=1)
            handler.setLevel(logging.WARNING)
            app.logger.addHandler(handler)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}