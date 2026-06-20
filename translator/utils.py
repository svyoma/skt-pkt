"""
IAST phoneme utilities for the Sanskrit-Prakrit rule engine.
"""

from typing import List, Set, Tuple, Optional

# ---------------------------------------------------------------------------
# Phoneme inventory
# ---------------------------------------------------------------------------

VOWELS: Set[str] = {
    'a', 'ā', 'i', 'ī', 'u', 'ū',
    'ṛ', 'ṝ', 'ḷ',
    'e', 'ai', 'o', 'au',
}

LONG_VOWELS: Set[str] = {'ā', 'ī', 'ū', 'ṝ', 'e', 'o', 'ai', 'au'}
SHORT_VOWELS: Set[str] = {'a', 'i', 'u', 'ṛ', 'ḷ'}

# Vowels that BLOCK consonant gemination (8.2.92): only the true Sanskrit long
# vowels ā/ī/ū/ṝ.  e and o are guṇa (sandhyakṣara) vowels that count as SHORT
# in Prakrit for doubling purposes, so they do NOT appear here.
GEM_BLOCK_VOWELS: Set[str] = frozenset({'ā', 'ī', 'ū', 'ṝ'})

# ---------------------------------------------------------------------------
# Ādeśa protection marker
# ---------------------------------------------------------------------------
# A token suffixed with PROTECTED_MARKER is an ādeśa (phonological substitute).
# Per Hemacandra's single-substitution principle, no further substitution rule
# may act on it.  Gemination IS allowed (double_consonant strips the marker).
# The marker is stripped in detokenize() before surface output.

PROTECTED_MARKER: str = '°'


def protect(t: str) -> str:
    """Mark token t as an ādeśa (exempt from further rule substitution)."""
    return t if t.endswith(PROTECTED_MARKER) else t + PROTECTED_MARKER


def unprotect(t: str) -> str:
    """Strip the ādeśa marker; returns the bare IAST token."""
    return t[:-1] if t.endswith(PROTECTED_MARKER) else t


def is_protected(t: str) -> bool:
    return t.endswith(PROTECTED_MARKER)


CONSONANTS: Set[str] = {
    'k', 'kh', 'g', 'gh', 'ṅ',
    'c', 'ch', 'j', 'jh', 'ñ',
    'ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ',
    't', 'th', 'd', 'dh', 'n',
    'p', 'ph', 'b', 'bh', 'm',
    'y', 'r', 'l', 'ḷ', 'v',
    'ś', 'ṣ', 's', 'h',
}

# Tokens ordered longest-first for greedy matching
_TOKENS_ORDERED: List[str] = [
    # Diphthongs (length 2)
    'ai', 'au',
    # Long vowels (single unicode char)
    'ā', 'ī', 'ū', 'ṝ',
    # Aspirate digraphs (must precede unaspirated single chars)
    'kh', 'gh', 'ch', 'jh', 'ṭh', 'ḍh', 'th', 'dh', 'ph', 'bh',
    # Retroflex / special single chars
    'ṭ', 'ḍ', 'ṇ', 'ñ', 'ṅ', 'ś', 'ṣ',
    # Vocalic liquids
    'ṛ', 'ḷ',
    # Anusvara and visarga
    'ṃ', 'ḥ',
    # Simple consonants
    'k', 'g', 'c', 'j', 't', 'd', 'p', 'b', 'm',
    'y', 'r', 'l', 'v', 's', 'h', 'n',
    # Simple vowels
    'a', 'i', 'u', 'e', 'o',
]

# Vowel lengthening / shortening maps
LENGTHEN: dict = {
    'a': 'ā', 'i': 'ī', 'u': 'ū', 'ṛ': 'ṝ',
    'ā': 'ā', 'ī': 'ī', 'ū': 'ū', 'ṝ': 'ṝ',
    'e': 'e', 'o': 'o', 'ai': 'ai', 'au': 'au',
}
SHORTEN: dict = {
    'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṝ': 'ṛ',
    'a': 'a', 'i': 'i', 'u': 'u', 'ṛ': 'ṛ',
    'e': 'e', 'o': 'o', 'ai': 'ai', 'au': 'au',
}

# Aspirate doubling: C → (preceding unaspirated/unvoiced, C)  [8.2.90]
ASPIRATE_DOUBLING: dict = {
    'kh': ['k', 'kh'],
    'gh': ['g', 'gh'],
    'ch': ['c', 'ch'],
    'jh': ['j', 'jh'],
    'ṭh': ['ṭ', 'ṭh'],
    'ḍh': ['ḍ', 'ḍh'],
    'th': ['t', 'th'],
    'dh': ['d', 'dh'],
    'ph': ['p', 'ph'],
    'bh': ['b', 'bh'],
}

# Upper-member elision list (8.2.77)
UPPER_ELIDE: Set[str] = {'k', 'g', 'ṭ', 'ḍ', 't', 'd', 'p', 'ś', 'ṣ', 's'}

# Lower-member list (8.2.78)
LOWER_ELIDE: Set[str] = {'m', 'n', 'y'}

# Always-elided in clusters (8.2.79)
CLUSTER_ALWAYS_ELIDE: Set[str] = {'r', 'l', 'v'}


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def tokenize(word: str) -> List[str]:
    """Convert an IAST string to a list of phoneme tokens."""
    tokens: List[str] = []
    word = word.strip()
    i = 0
    while i < len(word):
        matched = False
        for tok in _TOKENS_ORDERED:
            tlen = len(tok)
            if word[i: i + tlen] == tok:
                tokens.append(tok)
                i += tlen
                matched = True
                break
        if not matched:
            i += 1  # skip unknown character
    return tokens


def detokenize(tokens: List[str]) -> str:
    return ''.join(unprotect(t) for t in tokens)


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def is_vowel(t: str) -> bool:
    return unprotect(t) in VOWELS


def is_consonant(t: str) -> bool:
    return unprotect(t) in CONSONANTS


def is_long_vowel(t: str) -> bool:
    return t in LONG_VOWELS


def is_short_vowel(t: str) -> bool:
    return t in SHORT_VOWELS


def prev_is_vowel(tokens: List[str], idx: int) -> bool:
    """True if the token immediately before idx is a pure vowel.
    Anusvāra (ṃ) is explicitly excluded: a consonant following anusvāra is
    preceded by a nasal phoneme, not a bare vowel, so it is NOT intervocalic."""
    if idx <= 0:
        return False
    return is_vowel(tokens[idx - 1])


def next_is_vowel(tokens: List[str], idx: int) -> bool:
    if idx >= len(tokens) - 1:
        return False
    return is_vowel(tokens[idx + 1])


def in_cluster(tokens: List[str], idx: int) -> bool:
    """True if tokens[idx] is adjacent to another consonant."""
    t = tokens[idx]
    if not is_consonant(t):
        return False
    if idx > 0 and is_consonant(tokens[idx - 1]):
        return True
    if idx < len(tokens) - 1 and is_consonant(tokens[idx + 1]):
        return True
    return False


def is_intervocalic_single(tokens: List[str], idx: int) -> bool:
    """
    True if tokens[idx] is a non-initial, single (non-conjunct) consonant
    that immediately follows a vowel and precedes a vowel.
    This is the environment for Part-VII rules (8.1.176 adhikāra).
    """
    t = tokens[idx]
    if not is_consonant(t):
        return False
    if idx == 0:
        return False
    if in_cluster(tokens, idx):
        return False
    return prev_is_vowel(tokens, idx) and next_is_vowel(tokens, idx)


def find_clusters(tokens: List[str]) -> List[Tuple[int, int]]:
    """Return list of (start, end) spans for maximal consonant clusters (length ≥ 2)."""
    clusters: List[Tuple[int, int]] = []
    i = 0
    while i < len(tokens):
        if is_consonant(tokens[i]):
            j = i
            while j < len(tokens) and is_consonant(tokens[j]):
                j += 1
            if j - i >= 2:
                clusters.append((i, j))
            i = j
        else:
            i += 1
    return clusters


# ---------------------------------------------------------------------------
# Gemination helper
# ---------------------------------------------------------------------------

def double_consonant(c: str) -> List[str]:
    """
    Return the doubled representation of consonant c as a list of tokens.
    8.2.90: aspirates → unaspirated + aspirate (e.g. dh → d + dh = ddh)
    8.2.93: r and h are NOT doubled.
    The protection marker on an ādeśa is preserved on the ādeśa copy;
    the gemination copy (the new token inserted before it) is always bare.
    """
    bare = unprotect(c)
    if bare in ('r', 'h'):
        return [c]
    if bare in ASPIRATE_DOUBLING:
        pair = ASPIRATE_DOUBLING[bare]   # e.g. ['k', 'kh'] for 'kh'
        return [pair[0], c]              # gem-copy bare + ādeśa (possibly marked)
    return [bare, c]                     # gem-copy bare + ādeśa (possibly marked)


# ---------------------------------------------------------------------------
# Vibhakti stripping
# ---------------------------------------------------------------------------

# Ordered longest-first; each entry is (suffix_to_strip, replacement)
# Only the most unambiguous endings are included to avoid false positives.
_VIBHAKTI_ENDINGS: List[Tuple[str, str]] = [
    # Genitive sg a-stem
    ('asya', 'a'),
    # Locative sg a-stem
    ('asmin', 'a'),
    # Ablative sg
    ('āt', 'a'),
    # Instrumental sg
    ('ena', 'a'),
    # Dative sg
    ('āya', 'a'),
    # Nominative sg (visarga form)
    ('aḥ', 'a'),
    # Accusative sg
    ('am', 'a'),
    # Nominative pl
    ('āḥ', 'a'),
    # Accusative pl
    ('ān', 'a'),
    # Feminine ā-stem genitive
    ('āyāḥ', 'ā'),
    # Feminine ā-stem locative
    ('āyām', 'ā'),
    # Visarga alone
    ('ḥ', ''),
    # Anusvara alone
    ('ṃ', ''),
]


def strip_vibhakti(word: str) -> Tuple[str, Optional[str]]:
    """
    Try to strip a common case ending.
    Returns (stripped_stem, ending_stripped) or (word, None) if no stripping.

    Guard: the remaining stem must be at least as long as the suffix itself, so
    that short words (e.g. 'sasya' treated as 'sa-' + genitive '-asya') are not
    wrongly stripped.
    """
    for suffix, repl in _VIBHAKTI_ENDINGS:
        if word.endswith(suffix):
            stem = word[: -len(suffix)] + repl
            # Stem must have at least max(2, len(suffix)) characters
            if len(stem) >= max(2, len(suffix)):
                return stem, suffix
    return word, None
