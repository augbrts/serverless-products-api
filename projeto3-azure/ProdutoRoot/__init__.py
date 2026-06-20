from shared_code.db import (
    container,
    resposta,
    resposta_erro,
    validar_produto,
    ler_json,
    gerar_id,
    agora_iso
)


def main(req):
    method = req.method.upper()

    if method == "GET":
        itens = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        return resposta({"total": len(itens), "produtos": itens})

    if method == "POST":
        dados = ler_json(req)
        if dados is None:
            return resposta_erro("JSON inválido", 400)

        erro = validar_produto(dados)
        if erro:
            return resposta_erro(erro, 400)

        agora = agora_iso()
        item = {
            "id": dados.get("id") or gerar_id(),
            "nome": dados.get("nome"),
            "descricao": dados.get("descricao", ""),
            "categoria": dados.get("categoria"),
            "preco": dados.get("preco"),
            "estoque": dados.get("estoque", 0),
            "ativo": dados.get("ativo", True),
            "criadoEm": agora,
            "atualizadoEm": agora
        }
        container.create_item(body=item)
        return resposta({"mensagem": "Produto criado com sucesso", "produto": item}, 201)

    return resposta_erro("Método não permitido", 405)
