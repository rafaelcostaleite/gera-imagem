# Sistema de Gestão de Casos TI

Sistema completo de gerenciamento de casos (chamados) para equipes de TI, baseado em conceitos de ITIL, com planejamento de sprints e controle de apontamentos de horas.

## Objetivo

Criar um sistema de gestão de casos para que a equipe interna de TI efetue o atendimento de demandas de forma organizada, seguindo as melhores práticas de ITIL, com recursos de:

- Gerenciamento de casos (chamados)
- Autenticação via Active Directory (Microsoft Exchange)
- Controle de apontamentos de horas
- Planejamento de sprints
- Classificação e categorização de casos
- Rastreamento de status e fluxos de trabalho

## Arquitetura

### Backend
- **Python 3.11** com **FastAPI**
- **PostgreSQL** para banco de dados
- **SQLAlchemy** como ORM
- **Alembic** para migrações
- **LDAP3** para autenticação Active Directory
- **JWT** para autenticação de sessões

### Frontend
- **React 18** com **JavaScript**
- **React Router** para navegação
- **Axios** para chamadas à API
- **Context API** para gerenciamento de estado

### Infraestrutura
- **Docker** e **Docker Compose** para containerização
- **Git** para versionamento

## Funcionalidades Principais

### 1. Autenticação e Usuários
- Login via Active Directory (Microsoft Exchange)
- Autenticação JWT
- Gerenciamento de sessões
- Criação automática de usuários no primeiro login

### 2. Gestão de Casos

#### Tipos de Casos
- **Estou com um problema** (corretivas)
- **Tenho uma dúvida** (suporte)
- **Quero pedir algo** (requisições/preventivas/intervenções)
- **Solicitação de melhorias** (melhorias em sistemas)

#### Categorias
- Corretiva
- Suporte
- Requisições
- Preventivas
- Intervenções
- Intervenção Extração de dados
- Melhorias em sistemas

#### Fluxo de Trabalho
1. **Aberto**: Estágio inicial quando o caso é criado
2. **Em atendimento**: Ativado automaticamente ao primeiro apontamento
3. **Solucionado**: Quando o técnico resolve o caso
4. **Concluído**: Fechamento automático após 30 dias de solução (não reversível)
5. **Cancelado**: Disponível apenas para casos Abertos ou Em atendimento

#### Alocação
- **Dono do Caso**: Gestor da área responsável
- **Equipe**: Equipe de atendimento
- **Técnico Responsável**: Pessoa alocada para tratar o caso

#### Classificação
- Primeira etapa do atendimento realizada pelo analista
- Define a categoria e pode alterar o tipo do caso
- Define alocações (dono, equipe, técnico)

### 3. Apontamentos de Tempo

#### Campos
- **Data**: Não pode ser futura ou em período fechado
- **Horas**: Formato HH:MM (ex: 01:30)
- **Horas Decimal**: Calculado automaticamente (ex: 01:30 = 1.5)
- **Descrição**: Obrigatória
- **Tipo de Tarefa**:
  - 01-Levantamento/Documentação/Especificação
  - 02-Parametrização/Desenvolvimento
  - 03-Homologação/Teste/GMUD
  - 04-Revisão em par
  - 05-Revisão SM
  - 06-Entrada em produção
  - 0-Não classificado

#### Regras
- Não pode apontar em datas futuras
- Não pode apontar em períodos fechados
- Primeiro apontamento muda status do caso para "Em atendimento"
- Validação de formato HH:MM

### 4. Período de Fechamento
- Controle de períodos fechados para apontamentos
- Sistema aceita apenas apontamentos com datas posteriores ao último período fechado
- Previne alterações em períodos já auditados

### 5. Planejamento de Sprints
- Criação e gerenciamento de sprints
- Adição/remoção de casos às sprints
- Visualização de casos por sprint
- Marcação de sprints como concluídas
- Dashboard de planejamento

### 6. Árvore de Serviços
- Organização hierárquica de serviços
- Classificação de casos por serviço
- Estrutura pai-filho para categorização

## Instalação

### Pré-requisitos
- Docker
- Docker Compose
- Git

### Passos

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd gera-imagem
```

2. Configure o arquivo de ambiente do backend:
```bash
cp backend/.env.example backend/.env
```

3. Edite o arquivo `backend/.env`:

**Para Desenvolvimento (padrão):**
```env
# Modo desenvolvimento - permite login com senha padrão 123456
DEVELOPMENT_MODE=True
DEV_DEFAULT_PASSWORD=123456

# Configurações do AD (podem ser deixadas como estão em dev)
AD_SERVER=ldap://seu-servidor-ad.com
AD_DOMAIN=seu-dominio.com
AD_BASE_DN=DC=seu-dominio,DC=com
SECRET_KEY=sua-chave-secreta-aqui
```

**Para Produção:**
```env
# Desabilitar modo desenvolvimento - apenas autenticação AD
DEVELOPMENT_MODE=False

# Configurações do AD (obrigatórias)
AD_SERVER=ldap://seu-servidor-ad.com
AD_DOMAIN=seu-dominio.com
AD_BASE_DN=DC=seu-dominio,DC=com
AD_USE_SSL=True
SECRET_KEY=sua-chave-secreta-forte-aqui
```

4. Inicie os containers:
```bash
docker-compose up -d
```

5. Aguarde a inicialização dos serviços:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Documentação da API: http://localhost:8000/docs

6. Acesse a aplicação:
```
http://localhost:3000
```

### Comandos Úteis

Parar os containers:
```bash
docker-compose down
```

Ver logs:
```bash
docker-compose logs -f
```

Reconstruir após mudanças:
```bash
docker-compose up -d --build
```

Acessar banco de dados:
```bash
docker exec -it it-cases-db psql -U admin -d it_cases
```

### Modo de Desenvolvimento

O sistema possui um **modo de desenvolvimento** que facilita o teste e desenvolvimento sem necessidade de configurar um servidor Active Directory.

**Como funciona:**

Quando `DEVELOPMENT_MODE=True` (padrão no docker-compose.yml):
- Qualquer usuário pode fazer login usando a senha padrão `123456`
- O usuário é criado automaticamente no banco de dados
- O email gerado será `usuario@dev.local`
- Ainda é possível usar autenticação AD mesmo em modo dev

**Exemplo de uso:**
```
Usuário: joao
Senha: 123456
```

O usuário "joao" será criado automaticamente com:
- Username: joao
- Email: joao@dev.local
- Nome completo: Joao

**Importante:**
- ⚠️ **NUNCA use `DEVELOPMENT_MODE=True` em produção!**
- Em produção, sempre defina `DEVELOPMENT_MODE=False` para forçar autenticação apenas via Active Directory
- A senha padrão deve ser alterada caso você use modo dev em ambiente compartilhado

## Estrutura do Projeto

```
gera-imagem/
├── backend/
│   ├── app/
│   │   ├── api/              # Rotas da API
│   │   │   ├── auth.py       # Autenticação
│   │   │   ├── cases.py      # Gestão de casos
│   │   │   ├── time_entries.py  # Apontamentos
│   │   │   └── sprints.py    # Sprints
│   │   ├── core/             # Configurações centrais
│   │   │   ├── config.py     # Configurações
│   │   │   ├── database.py   # Conexão BD
│   │   │   └── security.py   # JWT e segurança
│   │   ├── models/           # Modelos do banco
│   │   │   └── models.py     # Todos os modelos
│   │   ├── schemas/          # Schemas Pydantic
│   │   │   ├── auth.py
│   │   │   ├── case.py
│   │   │   ├── time_entry.py
│   │   │   ├── sprint.py
│   │   │   └── user.py
│   │   ├── services/         # Lógica de negócio
│   │   │   └── auth_service.py  # Autenticação AD
│   │   └── main.py           # Aplicação principal
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   └── Layout.js
│   │   ├── contexts/         # Context API
│   │   │   └── AuthContext.js
│   │   ├── pages/            # Páginas
│   │   │   ├── Login.js
│   │   │   ├── Dashboard.js
│   │   │   └── NewCase.js
│   │   ├── services/         # Serviços API
│   │   │   └── api.js
│   │   ├── styles/           # CSS
│   │   ├── App.js
│   │   └── index.js
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .gitignore
└── README.md
```

## API Endpoints

### Autenticação
- `POST /api/v1/auth/login` - Login com AD
- `POST /api/v1/auth/login-json` - Login com JSON

### Casos
- `GET /api/v1/cases` - Listar casos
- `POST /api/v1/cases` - Criar caso
- `GET /api/v1/cases/{id}` - Obter caso
- `PUT /api/v1/cases/{id}` - Atualizar caso
- `POST /api/v1/cases/{id}/classify` - Classificar caso
- `POST /api/v1/cases/{id}/status` - Atualizar status
- `GET /api/v1/cases/my/cases` - Meus casos

### Apontamentos
- `GET /api/v1/time-entries` - Listar apontamentos
- `POST /api/v1/time-entries` - Criar apontamento
- `GET /api/v1/time-entries/{id}` - Obter apontamento
- `PUT /api/v1/time-entries/{id}` - Atualizar apontamento
- `DELETE /api/v1/time-entries/{id}` - Deletar apontamento
- `GET /api/v1/time-entries/my` - Meus apontamentos

### Sprints
- `GET /api/v1/sprints` - Listar sprints
- `POST /api/v1/sprints` - Criar sprint
- `GET /api/v1/sprints/{id}` - Obter sprint
- `PUT /api/v1/sprints/{id}` - Atualizar sprint
- `POST /api/v1/sprints/{id}/cases` - Adicionar casos
- `DELETE /api/v1/sprints/{id}/cases/{case_id}` - Remover caso
- `POST /api/v1/sprints/{id}/complete` - Concluir sprint

## Modelos de Dados

### User (Usuário)
- ID, username, email, full_name
- is_active, is_superuser
- Timestamps

### Case (Caso)
- ID, title, description
- case_type, category, status
- requester_id, owner_id, technician_id, team_id, service_id
- created_at, updated_at, solved_at, closed_at, cancelled_at

### TimeEntry (Apontamento)
- ID, case_id, user_id
- entry_date, hours_spent, hours_decimal
- description, task_type
- Timestamps

### Sprint
- ID, name, description
- start_date, end_date
- is_active, is_completed
- Relacionamento muitos-para-muitos com Cases

### Team (Equipe)
- ID, name, description
- is_active

### Service (Serviço)
- ID, name, description
- parent_id (auto-relacionamento)
- is_active

### ClosingPeriod (Período de Fechamento)
- ID, closing_date
- description, created_by

## Configuração do Active Directory

Para configurar a autenticação com Active Directory, edite o arquivo `backend/.env`:

```env
AD_SERVER=ldap://seu-servidor-ad.com:389
AD_DOMAIN=DOMINIO
AD_BASE_DN=DC=dominio,DC=com
AD_USE_SSL=False
```

Substitua pelos valores corretos do seu ambiente.

## Segurança

- Autenticação JWT com expiração configurável
- Senhas nunca são armazenadas (autenticação via AD)
- CORS configurado para origens específicas
- Validação de dados com Pydantic
- Proteção contra SQL Injection via SQLAlchemy
- Headers de segurança configurados

## Próximas Melhorias

- [ ] Relatórios e dashboards analíticos
- [ ] Exportação de dados (Excel, CSV)
- [ ] Notificações por email
- [ ] SLA e métricas de performance
- [ ] Anexos em casos
- [ ] Comentários em casos
- [ ] Histórico de mudanças
- [ ] Filtros avançados
- [ ] Busca full-text
- [ ] Permissões granulares por perfil
- [ ] Integração com outras ferramentas (Jira, Slack, etc)
- [ ] API webhooks
- [ ] Modo escuro

## Conceitos ITIL Implementados

- Gerenciamento de Incidentes (casos tipo "problema")
- Gerenciamento de Requisições de Serviço
- Gerenciamento de Mudanças (melhorias)
- Categorização de serviços
- SLA e métricas de tempo
- Gestão de conhecimento (base de casos)

## Suporte e Contribuições

Para reportar bugs ou sugerir melhorias, abra uma issue no repositório.

## Licença

Este projeto está disponível para uso livre.
