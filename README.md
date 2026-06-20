# Serverless Products API — Azure

API REST serverless para gerenciamento de produtos, construída com **Azure Functions** (modelo V1) e **Azure Cosmos DB**.

## Stack

| Componente | Serviço |
|---|---|
| Compute | Azure Functions (Python 3.11, Consumption Plan, modelo V1) |
| Banco NoSQL | Azure Cosmos DB (API NoSQL, modo Serverless) |
| Observabilidade | Application Insights + Azure Monitor |

## Arquitetura
Postman / Cliente HTTP

│

▼

Azure Functions (HTTP Trigger)

├── ProdutoRoot   → GET, POST              /api/produtos

└── ProdutoItem   → GET, PUT, PATCH, DELETE /api/produtos/{id}

│

▼

Azure Cosmos DB (NoSQL)

│

└── Application Insights (logs, falhas, performance)

└── Azure Monitor (alertas)

## Endpoints

| Método | Rota | Descrição | Status |
|---|---|---|---|
| POST | /produtos | Criar produto | 201 |
| GET | /produtos | Listar todos | 200 |
| GET | /produtos/{id} | Consultar por ID | 200 / 404 |
| PUT | /produtos/{id} | Atualizar completamente | 200 / 404 |
| PATCH | /produtos/{id} | Atualizar parcialmente | 200 / 404 |
| DELETE | /produtos/{id} | Excluir | 200 / 404 |

## Estrutura do projeto
serverless-products-api/

├── projeto3-azure/

│   ├── ProdutoRoot/        # GET, POST /produtos

│   ├── ProdutoItem/        # GET, PUT, PATCH, DELETE /produtos/{id}

│   ├── shared_code/        # Cliente Cosmos DB e helpers

│   ├── host.json

│   └── requirements.txt

├── infra/

│   └── variaveis.sh        # Nomes dos recursos (sem segredos)

├── postman/

│   └── produtos-api-collection.json

├── evidencias/             # Prints de testes, banco, logs, dashboard, alertas

└── README.md

## Pré-requisitos

- Azure CLI (`az version`)
- Azure Functions Core Tools v4 (`func --version`)
- Python 3.11

## Como reproduzir

### 1. Clonar e configurar variáveis

```bash
git clone https://github.com/SEU_USUARIO/serverless-products-api.git
cd serverless-products-api
```

### 2. Provisionar a infraestrutura

```bash
export LOCATION=brazilsouth
export SUFIXO=$(openssl rand -hex 3)
export RG="rg-projeto3-produtos-$SUFIXO"
export STORAGE="stp3$SUFIXO"
export FUNC="func-p3-produtos-$SUFIXO"
export COSMOS="cosmosp3$SUFIXO"
export DB_NAME="dbprodutos"
export CONTAINER_NAME="produtos"
export APPINSIGHTS="appi-p3-produtos-$SUFIXO"

az group create --name "$RG" --location "$LOCATION"
az storage account create --name "$STORAGE" --resource-group "$RG" --location "$LOCATION" --sku Standard_LRS
az cosmosdb create --name "$COSMOS" --resource-group "$RG" --locations regionName="$LOCATION" failoverPriority=0 --capabilities EnableServerless
az cosmosdb sql database create --account-name "$COSMOS" --resource-group "$RG" --name "$DB_NAME"
az cosmosdb sql container create --account-name "$COSMOS" --resource-group "$RG" --database-name "$DB_NAME" --name "$CONTAINER_NAME" --partition-key-path //id
az monitor app-insights component create --app "$APPINSIGHTS" --location "$LOCATION" --resource-group "$RG" --application-type web
az functionapp create --resource-group "$RG" --consumption-plan-location "$LOCATION" --runtime python --runtime-version 3.11 --functions-version 4 --name "$FUNC" --storage-account "$STORAGE" --os-type Linux
```

### 3. Configurar variáveis da Function App

```bash
export COSMOS_CONN=$(az cosmosdb keys list --name "$COSMOS" --resource-group "$RG" --type connection-strings --query "connectionStrings[0].connectionString" -o tsv)
export APPINSIGHTS_CONN=$(az monitor app-insights component show --app "$APPINSIGHTS" --resource-group "$RG" --query "connectionString" -o tsv)

az functionapp config appsettings set --resource-group "$RG" --name "$FUNC" --settings \
  COSMOS_CONNECTION_STRING="$COSMOS_CONN" \
  COSMOS_DATABASE="$DB_NAME" \
  COSMOS_CONTAINER="$CONTAINER_NAME" \
  APPLICATIONINSIGHTS_CONNECTION_STRING="$APPINSIGHTS_CONN" \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true \
  ENABLE_ORYX_BUILD=true
```

### 4. Publicar o código

```bash
cd projeto3-azure
func azure functionapp publish "$FUNC" --python
cd ..
```

> **Importante:** use `func azure functionapp publish` (Azure Functions Core Tools), não `az functionapp deployment source config-zip`. Este último não sincroniza os triggers automaticamente em alguns cenários, fazendo com que as funções não apareçam mesmo após um deploy "bem-sucedido".

### 5. Testar

```bash
export HOST_KEY=$(az functionapp keys list --resource-group "$RG" --name "$FUNC" --query "functionKeys.default" -o tsv)
export AZURE_BASE_URL="https://$FUNC.azurewebsites.net/api"

curl -s -X POST "$AZURE_BASE_URL/produtos" \
  -H "Content-Type: application/json" \
  -H "x-functions-key: $HOST_KEY" \
  -d '{"nome":"Mouse","descricao":"Mouse USB","categoria":"Perifericos","preco":89.90,"estoque":10,"ativo":true}'
```

## Postman Collection

Importe `postman/produtos-api-collection.json` e configure:
- `baseUrl`: URL da sua Function App
- `functionKey`: chave obtida via `az functionapp keys list`

## Monitoramento

- **Logs e execuções:** Application Insights → Logs (KQL) ou Performance
- **Alertas configurados:**
  - `alerta-api-produtos-falhas` — disparado quando há falhas nas requisições
  - `alerta-api-produtos-latencia` — disparado quando a latência média excede 2 segundos

## Limpeza de recursos

```bash
source infra/variaveis.sh
az group delete --name "$RG" --yes --no-wait
```

## Projeto acadêmico

Desenvolvido como Projeto 3 da disciplina de Computação em Nuvem, seguindo o Roteiro Detalhado fornecido em aula. Implementação completa na Azure, com CRUD funcional, segurança via Function Key, observabilidade via Application Insights e alertas configurados no Azure Monitor.
