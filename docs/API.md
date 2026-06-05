# API Reference - Regenerative Pasture Backend

## Overview

Sistema backend para gerenciamento inteligente de pastagens no Cerrado, integrado com Firebase.

**Base URL**: `https://{region}-{projectId}.cloudfunctions.net`

---

## Endpoints

### 1. Calcular Viabilidade de Pastagem

**Endpoint**: `/calcular_viabilidade_pastagem_http`  
**Method**: `POST`  
**Content-Type**: `application/json`

#### Request

```json
{
  "piquete_id": "string",
  "fazenda_id": "string",
  "estande_pct": 45,
  "custo_hora_trator_reais": 450,
  "custo_sementes_kg_reais": 8.5,
  "quantidade_sementes_kg_ha": 15,
  "area_ha": 50,
  "supervisor_id": "optional_supervisor_id"
}
```

#### Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `piquete_id` | string | ✅ | Identificador único do piquete |
| `fazenda_id` | string | ✅ | Identificador da fazenda |
| `estande_pct` | number | ✅ | Estande atual (0-100%) |
| `custo_hora_trator_reais` | number | ✅ | Custo horário (R$) |
| `custo_sementes_kg_reais` | number | ✅ | Custo por kg (R$) |
| `quantidade_sementes_kg_ha` | number | ✅ | Quantidade (kg/ha) |
| `area_ha` | number | ✅ | Área total (hectares) |
| `supervisor_id` | string | ❌ | ID do supervisor |

#### Response (Success 200)

```json
{
  "status": "success",
  "data": {
    "tipo_intervencao": "Recuperacao",
    "justificativa": "Estande de 45%...",
    "custo_operacional_reais": 18750.00,
    "producao_estimada_kg_ms_ha": 4500,
    "ua_ha_estimada": 1.85,
    "roi_estimado_pct": 125.3,
    "validade_dias": 180,
    "data_proxima_reaval": "2026-12-05T14:32:00Z"
  }
}
```

#### Response Fields

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `tipo_intervencao` | string | `Recuperacao`, `Reforma` ou `Manutencao` |
| `justificativa` | string | Explicação técnica da recomendação |
| `custo_operacional_reais` | number | Custo total estimado (R$) |
| `producao_estimada_kg_ms_ha` | number | Produção de matéria seca (kg/ha) |
| `ua_ha_estimada` | number | Unidades Animais por hectare |
| `roi_estimado_pct` | number | Retorno sobre investimento (%) |
| `validade_dias` | number | Dias até próxima reavaliação |
| `data_proxima_reaval` | string | Data recomendada para reavaliação |

#### Error Responses

**400 - Bad Request**
```json
{
  "status": "error",
  "message": "Campo obrigatório ausente: area_ha"
}
```

**500 - Internal Server Error**
```json
{
  "status": "error",
  "message": "Erro interno: {error_details}"
}
```

---

### 2. Estimar Lotação e Suporte

**Endpoint**: `/estimar_lotacao_suporte_http`  
**Method**: `POST`  
**Content-Type**: `application/json`

#### Request

```json
{
  "piquete_id": "string",
  "fazenda_id": "string",
  "ndvi_valor": 0.72,
  "tipo_forrageira": "Brachiaria brizantha cv. Marandu",
  "area_ha": 50,
  "dados_solo_laudo_id": "optional_laudo_id"
}
```

#### Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `piquete_id` | string | ✅ | Identificador único do piquete |
| `fazenda_id` | string | ✅ | Identificador da fazenda |
| `ndvi_valor` | number | ✅ | Índice de vegetação (-1 a 1) |
| `tipo_forrageira` | string | ✅ | Tipo de forrageira (veja lista) |
| `area_ha` | number | ✅ | Área total (hectares) |
| `dados_solo_laudo_id` | string | ❌ | ID do laudo de solo |

#### Forrageiras Suportadas

| Nome | Descrição |
|------|-----------|
| `Brachiaria decumbens` | Braquiária Decumbens |
| `Brachiaria brizantha cv. Marandu` | Braquiária Marandu |
| `Panicum maximum cv. Mombaça` | Capim Mombaça |
| `Cynodon dactylon` | Grama Bermuda |

#### Response (Success 200)

```json
{
  "status": "success",
  "data": {
    "ua_ha_recomendada": 1.850,
    "ua_total": 92.50,
    "biomassa_disponivel_kg_ms": 175000,
    "biomassa_disponivel_kg_ms_ha": 3500,
    "indice_vegetacao_ndvi": 0.720,
    "classificacao_vigor": "Bom",
    "fator_ajuste_solo": 0.95,
    "lotacao_maxima_segura_ua_ha": 2.090,
    "dias_repouso_recomendado": 28,
    "alerta": null
  }
}
```

#### Response Fields

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ua_ha_recomendada` | number | Lotação recomendada (UA/ha) |
| `ua_total` | number | Total de UAs disponíveis |
| `biomassa_disponivel_kg_ms` | number | Biomassa total (kg MS) |
| `biomassa_disponivel_kg_ms_ha` | number | Biomassa por hectare (kg MS/ha) |
| `indice_vegetacao_ndvi` | number | NDVI utilizado |
| `classificacao_vigor` | string | `Crítico`, `Pobre`, `Regular`, `Bom`, `Excelente` |
| `fator_ajuste_solo` | number | Fator de ajuste baseado em análise de solo |
| `lotacao_maxima_segura_ua_ha` | number | Lotação máxima segura (UA/ha) |
| `dias_repouso_recomendado` | number | Dias de repouso sugerido |
| `alerta` | string ou null | Alerta se houver (null se sem alertas) |

---

## NDVI Classification

| Faixa | Classificação | Ação |
|------|---------------|------|
| < 0.30 | Crítico | ⚠️ Intervenção urgente |
| 0.30-0.45 | Pobre | ⚠️ Adiamento de entrada de animais |
| 0.45-0.60 | Regular | Monitorar consumo |
| 0.60-0.75 | Bom | Operação normal |
| > 0.75 | Excelente | ✅ Máxima produção |

---

## Exemplos de Uso

### cURL

```bash
# Calcular viabilidade
curl -X POST https://us-central1-regenerative-pasture.cloudfunctions.net/calcular_viabilidade_pastagem_http \
  -H "Content-Type: application/json" \
  -d '{
    "piquete_id": "piquete_001",
    "fazenda_id": "fazenda_001",
    "estande_pct": 45,
    "custo_hora_trator_reais": 450,
    "custo_sementes_kg_reais": 8.5,
    "quantidade_sementes_kg_ha": 15,
    "area_ha": 50
  }'

# Estimar lotação
curl -X POST https://us-central1-regenerative-pasture.cloudfunctions.net/estimar_lotacao_suporte_http \
  -H "Content-Type: application/json" \
  -d '{
    "piquete_id": "piquete_001",
    "fazenda_id": "fazenda_001",
    "ndvi_valor": 0.72,
    "tipo_forrageira": "Brachiaria brizantha cv. Marandu",
    "area_ha": 50
  }'
```

### Python

```python
from client_python import RegenerativePastureClient

client = RegenerativePastureClient(project_id='regenerative-pasture')

# Calcular viabilidade
result = client.calcular_viabilidade_pastagem(
    piquete_id='piquete_001',
    fazenda_id='fazenda_001',
    estande_pct=45,
    area_ha=50
)

print(f"Tipo: {result['data']['tipo_intervencao']}")
print(f"Custo: R$ {result['data']['custo_operacional_reais']:.2f}")

# Estimar lotação
result = client.estimar_lotacao_suporte(
    piquete_id='piquete_001',
    fazenda_id='fazenda_001',
    ndvi_valor=0.72,
    tipo_forrageira='Brachiaria brizantha cv. Marandu',
    area_ha=50
)

print(f"UA/ha: {result['data']['ua_ha_recomendada']:.2f}")
print(f"Vigor: {result['data']['classificacao_vigor']}")
```

---

## Status Codes

| Código | Descrição |
|--------|-----------|
| `200` | Sucesso |
| `400` | Requisição inválida (validação falhou) |
| `500` | Erro interno do servidor |

---

## Firestore Collections

### Users
```
users/{userId}
├── email: string
├── role: 'Pecuarista' | 'Supervisor_Tecnico'
├── fazendas: string[]
└── fazendas_atribuidas: string[]
```

### Farms
```
fazendas/{fazendaId}
├── nome: string
├── proprietario_id: string
├── supervisores: string[]
└── agregados: {custo_mes, ua_total, status, ...}
```

### Plots
```
fazendas/{fazendaId}/piquetes/{piqueteId}
├── nome: string
├── estande_atual_pct: number
├── ndvi_ultima_leitura: number
├── ua_ha_recomendada: number
└── status_sanitario: string
```

### Recommendations
```
fazendas/{fazendaId}/historico_recomendacoes/{recomendacaoId}
├── tipo_intervencao: string
├── resultado_calculo: {...}
├── status_implementacao: string
└── data_geracao: timestamp
```

---

## Rate Limiting

Sem limite explícito definido. Sujeito às quotas do Firebase:
- **Cloud Functions**: 540.000 invocações/mês (Spark), 2M/mês (Blaze)
- **Firestore**: 50.000 leituras/dia (Spark)

---

## Autenticação

Utilize Firebase Authentication com tokens JWT. Passe via header:
```
Authorization: Bearer <ID_TOKEN>
```

---

## Support

Para questões, abra uma issue no repositório:
https://github.com/lab869-cmd/regenerative-pasture-backend/issues
