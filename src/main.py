import os
import sys

# garante que imports relativos dentro de src/ funcionem
sys.path.insert(0, os.path.dirname(__file__))

from config import DB_PATH, MODEL_NAME
from database import init_database
from llm import load_model
from text2sql import run_text2sql

EXAMPLE_QUESTIONS = [
    "Quais são os 3 produtos mais caros?",
    "Quantos pedidos cada cliente fez?",
    "Qual o faturamento total por categoria de produto?",
    "Quais pedidos foram cancelados e quem são os clientes?",
    "Qual cliente gastou mais no total?",
]


def print_menu():
    print("\n" + "=" * 50)
    print("         TEXT2SQL — E-Commerce Demo")
    print("=" * 50)
    print("O que você deseja fazer?")
    print("  1. Criar/recriar banco de exemplo (e-commerce)")
    print("  2. Carregar banco existente e fazer perguntas")
    print("  3. Sair")
    print("-" * 50)


def question_loop(db_path: str, tokenizer, model) -> None:
    print("\nExemplos de perguntas que funcionam bem:")
    for q in EXAMPLE_QUESTIONS:
        print(f"  • {q}")
    print('\nDigite sua pergunta ou "sair" para voltar ao menu.\n')

    while True:
        try:
            question = input("Pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() == "sair":
            break

        run_text2sql(db_path, tokenizer, model, question)


def main():
    tokenizer = None
    model = None

    while True:
        print_menu()
        try:
            choice = input("Escolha: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando...")
            break

        if choice == "1":
            print()
            init_database(DB_PATH)

        elif choice == "2":
            if not os.path.exists(DB_PATH):
                print("\n[!] Banco não encontrado. Use a opção 1 para criá-lo primeiro.")
                continue

            if model is None:
                print()
                tokenizer, model = load_model(MODEL_NAME)

            question_loop(DB_PATH, tokenizer, model)

        elif choice == "3":
            print("\nAté logo!")
            break

        else:
            print("\n[!] Opção inválida. Digite 1, 2 ou 3.")


if __name__ == "__main__":
    main()
