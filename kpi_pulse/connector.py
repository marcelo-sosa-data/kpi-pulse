"""
Manejo de la conexión a la base de datos.
Las credenciales siempre desde variables de entorno, no hardcodeadas.
"""
import os
from sqlalchemy import create_engine, text


class DBConnector:
    def __init__(self, config: dict):
        self.engine = self._build_engine(config)

    def _build_engine(self, config: dict):
        db_type = config.get("type", "postgresql")
        host = config.get("host", "localhost")
        port = config.get("port", 5432)
        dbname = config.get("dbname")
        user = config.get("user")
        # primero busca en env, si no usa lo del yaml
        password = os.environ.get("DB_PASSWORD", config.get("password", ""))

        urls = {
            "sqlite": f"sqlite:///{dbname}",
            "mysql": f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}",
            "postgresql": f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}",
        }
        return create_engine(urls.get(db_type, urls["postgresql"]))

    def run_query(self, query: str):
        """Ejecuta la query y devuelve el primer valor escalar."""
        with self.engine.connect() as conn:
            row = conn.execute(text(query)).fetchone()
            return row[0] if row else None

    def test_connection(self) -> bool:
        """Verifica la conexión antes de correr los checks."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"  Error de conexión: {e}")
            return False
