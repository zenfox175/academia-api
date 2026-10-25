# Academia FitTec

API em FastAPI para gerenciamento de alunos, personal trainers, matrículas, treinos e fichas de treino da Academia FitTec.

Grupo: Alexandre Malta, Christiano Santos, Rafael Santana, João dos Anjos e Luiz Henrique.

## Alterações desta versão

- A matrícula é a chave primária da tabela `pessoas` e agora é um número inteiro gerado automaticamente pelo banco.
- O campo `id` separado foi removido da tabela `pessoas`, evitando dois campos com a mesma função.
- No `POST /pessoas/`, a matrícula não é informada pelo usuário; ela é criada automaticamente.
- Foi criada a tabela `tipos_pessoa` com os valores fixos `1 - ALUNO` e `2 - PERSONAL`.
- O cadastro de pessoa recebe `tipo_pessoa_id` e se relaciona com `tipos_pessoa`.
- O telefone aceita exatamente 11 dígitos numéricos.
- O `GET /pessoas/` permite busca por matrícula, nome, e-mail, telefone e tipo de pessoa.
- O retorno de pessoas inclui `data_criacao`.
- A tabela `treinos` funciona como catálogo de treinos, sem vínculo direto com aluno.
- A tabela `fichas_treino` relaciona aluno, personal e treino.

## Estrutura das tabelas

### Tipos de pessoa

| Campo | Tipo | Descrição |
|---|---|---|
| id | INTEGER | Chave primária; `1` para aluno e `2` para personal |
| descricao | VARCHAR(20) | `ALUNO` ou `PERSONAL` |

### Pessoas

| Campo | Tipo | Descrição |
|---|---|---|
| matricula | INTEGER | Chave primária com autoincremento |
| nome | VARCHAR(100) | Nome completo |
| email | VARCHAR(150) | E-mail único |
| telefone | VARCHAR(11) | Telefone único, exatamente 11 números |
| tipo_pessoa_id | INTEGER | FK para `tipos_pessoa.id` |
| data_criacao | DATETIME | Data de criação automática |

### Matrículas dos alunos

| Campo | Tipo | Descrição |
|---|---|---|
| id | INTEGER | Chave primária |
| aluno_matricula | INTEGER | FK para a matrícula de uma pessoa do tipo aluno |
| personal_matricula | INTEGER | FK para a matrícula de uma pessoa do tipo personal |
| usuario_inclusao | VARCHAR(100) | Usuário que criou o vínculo |
| data_inclusao | DATETIME | Data automática de inclusão |
| usuario_alteracao | VARCHAR(100) | Usuário da última alteração |
| data_alteracao | DATETIME | Data automática da alteração |

### Treinos

| Campo | Tipo | Descrição |
|---|---|---|
| id | INTEGER | Chave primária do treino |
| nome | VARCHAR(100) | Nome do treino |
| descricao | TEXT | Descrição do treino |
| objetivo | VARCHAR(150) | Objetivo do treino |
| nivel | VARCHAR(30) | Nível do treino |
| data_criacao | DATETIME | Data de criação automática |

### Fichas de treino

| Campo | Tipo | Descrição |
|---|---|---|
| id | INTEGER | Chave primária |
| aluno_matricula | INTEGER | FK para o aluno |
| personal_matricula | INTEGER | FK para o personal |
| treino_id | INTEGER | FK para o treino |
| observacoes | TEXT | Observações que permitem personalizar a ficha ao perfil do aluno |
| data_criacao | DATETIME | Data de criação automática |

## Como executar

No PowerShell, entre na pasta do projeto e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Depois abra:

- Documentação Swagger: <http://127.0.0.1:8000/docs>
- API: <http://127.0.0.1:8000>

> Como o tipo da matrícula mudou de texto para inteiro com autoincremento, apague qualquer `academia.db` de uma versão anterior antes de iniciar esta versão. O SQLite recriará as tabelas automaticamente.

## Exemplos para teste

### 1. Criar um aluno

`POST /pessoas/`

```json
{
  "nome": "João dos Anjos",
  "email": "joao@email.com",
  "telefone": "11999998888",
  "tipo_pessoa_id": 1
}
```

A resposta incluirá uma matrícula gerada automaticamente, por exemplo:

```json
{
  "nome": "João dos Anjos",
  "email": "joao@email.com",
  "telefone": "11999998888",
  "tipo_pessoa_id": 1,
  "matricula": 1
}
```

### 2. Criar um personal

`POST /pessoas/`

```json
{
  "nome": "Carlos Silva",
  "email": "carlos@email.com",
  "telefone": "11988887777",
  "tipo_pessoa_id": 2
}
```

Se for a segunda pessoa cadastrada, a matrícula retornada será `2`.

### 3. Vincular aluno e personal

`POST /matriculas/`

```json
{
  "aluno_matricula": 1,
  "personal_matricula": 2,
  "usuario_inclusao": "admin"
}
```

### 4. Criar um treino

`POST /treinos/`

```json
{
  "nome": "Treino A - Peito e Tríceps",
  "descricao": "Treino de força com exercícios para peito e tríceps.",
  "objetivo": "Hipertrofia",
  "nivel": "Intermediário"
}
```

### 5. Criar uma ficha de treino

Use no campo `treino_id` o ID retornado ao criar o treino.

`POST /fichas-treino/`

```json
{
  "aluno_matricula": 1,
  "personal_matricula": 2,
  "treino_id": 1,
  "observacoes": "Ajustar carga e repetições de acordo com a evolução do aluno."
}
```

## Rotas

| Método | Rota | Função |
|---|---|---|
| GET | `/pessoas/` | Lista pessoas e filtra por qualquer campo de cadastro |
| GET | `/pessoas/{matricula}` | Busca pessoa pela matrícula numérica |
| POST | `/pessoas/` | Cadastra aluno ou personal e gera a matrícula automaticamente |
| PUT | `/pessoas/{matricula}` | Atualiza uma pessoa |
| DELETE | `/pessoas/{matricula}` | Exclui uma pessoa sem vínculos |
| GET | `/tipos-pessoa/` | Lista `1 - ALUNO` e `2 - PERSONAL` |
| GET | `/matriculas/` | Lista os vínculos entre aluno e personal |
| GET | `/matriculas/{id}` | Busca um vínculo |
| POST | `/matriculas/` | Vincula aluno e personal pelas matrículas |
| PUT | `/matriculas/{id}` | Altera o personal do aluno |
| DELETE | `/matriculas/{id}` | Exclui o vínculo |
| GET | `/treinos/` | Lista treinos e permite filtros por nome, objetivo e nível |
| GET | `/treinos/{id}` | Busca um treino |
| POST | `/treinos/` | Cria um treino no catálogo |
| PUT | `/treinos/{id}` | Atualiza os dados do treino |
| DELETE | `/treinos/{id}` | Exclui um treino |
| GET | `/fichas-treino/` | Lista fichas e permite filtrar por aluno ou personal |
| GET | `/fichas-treino/{id}` | Busca uma ficha |
| POST | `/fichas-treino/` | Relaciona aluno, personal e treino |
| PUT | `/fichas-treino/{id}` | Atualiza treino, personal ou observações da ficha |
| DELETE | `/fichas-treino/{id}` | Exclui uma ficha de treino |
