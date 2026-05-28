import os

MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

_SRC_DIR = os.path.dirname(__file__)
_PROJECT_DIR = os.path.dirname(_SRC_DIR)
DB_PATH = os.path.join(_PROJECT_DIR, "data", "ecommerce.db")

GENERATION_PARAMS = {
    "temperature": 0.1,
    "top_p": 0.9,
    "repetition_penalty": 1.05,
    "max_new_tokens": 256,
    "do_sample": True,
}

MAX_DISPLAY_ROWS = 20
