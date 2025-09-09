# qdrant_singleton.py
import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, NamedVector


QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
EMBEDDING_DIM = 3072

CATEGORIAS = [
    "horarios","info_gerais","laboratorios","colegiado","nde",
    "empresa_junior","inscricao_periodica","premios","professores",
    "requerimento_eletronico","atividade_complementar","ppc"
]

class QdrantSingleton:
    _instance = None
    _collections_initialized = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantSingleton, cls).__new__(cls)
            cls._instance.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        return cls._instance

    def get_collection_name(self, categoria: str):
        return f"ufsj_{categoria}"

    def ensure_collection(self, categoria: str):
        col_name = self.get_collection_name(categoria)
        if col_name not in self._collections_initialized:
            try:
                self.client.recreate_collection(
                    collection_name=col_name,
                    vectors_config={
                        "text-dense": VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
                    }
                )
                self._collections_initialized.append(col_name)
            except Exception as e:
                print(f"Erro criando coleção {col_name}: {e}")
        return col_name

    def search(self, categoria: str, vector: list, limit: int = 10):
        col_name = self.get_collection_name(categoria)
        vector = NamedVector(name="text-dense", vector=vector)

        return self.client.search(
            collection_name=col_name,
            query_vector=vector, 
            limit=limit,
            with_payload=True
        )

    def upsert_points(self, categoria: str, points: list):
        """
        points: lista de dicts do tipo:
        {
            "id": str ou int ou uuid.UUID,
            "vector": embedding,
            "payload": {...}
        }
        """
        col_name = self.ensure_collection(categoria)
        formatted_points = []
        for p in points:
            # garante que o ID seja válido (str ou UUID)
            point_id = p.get("id")
            if point_id is None:
                point_id = str(uuid.uuid4())
            formatted_points.append({
                "id": point_id,
                "vector": {"text-dense": p["vector"]},
                "payload": p.get("payload", {})
            })
        self.client.upsert(collection_name=col_name, points=formatted_points)
