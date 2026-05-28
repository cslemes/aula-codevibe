import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import MODEL_NAME, GENERATION_PARAMS


def load_model(model_name: str = MODEL_NAME):
    print(f"Carregando modelo: {model_name}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    print(f"Dispositivo: {device.upper()}  |  dtype: {dtype}")

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True,
    )
    if device == "cpu":
        model = model.to(device)

    model.eval()
    print("Modelo carregado com sucesso.\n")
    return tokenizer, model


def _generate(tokenizer, model, prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            **GENERATION_PARAMS,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = output_ids[0][input_len:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def build_sql_prompt(schema: str, question: str) -> str:
    return f"""Você é um especialista em SQL. Sua tarefa é converter uma pergunta em linguagem natural para uma consulta SQL válida no dialeto SQLite.

Schema do banco de dados:
{schema}

Regras:
- Use apenas as tabelas e colunas que existem no schema acima.
- Retorne APENAS a consulta SQL, sem explicações, sem markdown, sem comentários.
- Use JOINs quando precisar combinar tabelas.
- Se a pergunta não puder ser respondida com este schema, retorne: SELECT 'pergunta fora do escopo' AS erro;

Pergunta:
{question}

SQL:"""


def build_answer_prompt(question: str, sql: str, columns: list, rows: list) -> str:
    rows_as_dicts = [dict(zip(columns, row)) for row in rows[:10]]
    return f"""Você é um assistente que explica resultados de banco de dados em português.

Pergunta original: {question}

Consulta SQL executada:
{sql}

Resultado (primeiras {len(rows_as_dicts)} linhas):
{rows_as_dicts}

Total de linhas retornadas: {len(rows)}

Responda em 1-2 frases, em português, baseando-se APENAS no resultado acima. Não invente dados."""


def extract_sql(raw_output: str) -> str:
    # tenta extrair de bloco markdown ```sql ... ``` ou ``` ... ```
    match = re.search(r"```(?:sql)?\s*(.*?)```", raw_output, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
    else:
        sql = raw_output.strip()

    # descarta tudo depois do primeiro ponto-e-vírgula (inclusive comentários extras)
    semicolon_pos = sql.find(";")
    if semicolon_pos != -1:
        sql = sql[: semicolon_pos + 1]

    return sql.strip()


def generate_sql(tokenizer, model, schema: str, question: str) -> str:
    prompt = build_sql_prompt(schema, question)
    raw = _generate(tokenizer, model, prompt)
    return extract_sql(raw)


def generate_answer(tokenizer, model, question: str, sql: str, columns: list, rows: list) -> str:
    prompt = build_answer_prompt(question, sql, columns, rows)
    return _generate(tokenizer, model, prompt)
