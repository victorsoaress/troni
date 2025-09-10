# ingest_data.py
import os
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from llama_index.core import SimpleDirectoryReader
from embeddings_utils import create_embedding
from qdrant_singleton import QdrantSingleton
import uuid

qdrant = QdrantSingleton()

DATA_CONFIG_FILE = "data_config.json"
EMBEDDING_DIM = 3072

class Command(BaseCommand):
    help = "Ingesta dados para Qdrant usando embeddings próprios"

    def handle(self, *args, **options):
        # --- Ler configuração ---
        with open(DATA_CONFIG_FILE, "r", encoding="utf-8") as f:
            data_config = json.load(f)

        for categoria, arquivos in data_config.items():
            print(f"Ingestando categoria: {categoria}")
            collection_name = qdrant.ensure_collection(categoria)

            all_points = []
            for arquivo in arquivos:
                path = Path(arquivo)
                if not path.exists():
                    print(f"Arquivo não encontrado: {arquivo}")
                    continue

                # --- Ler documentos da pasta ou arquivo ---
                reader = SimpleDirectoryReader(input_dir=str(path.parent), recursive=False)
                nodes = reader.load_data()

                for idx, node in enumerate(nodes):
                    embedding = create_embedding(node.text)
                    point_id = str(uuid.uuid4())  # UUID para Qdrant
                    all_points.append({
                        "id": point_id,
                        "vector": embedding,
                        "payload": {
                            "text": node.text,
                            "source": str(path.name)
                        }
                    })

            if all_points:
                qdrant.upsert_points(categoria, all_points)
                print(f"{len(all_points)} pontos inseridos na coleção {collection_name}")
            else:
                print(f"Nenhum ponto inserido para {categoria}")

        print("Ingest completo!")
