# 🌱 Backend - Inteligência e Gestão Regenerativa de Pastagens (Cerrado)

**Plataforma de Supervisão e Recomendações Agronômicas em Tempo Real**

## 📋 Visão Geral

Sistema backend escalável desenvolvido em **Firebase** para gerenciar a inteligência e gestão regenerativa de pastagens no bioma Cerrado. Fornece recomendações baseadas em dados de solo, índices de vegetação (NDVI) e análises de viabilidade econômica.

### Stack Tecnológico
- **Autenticação**: Firebase Authentication
- **Banco de Dados**: Cloud Firestore (NoSQL, offline-first)
- **Backend/Lógica Negócio**: Cloud Functions (Python 3.11, 2ª Geração)
- **Armazenamento**: Firebase Storage (PDFs de laudos, imagens satelitais)
- **Segurança**: Firestore Security Rules + Storage Rules (RBAC)

---

## 🏗️ Arquitetura

### Coleções Firestore

```
users/                          # Usuários (Pecuarista | Supervisor_Tecnico)
├── {userId}
│   ├── email, role, cpf, phone
│   ├── fazendas[]              # IDs de fazendas (Pecuarista)
│   └── fazendas_atribuidas[]   # IDs atribuídas (Supervisor)

fazendas/                       # Propriedades agrícolas
├── {fazendaId}
│   ├── nome, municipio, estado
│   ├── proprietario_id, supervisores[]
│   ├── area_total_ha, coordenadas_centrais (GeoPoint)
│   ├── metadata (solo, bioma, altitude, precipitação)
│   ├── piquetes/               # Subcoleção de talhões
│   ├── laudos_solo/            # Subcoleção de análises
│   └── historico_recomendacoes/ # Subcoleção de histórico

piquetes/                       # Talhões (demarcação com coordenadas)
├── {piqueteId}
│   ├── nome, fazenda_id, area_ha
│   ├── tipo_forrageira, estande_atual_pct
│   ├── coordenadas[]           # Array de GeoPoints (polygon)
│   ├── ndvi_ultima_leitura, data_ndvi_leitura
│   ├── recomendacao_atual, custo_operacional_estimado_reais
│   ├── ua_ha_recomendada, status_sanitario
│   └── createdAt, updatedAt, deletedAt (soft delete)

laudos_solo/                    # Análises laboratoriais
├── {laudoId}
│   ├── piquete_id, fazenda_id, supervisor_id
│   ├── data_coleta, laboratorio, numero_protocolo_lab
│   ├── url_pdf_storage
│   ├── analise {ph, MO, P, K, Ca, Mg, Al, H, S, CTC, V%, M%, B, Cu, Fe, Zn, Mn, granulometria}
│   └── createdAt, updatedAt

historico_recomendacoes/       # Rastreamento de decisões técnicas
├── {recomendacaoId}
│   ├── piquete_id, fazenda_id, supervisor_id
│   ├── data_geracao, tipo_intervencao (Recuperacao|Reforma|Manutencao)
│   ├── justificativa, estande_gatilho
│   ├── parametros_calculo {estande_pct, custos, NDVI, etc}
│   ├── resultado_calculo {custo_operacional, UA/ha, biomassa, ROI%}
│   ├── status_implementacao (Pendente|Iniciada|Concluida|Rejeitada)
│   └── data_conclusao, notas_campo

logs_auditoria/                # Rastreamento completo de ações
├── {logId}
│   ├── usuario_id, acao, colecao_afetada, documento_id
│   ├── dados_anterior, dados_novo
│   ├── ip_origem, timestamp, resultado (Sucesso|Erro)
```

### Cloud Functions (Python)

#### 1. `calcular_viabilidade_pastagem` (HTTP Callable)
**Lógica de Negócio:**
- Se estande > 50% → **Força Recuperação** (trava de segurança)
- Se 20-50% → Análise custo-benefício (Reforma vs. Manutenção)
- Se < 20% → **Reforma Obrigatória**
- Calcula custo operacional (R$/ha) e ROI estimado (%)

**Entrada:**
```json
{
  "piquete_id": "string",
  "fazenda_id": "string",
  "estande_pct": 45,
  "custo_hora_trator_reais": 450,
  "custo_sementes_kg_reais": 8.5,
  "quantidade_sementes_kg_ha": 15,
  "area_ha": 50
}
```

**Saída:**
```json
{
  "tipo_intervencao": "Reforma",
  "justificativa": "...",
  "custo_operacional_reais": 18750,
  "producao_estimada_kg_ms_ha": 4500,
  "ua_ha_estimada": 1.85,
  "roi_estimado_pct": 125.3,
  "validade_dias": 180,
  "data_proxima_reaval": "2026-12-05T..."
}
```

#### 2. `estimar_lotacao_suporte` (HTTP Callable)
**Lógica de Negócio:**
- Recebe NDVI (índice de vegetação via satélite)
- Estima biomassa disponível
- Integra dados de solo (se laudo disponível)
- Retorna UA/ha recomendada com margem de segurança

**Entrada:**
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

**Saída:**
```json
{
  "ua_ha_recomendada": 1.85,
  "ua_total": 92.5,
  "biomassa_disponivel_kg_ms": 175000,
  "biomassa_disponivel_kg_ms_ha": 3500,
  "indice_vegetacao_ndvi": 0.72,
  "classificacao_vigor": "Bom",
  "fator_ajuste_solo": 0.95,
  "lotacao_maxima_segura_ua_ha": 2.1,
  "dias_repouso_recomendado": 28,
  "alerta": null
}
```

### Security Rules (RBAC)

**Pecuarista:**
- ✅ Lê apenas dados de suas próprias fazendas
- ✅ Cria/edita piquetes em suas fazendas
- ❌ Não pode inserir laudos ou gerar recomendações

**Supervisor_Tecnico:**
- ✅ Lê fazendas onde foi explicitamente atribuído
- ✅ Insere laudos de solo (com assinatura digital)
- ✅ Gera recomendações agronômicas
- ✅ Atualiza status de implementação

---

## 🚀 Deployment

### Pré-requisitos
```bash
# Firebase CLI
npm install -g firebase-tools

# Python 3.11+
python3 --version

# Autenticação Firebase
firebase login
firebase init
```

### Deploy Completo
```bash
# 1. Firestore Rules
firebase deploy --only firestore:rules

# 2. Storage Rules
firebase deploy --only storage

# 3. Cloud Functions (Python)
cd cloud-functions
pip install -r requirements.txt
firebase deploy --only functions
```

### Teste Local (Emulator Suite)
```bash
firebase emulators:start --only firestore,functions,storage
```

---

## 📊 Dados Técnicos do Cerrado (Hardcoded)

### Forrageiras Suportadas
| Espécie | UA/ha (ótimo) | kg MS/ha (máx) | Ciclo (dias) | Tolerância |
|---------|---------------|----------------|--------------|----------|
| Brachiaria decumbens | 1.8 | 5500 | 30 | Média seca |
| B. brizantha Marandu | 2.2 | 6200 | 28 | Alta seca/pisoteio |
| Panicum maximum Mombaça | 2.5 | 7000 | 25 | Ótima palatabilidade |
| Cynodon dactylon (Bermuda) | 2.0 | 5800 | 21 | Muito alta pisoteio |

### Índice NDVI (Classificação de Vigor)
| Faixa NDVI | Classificação | Ação Recomendada |
|-----------|---|---|
| < 0.30 | Crítico | ⚠️ Intervenção urgente |
| 0.30-0.45 | Pobre | Adiamento de entrada |
| 0.45-0.60 | Regular | Monitorar consumo |
| 0.60-0.75 | Bom | Normal |
| > 0.75 | Excelente | Máxima produção |

---

## 🔒 Segurança

### Firestore Rules
- ✅ RBAC por role
- ✅ Isolamento de dados por proprietário/supervisor
- ✅ Soft delete para piquetes (campos deletedAt)
- ✅ Proteção de CPF e dados sensíveis

### Storage Rules
- ✅ Laudos PDF acessíveis apenas para fazer upload/download autorizado
- ✅ Imagens satelitais com controle de permissão

### Auditoria
- ✅ Todos os inserts/updates registrados em `logs_auditoria`
- ✅ Rastreamento de IP e timestamp
- ✅ Histórico completo de modificações

---

## 💡 Próximas Etapas (Roadmap)

### Fase 1: Trigger Functions ✅
- [x] Validação automática de laudos ao upload
- [x] Notificações push quando recomendação gerada
- [x] Cálculo de aggregates (custo total/fazenda/mês)

### Fase 2: Integrações Externas 🔄
- [ ] INMET API (dados agrometeorológicos)
- [ ] Google Earth Engine (NDVI/satélites automático)
- [ ] EMBRAPA (classificação pedológica)

### Fase 3: Machine Learning 🤖
- [ ] Modelo preditivo de degradação
- [ ] Otimização automática de ciclos
- [ ] Previsão de produção por piquete

### Fase 4: Frontend (Web/Mobile) 📱
- [ ] Dashboard com mapas interativos
- [ ] Gráficos série temporal
- [ ] Notificações em tempo real
- [ ] Relatórios PDF automatizados

---

## 📝 Variáveis de Ambiente

Criar `.env` na raiz:
```env
FIREBASE_PROJECT_ID=regenerative-pasture
FIREBASE_STORAGE_BUCKET=regenerative-pasture.appspot.com
PYTHON_VERSION=3.11
ENVIRONMENT=production
```

---

## 📚 Documentação Técnica

- [Firestore Schema](./docs/firestore-schema.md)
- [Cloud Functions API](./docs/cloud-functions-api.md)
- [Security Rules](./docs/security-rules.md)
- [Cálculos Agronômicos](./docs/agro-calculations.md)

---

## 👥 Contribuindo

1. Fork o repositório
2. Crie branch `feature/sua-feature`
3. Commit com mensagens descritivas
4. Push e abra Pull Request

---

## 📄 Licença

MIT License - Veja LICENSE.md

---

**Desenvolvido com ❤️ para o Cerrado Brasileiro**

*Inteligência Regenerativa em Pastagens • Supervisão Técnica • Gestão Econômica*