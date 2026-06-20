import os
import json
import uuid
import datetime
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions

COSMOS_CONNECTION_STRING = os.environ["COSMOS_CONNECTION_STRING"]
COSMOS_DATABASE = os.environ["COSMOS_DATABASE"]
COSMOS_CONTAINER = os.environ["COSMOS_CONTAINER"]

client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
database = client.get_database_client(COSMOS_DATABASE)
container = database.get_container_client(COSMOS_CONTAINER)


def agora_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def resposta(body, status_code=200):
    return func.HttpResponse(
        json.dumps(body, ensure_ascii=False),
        status_code=status_code,
        mimetype="application/json"
    )


def resposta_erro(mensagem, status_code):
    return resposta({"erro": mensagem}, status_code)


def gerar_id():
    return str(uuid.uuid4())


def validar_produto(dados):
    campos = ["nome", "categoria", "preco"]
    for campo in campos:
        if campo not in dados:
            return f"Campo obrigatório ausente: {campo}"
    return None


def ler_json(req):
    try:
        return req.get_json()
    except ValueError:
        return None


def buscar_por_id(produto_id):
    try:
        return container.read_item(item=produto_id, partition_key=produto_id)
    except exceptions.CosmosResourceNotFoundError:
        return None
