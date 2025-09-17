# utils.py
# частотный анализ и оценка кандидатов (chi-squared)

from collections import Counter
import math

# Частоты букв в русском и английском (примерные, нормированные)
ENG_FREQ = {
 'a': 0.08167,'b': 0.01492,'c': 0.02782,'d': 0.04253,'e': 0.12702,'f': 0.02228,'g': 0.02015,'h': 0.06094,
 'i': 0.06966,'j': 0.00153,'k': 0.00772,'l': 0.04025,'m': 0.02406,'n': 0.06749,'o': 0.07507,'p': 0.01929,
 'q': 0.00095,'r': 0.05987,'s': 0.06327,'t': 0.09056,'u': 0.02758,'v': 0.00978,'w': 0.02360,'x': 0.00150,
 'y': 0.01974,'z': 0.00074
}
# Русские частоты (приблизительно)
RUS_FREQ = {
 'о':0.1097,'е':0.0845,'а':0.0801,'и':0.0735,'н':0.0670,'т':0.0626,'с':0.0547,'р':0.0473,'в':0.0454,'л':0.0434,
 'к':0.0349,'м':0.0321,'д':0.0298,'п':0.0281,'у':0.0262,'я':0.0201,'ы':0.0189,'ь':0.0174,'г':0.0169,'з':0.0165,
 'б':0.0145,'ч':0.0121,'й':0.0094,'х':0.0090,'ж':0.0073,'ш':0.0063,'ю':0.0064,'ц':0.0048,'щ':0.0036,'э':0.0032,'ё':0.0004,'ъ':0.0004
}

def chi_squared_score(text: str, alphabet: str, freq_map: dict) -> float:
    # вычисляем chi-squared между частотой букв в тексте и эталонной частотой
    text = text.lower()
    counts = Counter([c for c in text if c in alphabet])
    n = sum(counts.values())
    if n == 0:
        return float('inf')
    chi2 = 0.0
    for ch in alphabet:
        observed = counts.get(ch, 0)
        expected = freq_map.get(ch, 0) * n
        chi2 += (observed - expected) ** 2 / (expected + 1e-9)
    # чем меньше chi2 — лучше совпадение с языком
    return chi2

def suggest_top_candidates(candidates: list, lang: str, top_n: int=10):
    if lang.startswith("ru"):
        alphabet = "".join(sorted(RUS_FREQ.keys()))  # не важно порядок
        freq_map = RUS_FREQ
    else:
        alphabet = "".join(sorted(ENG_FREQ.keys()))
        freq_map = ENG_FREQ

    scored = []
    for key, decrypted in candidates:
        sc = chi_squared_score(decrypted, alphabet, freq_map)
        scored.append((sc, key, decrypted))
    scored.sort(key=lambda x: x[0])  # по возрастанию chi2
    return scored[:top_n]
