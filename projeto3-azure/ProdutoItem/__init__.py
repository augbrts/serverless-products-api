from shared_code.db import (
    container,
    resposta,
    resposta_erro,
    validar_produto,
    ler_json,
    buscar_por_id,
    agora_iso
)


def main(req):
    method = req.method.upper()
    produto_id = req.route_params.get("id")

    if not produto_id:
        return resposta_erro("ID do produto não informado", 400)

    produto = buscar_por_id(produto_id)
    if not produto:
        return resposta_erro("Produto não encontrado", 404)

    if method == "GET":
        return resposta(produto)

    if method == "DELETE":
        container.delete_item(item=produto_id, partition_key=produto_id)
        return resposta({"mensagem": "Produto excluído com sucesso", "produto": produto})

    if method in ["PUT", "PATCH"]:
        dados = ler_json(req)
        if dados is None:
            return resposta_erro("JSON inválido", 400)

        if method == "PUT":
            erro = validar_produto(dados)
            if erro:
                return resposta_erro(erro, 400)

        for chave, valor in dados.items():
            if chave not in ["id", "criadoEm"]:
                produto[chave] = valor

        produto["id"] = produto_id
        produto["atualizadoEm"] = agora_iso()
        container.replace_item(item=produto_id, body=produto)
        return resposta({"mensagem": "Produto atualizado com sucesso", "produto": produto})

    return resposta_erro("Método não permitido", 405)
