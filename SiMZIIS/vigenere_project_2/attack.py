# attack.py
# Брутфорс-атака по ключам длины <= max_key_len
# Внимание: пространство ключей растёт экспоненциально -> ограничение max_key_len (например 1..5)

import itertools
from cipher import vigenere_decrypt, get_alphabets
from utils import suggest_top_candidates

def generate_keys(alphabet: str, max_len: int):
    # генерирует все ключи длины 1..max_len из alphabet
    for L in range(1, max_len+1):
        for tup in itertools.product(alphabet, repeat=L):
            yield "".join(tup)

def brute_force(ciphertext: str, lang: str="ru", max_key_len: int=3, top_n:int=50, known_plaintext: str=None):
    lower_alpha, upper_alpha = get_alphabets(lang)
    alphabet = lower_alpha  # используем нижний регистр для генерации ключей
    candidates = []
    cnt = 0
    # предупреждение: делать осторожно (в GUI будет прогресс)
    for key in generate_keys(alphabet, max_key_len):
        dec = vigenere_decrypt(ciphertext, key, lang=lang)
        cnt += 1
        if known_plaintext:
            # простая быстрая проверка: если known_plaintext содержится в dec -> считаем найдено
            if known_plaintext in dec:
                return {"found": True, "key": key, "plaintext": dec, "tested": cnt}
        # не сохраняем все — сохраняем некоторую выборку
        candidates.append((key, dec))
    # ранжируем по статистике
    scored = suggest_top_candidates(candidates, lang, top_n=top_n)
    return {"found": False, "tested": cnt, "candidates": scored}
