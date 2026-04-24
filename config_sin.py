import os
from dotenv import load_dotenv

load_dotenv()

class SinConfig:
    """Configuración para la comunicación con el SIN."""

    NIT = os.environ.get("SIN_NIT", "123456789")
    RAZON_SOCIAL = os.environ.get("SIN_RAZON_SOCIAL", "REDHUALL SURTIDORES")
    SUCURSAL = int(os.environ.get("SIN_SUCURSAL", 0))
    PUNTO_VENTA = int(os.environ.get("SIN_PUNTO_VENTA", 1))
    USUARIO = os.environ.get("SIN_USUARIO", "usuario_prueba")
    PASSWORD = os.environ.get("SIN_PASSWORD", "clave_prueba")
    CERTIFICADO = os.environ.get("SIN_CERTIFICADO", "certs/certificado.pem")

    @staticmethod
    def init_app(app):
        """Inicialización de la aplicación (si se requiere)."""
        pass

    @classmethod
    def as_dict(cls):
        """Devuelve la configuración como diccionario."""
        return {
            "nit": cls.NIT,
            "razon_social": cls.RAZON_SOCIAL,
            "sucursal": cls.SUCURSAL,
            "punto_venta": cls.PUNTO_VENTA,
            "usuario": cls.USUARIO,
            "password": cls.PASSWORD,
            "certificado": cls.CERTIFICADO,
        }