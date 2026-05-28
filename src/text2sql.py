import sqlite3
from database import get_schema_description, execute_query, print_table
from llm import generate_sql, generate_answer


def run_text2sql(db_path: str, tokenizer, model, question: str) -> None:
    schema = get_schema_description(db_path)

    print("\n--- SQL gerado ---")
    sql = generate_sql(tokenizer, model, schema, question)
    print(sql)

    print("\n--- Resultado ---")
    try:
        columns, rows = execute_query(db_path, sql)
        print_table(columns, rows)
    except sqlite3.Error as e:
        print(f"Erro ao executar SQL: {e}")
        return

    print("\n--- Resposta ---")
    answer = generate_answer(tokenizer, model, question, sql, columns, rows)
    print(answer)
    print()
