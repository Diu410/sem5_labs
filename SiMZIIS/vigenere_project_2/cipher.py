# cipher.py
# Исправленная реализация шифра Виженера — поддерживает русский и английский алфавиты,
# сохраняет регистр и сохраняет небуквенные символы.

from typing import Tuple

RUS_LOWER = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
RUS_UPPER = RUS_LOWER.upper()
ENG_LOWER = "abcdefghijklmnopqrstuvwxyz"
ENG_UPPER = ENG_LOWER.upper()

def get_alphabets(lang: str) -> Tuple[str,str]:
    lang = lang.lower()
    if lang.startswith("ru"):
        return RUS_LOWER, RUS_UPPER
    else:
        return ENG_LOWER, ENG_UPPER

def _shift_char(ch: str, key_ch: str, encrypt: bool, lower_alpha: str, upper_alpha: str) -> str:
    # выбираем базовый алфавит в зависимости от регистра символа plaintext/ciphertext
    if ch.islower() and ch in lower_alpha:
        base = lower_alpha
        key_norm = key_ch.lower()
    elif ch.isupper() and ch in upper_alpha:
        base = upper_alpha
        key_norm = key_ch.upper()
    else:
        # либо не буква, либо буква другого алфавита — возвращаем как есть
        return ch

    # теперь убедимся, что ключевой символ в том же алфавите/регистре, что и base
    if key_norm not in base:
        # даём понятную ошибку — это защитит от смешивания алфавитов в ключе
        raise ValueError(f"Символ ключа '{key_ch}' не принадлежит выбранному алфавиту/регистру.")
    m = len(base)
    a_idx = base.index(ch)
    k_idx = base.index(key_norm)
    if encrypt:
        new_idx = (a_idx + k_idx) % m
    else:
        new_idx = (a_idx - k_idx + m) % m
    return base[new_idx]

def _normalize_key_for_text(key: str, text: str, lower_alpha: str, upper_alpha: str):
    # Убираем из ключа символы не в выбранном алфавите (ни в lower, ни в upper)
    filtered_key = "".join([ch for ch in key if (ch.lower() in lower_alpha) or (ch.upper() in upper_alpha)])
    if not filtered_key:
        raise ValueError("Ключ не содержит букв выбранного алфавита.")
    # Сформировать последовательность ключевых символов для каждой буквы текста,
    # пропуская небуквенные символы (оставляя None на их местах)
    key_seq = []
    klen = len(filtered_key)
    ki = 0
    for ch in text:
        if (ch.islower() and ch in lower_alpha) or (ch.isupper() and ch in upper_alpha):
            key_seq.append(filtered_key[ki % klen])
            ki += 1
        else:
            key_seq.append(None)
    return key_seq

def vigenere_encrypt(plaintext: str, key: str, lang: str="ru") -> str:
    lower_alpha, upper_alpha = get_alphabets(lang)
    key_seq = _normalize_key_for_text(key, plaintext, lower_alpha, upper_alpha)
    out = []
    for ch, kch in zip(plaintext, key_seq):
        if kch is None:
            out.append(ch)
        else:
            out.append(_shift_char(ch, kch, True, lower_alpha, upper_alpha))
    return "".join(out)

def vigenere_decrypt(ciphertext: str, key: str, lang: str="ru") -> str:
    lower_alpha, upper_alpha = get_alphabets(lang)
    key_seq = _normalize_key_for_text(key, ciphertext, lower_alpha, upper_alpha)
    out = []
    for ch, kch in zip(ciphertext, key_seq):
        if kch is None:
            out.append(ch)
        else:
            out.append(_shift_char(ch, kch, False, lower_alpha, upper_alpha))
    return "".join(out)
