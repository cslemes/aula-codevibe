# Text2SQL com Qwen2.5-Coder

<p align="center"><img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWZ2b3V5azZpdGJlc3o4YjFsZGRoeTRpY2prbGR1dWk2Z2Y0bGU0MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cNZmQ1qfjIZa4Xr3VE/giphy.gif" /></p>


Projeto didático que converte perguntas em português para consultas SQL usando um LLM local, sem frameworks externos como LangChain.

## O que é e qual problema resolve

Text2SQL permite que usuários não técnicos façam perguntas sobre um banco de dados em linguagem natural e recebam respostas baseadas em dados reais. Este projeto demonstra o pipeline completo de forma manual e transparente, facilitando o aprendizado.

## Relação com RAG

| RAG | Text2SQL |
|-----|----------|
| Chunks de documentos | Schema do banco (DDLs) |
| Embedding + busca vetorial | Extração direta via `sqlite_master` |
| LLM gera resposta livre | LLM gera SQL estruturado |
| Retrieval = busca semântica | Retrieval = execução de query |

Em ambos os casos, o contexto relevante é injetado no prompt antes da geração.

## Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd text2sql_qwen

# Instale as dependências e crie o ambiente virtual
uv sync
```

## Como executar

```bash
uv run python src/main.py
```

**Primeira execução:** o modelo Qwen2.5-Coder-1.5B-Instruct (~3 GB) é baixado automaticamente do Hugging Face na opção 2. Isso pode levar alguns minutos dependendo da sua conexão.

**Fluxo recomendado:**
1. Escolha **opção 1** para criar o banco de e-commerce com dados de exemplo.
2. Escolha **opção 2** para carregar o modelo e começar a fazer perguntas.
3. Digite **sair** para voltar ao menu, ou **3** para encerrar.

## Exemplos de perguntas que funcionam bem

- `Quais são os 3 produtos mais caros?`
- `Quantos pedidos cada cliente fez?`
- `Qual o faturamento total por categoria de produto?`
- `Quais pedidos foram cancelados e quem são os clientes?`
- `Qual cliente gastou mais no total?`
- `Liste os produtos com estoque abaixo de 15 unidades.`
- `Quais cidades têm mais clientes?`
- `Qual o ticket médio dos pedidos entregues?`

## Pipeline passo a passo

```
Pergunta do usuário
        │
        ▼
┌───────────────────┐
│  Extrai schema    │  get_schema_description() → DDLs das 4 tabelas
│  do SQLite        │
└────────┬──────────┘
         │ schema (texto)
         ▼
┌───────────────────┐
│  Monta prompt SQL │  build_sql_prompt(schema, question) → f-string
└────────┬──────────┘
         │ prompt
         ▼
┌───────────────────┐
│  Chama o LLM      │  Qwen2.5-Coder gera o SQL (temp=0.1)
└────────┬──────────┘
         │ raw output
         ▼
┌───────────────────┐
│  Limpa o SQL      │  extract_sql() remove markdown, texto extra
└────────┬──────────┘
         │ SQL limpo
         ▼
┌───────────────────┐
│  Executa no banco │  execute_query(db_path, sql) → (columns, rows)
└────────┬──────────┘
         │ resultados
         ▼
┌───────────────────┐
│  Exibe tabela     │  print_table() → ASCII tabular (máx. 20 linhas)
└────────┬──────────┘
         │ question + sql + rows
         ▼
┌───────────────────┐
│  Prompt explicação│  build_answer_prompt() → f-string
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Chama o LLM      │  Qwen gera resposta em português (1-2 frases)
└────────┬──────────┘
         │
         ▼
  Resposta exibida
```

## Como recriar o banco do zero

Escolha a opção **1** no menu a qualquer momento. As operações usam `CREATE TABLE IF NOT EXISTS` e `INSERT OR IGNORE`, tornando a operação idempotente — ela recria apenas o que estiver faltando.

Para forçar uma recriação completa, delete o arquivo manualmente:
```bash
rm data/ecommerce.db
```
E então use a opção 1 novamente.

## Como trocar o modelo

Edite `MODEL_NAME` em `src/config.py`:

| Modelo | Tamanho | Qualidade SQL | Velocidade CPU |
|--------|---------|---------------|----------------|
| `Qwen/Qwen2.5-Coder-1.5B-Instruct` | ~3 GB | Boa | Razoável |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | ~14 GB | Muito boa | Lenta |
| `defog/sqlcoder-7b-2` | ~14 GB | Excelente | Lenta |
| `Qwen/Qwen3-1.7B` | ~3.5 GB | Boa (uso geral) | Razoável |

## Como adaptar para outro banco real

1. Substitua `DB_PATH` em `config.py` pelo caminho/DSN do seu banco.
2. Reescreva `get_schema_description()` e `execute_query()` em `database.py` usando o driver adequado (`psycopg2` para Postgres, `mysql-connector-python` para MySQL).
3. Ajuste o prompt em `build_sql_prompt()` para mencionar o dialeto correto (ex.: "PostgreSQL" em vez de "SQLite").

## Problemas comuns

| Problema | Causa | Solução |
|----------|-------|---------|
| `CUDA out of memory` | GPU sem VRAM suficiente | Use CPU (automático) ou modelo menor |
| SQL com erro de sintaxe | Modelo pequeno alucina | Reformule a pergunta com termos mais próximos ao schema |
| Coluna inexistente no SQL | Alucinação do LLM | Perguntas mais diretas; considere modelo maior |
| Geração muito lenta | CPU sem AVX2 | Use uma máquina com GPU ou serviço de inferência |
| Modelo não encontrado | Sem acesso ao HuggingFace | Verifique conectividade ou use modelo local com `from_pretrained("/caminho/local")` |
