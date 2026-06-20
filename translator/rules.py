"""
Sanskrit→Prakrit phonological rules from Hemacandra's Siddhahemaśabdānuśāsana
Adhyāya VIII, Pādas 1–2 (all 489 sūtras).

Each rule function takes List[Form] and returns List[Form].
OBLIGATORY rules replace forms in-place (1 → 1).
OPTIONAL / BAHULAM rules branch (1 → 2).

The Form class is defined in engine.py; imported here to avoid circular deps.
"""

from typing import List, Callable
from .utils import (
    VOWELS, LONG_VOWELS, SHORT_VOWELS, GEM_BLOCK_VOWELS, CONSONANTS,
    UPPER_ELIDE, LOWER_ELIDE, CLUSTER_ALWAYS_ELIDE,
    is_vowel, is_consonant, is_long_vowel, is_short_vowel,
    in_cluster, is_intervocalic_single, find_clusters,
    prev_is_vowel, next_is_vowel,
    double_consonant, detokenize, tokenize,
    SHORTEN, LENGTHEN,
    protect, unprotect, is_protected,
)


# ---------------------------------------------------------------------------
# Form class (defined here to avoid circular import with engine.py)
# ---------------------------------------------------------------------------

class Form:
    """Represents one possible Prakrit output with a trace of applied rules."""

    def __init__(self, tokens: List[str], rules: List[tuple] = None):
        self.tokens: List[str] = tokens
        self.rules: List[tuple] = rules if rules is not None else []

    def copy(self) -> 'Form':
        return Form(tokens=self.tokens[:], rules=self.rules[:])

    def surface(self) -> str:
        return detokenize(self.tokens)

    def add(self, rule_id: str, desc: str) -> 'Form':
        f = self.copy()
        f.rules.append((rule_id, desc))
        return f


# ---------------------------------------------------------------------------
# Utilities for rule functions
# ---------------------------------------------------------------------------

def _obligatory(forms: List[Form], transform, rule_id: str, desc: str) -> List[Form]:
    """Apply transform to every form's tokens. Add rule if tokens changed."""
    result = []
    for f in forms:
        new_tokens = transform(f.tokens)
        if new_tokens != f.tokens:
            result.append(Form(tokens=new_tokens, rules=f.rules + [(rule_id, desc)]))
        else:
            result.append(f)
    return result


def _optional(forms: List[Form], transform, rule_id: str, desc: str) -> List[Form]:
    """Produce both original and transformed forms (optional / bahulam rule)."""
    result = []
    for f in forms:
        new_tokens = transform(f.tokens)
        result.append(f)  # always keep original
        if new_tokens != f.tokens:
            result.append(Form(tokens=new_tokens, rules=f.rules + [(rule_id, desc)]))
    return result


# ---------------------------------------------------------------------------
# PART 0 — Governing principles (meta, no token changes)
# ---------------------------------------------------------------------------
# 8.1.1 atha prākṛtam — excluded phonemes, no dual/dat.pl
# 8.1.2 bahulam — rules are optional/variable
# 8.1.3 ārṣam — Jaina canonical: all rules optional


# ---------------------------------------------------------------------------
# PART I — Vowel quantity
# ---------------------------------------------------------------------------

def rule_8_1_4(forms: List[Form]) -> List[Form]:
    """8.1.4 BAHULAM — In compounds, vowels may shorten or lengthen."""
    # No reliable way to detect compounds without morphological info; skip.
    return forms


def rule_8_1_10(forms: List[Form]) -> List[Form]:
    """8.1.10 BAHULAM — V+V → vowel elision (luk) at word boundaries (not applied here)."""
    return forms


# ---------------------------------------------------------------------------
# PART II — Final consonants
# ---------------------------------------------------------------------------

def _delete_final_consonant(tokens: List[str]) -> List[str]:
    if tokens and is_consonant(tokens[-1]):
        return tokens[:-1]
    return tokens


def rule_8_1_11(forms: List[Form]) -> List[Form]:
    """8.1.11 OBLIGATORY — Final C elided."""
    return _obligatory(forms, _delete_final_consonant, '8.1.11', 'Final C elided')


# ---------------------------------------------------------------------------
# PART III — Anusvāra
# ---------------------------------------------------------------------------

def _m_to_anusvara(tokens: List[str]) -> List[str]:
    """8.1.23: m# → ṃ (word-final m becomes anusvara)."""
    if tokens and tokens[-1] == 'm':
        return tokens[:-1] + ['ṃ']
    return tokens


def rule_8_1_23(forms: List[Form]) -> List[Form]:
    """8.1.23 OBLIGATORY — m# → ṃ."""
    return _obligatory(forms, _m_to_anusvara, '8.1.23', 'm# → ṃ (word-final m → anusvara)')


def _class_nasal_to_anusvara(tokens: List[str]) -> List[str]:
    """
    8.1.25: nasal (ṅ/ñ/ṇ/n/m) → ṃ before a VARGA consonant (the 25 obstruents
    ka–ma).  Semi-vowels, sibilants and h are NOT varga, so nasals before
    y/r/l/v/s/h are left unchanged.  Nasals before another nasal are also left
    unchanged (geminates like nn, mm stay as-is).

    Terminal Prakrit ādeśa clusters (mha, ṇha, nha from rules 8.2.74-76) are
    protected; but since 'h' is non-varga the varga check already excludes them.
    """
    all_nasals = {'ṅ', 'ñ', 'ṇ', 'n', 'm'}
    # The 25 varga consonants (ka-varga … pa-varga), digraphs treated as one unit
    _varga = frozenset({
        'k', 'kh', 'g', 'gh',           # ka-varga (ṅ excluded — it's a nasal)
        'c', 'ch', 'j', 'jh',           # ca-varga (ñ excluded)
        'ṭ', 'ṭh', 'ḍ', 'ḍh',          # ṭa-varga (ṇ excluded)
        't', 'th', 'd', 'dh',           # ta-varga (n excluded)
        'p', 'ph', 'b', 'bh',           # pa-varga (m excluded)
    })
    result = []
    i = 0
    changed = False
    while i < len(tokens):
        t = tokens[i]
        nxt = tokens[i + 1] if i < len(tokens) - 1 else None
        if (t in all_nasals
                and nxt is not None
                and unprotect(nxt) in _varga):   # use bare token — nxt may be a marked ādeśa
            result.append('ṃ')
            changed = True
        else:
            result.append(t)
        i += 1
    return result if changed else tokens


def rule_8_1_25(forms: List[Form]) -> List[Form]:
    """8.1.25 OBLIGATORY — nasal (ṅ/ñ/ṇ/n/m) + C → ṃ + C."""
    return _obligatory(forms, _class_nasal_to_anusvara,
                       '8.1.25', 'Nasal + C → ṃ (anusvāra before consonant)')


# ---------------------------------------------------------------------------
# PART V — Visarga
# ---------------------------------------------------------------------------

def _ah_to_o(tokens: List[str]) -> List[str]:
    """8.1.37: aḥ → o at word end (nom. sg. canonical form)."""
    if len(tokens) >= 2 and tokens[-2] == 'a' and tokens[-1] == 'ḥ':
        return tokens[:-2] + ['o']
    return tokens


def _visarga_drop(tokens: List[str]) -> List[str]:
    """Drop any remaining final or internal visarga."""
    if tokens and tokens[-1] == 'ḥ':
        return tokens[:-1]
    return tokens


def rule_8_1_37(forms: List[Form]) -> List[Form]:
    """8.1.37 OBLIGATORY — aḥ → o."""
    f2 = _obligatory(forms, _ah_to_o, '8.1.37', 'aḥ → o (nom. sg.)')
    # Drop any remaining ḥ
    return _obligatory(f2, _visarga_drop, '8.1.37', 'ḥ → ∅')


# ---------------------------------------------------------------------------
# PART VI — Initial-syllable vowel substitutions
# ---------------------------------------------------------------------------

def _vocalic_r_to_a(tokens: List[str]) -> List[str]:
    """8.1.126 OBLIGATORY — ṛ → a (default substitution for vocalic r)."""
    return ['a' if t == 'ṛ' else t for t in tokens]


def rule_8_1_126(forms: List[Form]) -> List[Form]:
    """8.1.126 OBLIGATORY — ṛ → a."""
    return _obligatory(forms, _vocalic_r_to_a, '8.1.126', 'ṛ → a (vocalic r → a)')


def _vocalic_r_to_i_opt(tokens: List[str]) -> List[str]:
    """8.1.128 OPTIONAL — ṛ → i (kṛpā-class)."""
    return ['i' if t == 'ṛ' else t for t in tokens]


def rule_8_1_128(forms: List[Form]) -> List[Form]:
    """8.1.128 OPTIONAL — ṛ → i."""
    return _optional(forms, _vocalic_r_to_i_opt, '8.1.128', 'ṛ → i (kṛpā-class, opt.)')


def _vocalic_r_to_u(tokens: List[str]) -> List[str]:
    """8.1.131 OBLIGATORY — ṛ → u (ṛtu-class)."""
    return ['u' if t == 'ṛ' else t for t in tokens]


def rule_8_1_131(forms: List[Form]) -> List[Form]:
    """8.1.131 OPTIONAL — ṛ → u (ṛtu-class)."""
    return _optional(forms, _vocalic_r_to_u, '8.1.131', 'ṛ → u (ṛtu-class, opt.)')


def _long_v_shorten_before_cc(tokens: List[str]) -> List[str]:
    """8.1.84 OBLIGATORY — Long V shortens before consonant cluster (CC)."""
    result = tokens[:]
    clusters = find_clusters(result)
    # For each cluster, check if immediately preceding token is a long vowel
    for start, end in clusters:
        if start > 0 and is_long_vowel(result[start - 1]):
            v = result[start - 1]
            if v in SHORTEN:
                result[start - 1] = SHORTEN[v]
    return result


def rule_8_1_84(forms: List[Form]) -> List[Form]:
    """8.1.84 OBLIGATORY — Long V → short V before CC."""
    return _obligatory(forms, _long_v_shorten_before_cc,
                       '8.1.84', 'Long V → short V before cluster (CC)')


def _ai_to_e(tokens: List[str]) -> List[str]:
    """8.1.148 OBLIGATORY — Initial ai → e."""
    # Apply to all ai (initial position per the adhikāra; bahulam for medial)
    return ['e' if t == 'ai' else t for t in tokens]


def rule_8_1_148(forms: List[Form]) -> List[Form]:
    """8.1.148 OBLIGATORY — ai → e."""
    return _obligatory(forms, _ai_to_e, '8.1.148', 'ai → e')


def _au_to_o(tokens: List[str]) -> List[str]:
    """8.1.159 OBLIGATORY — Initial au → o."""
    return ['o' if t == 'au' else t for t in tokens]


def rule_8_1_159(forms: List[Form]) -> List[Form]:
    """8.1.159 OBLIGATORY — au → o."""
    return _obligatory(forms, _au_to_o, '8.1.159', 'au → o')


# ---------------------------------------------------------------------------
# PART VII — Intervocalic single consonants (lenition)
# ---------------------------------------------------------------------------

def rule_8_1_177(forms: List[Form]) -> List[Form]:
    """
    8.1.177 BAHULAM — k, g, c, j, t, d, v → ∅ when intervocalic,
    single, non-initial. Branches once per elision site (independent choices)
    plus an all-elided branch for words with multiple sites.
    """
    LENITE_SET = {'k', 'g', 'c', 'j', 't', 'd', 'v'}
    result = []
    for f in forms:
        tokens = f.tokens
        elision_positions = [
            i for i, t in enumerate(tokens)
            if t in LENITE_SET and is_intervocalic_single(tokens, i)
        ]
        if not elision_positions:
            result.append(f)
            continue
        # Original form (no deletions)
        result.append(f)
        # One branch per position: delete only that consonant
        for pos in elision_positions:
            new_tokens = [t for i, t in enumerate(tokens) if i != pos]
            result.append(Form(
                tokens=new_tokens,
                rules=f.rules + [('8.1.177', f'{tokens[pos]} → ∅ intervocalic (bahulam)')]))
        # All-deleted branch (only if more than one site)
        if len(elision_positions) > 1:
            elide_set = set(elision_positions)
            new_tokens = [t for i, t in enumerate(tokens) if i not in elide_set]
            result.append(Form(
                tokens=new_tokens,
                rules=f.rules + [('8.1.177', 'Multiple C → ∅ intervocalic (bahulam)')]))
    return result


def rule_8_1_179_231(forms: List[Form]) -> List[Form]:
    """
    8.1.179 + 8.1.231: Intervocalic p.
    After a/ā: p → v (blocked from elision by 8.1.179; 8.1.231 gives v).
    Otherwise: p → ∅ (bahulam) or p → v.
    Both p→v and p→∅ are produced.
    """
    result = []
    for f in forms:
        tokens = f.tokens
        p_positions = [
            i for i, t in enumerate(tokens)
            if t == 'p' and is_intervocalic_single(tokens, i)
        ]
        if not p_positions:
            result.append(f)
            continue
        result.append(f)  # original
        # p → v
        v_tokens = tokens[:]
        for pos in p_positions:
            v_tokens[pos] = 'v'
        result.append(Form(tokens=v_tokens,
                           rules=f.rules + [('8.1.231', 'p → v intervocalic (8.1.179+8.1.231)')]))
        # p → ∅ (bahulam, only after non a/ā)
        elide_positions = [
            i for i in p_positions
            if i > 0 and tokens[i - 1] not in ('a', 'ā')
        ]
        if elide_positions:
            del_tokens = [t for i, t in enumerate(tokens)
                          if i not in set(elide_positions)]
            result.append(Form(tokens=del_tokens,
                               rules=f.rules + [('8.1.177+8.1.231', 'p → ∅ intervocalic (bahulam)')]))
    return result


def rule_8_1_187(forms: List[Form]) -> List[Form]:
    """8.1.187 OBLIGATORY — kh, gh, th, dh, bh → h (h-rule, intervocalic single).
    Protected ādeśa tokens (e.g. kh° from a cluster rule) are skipped — a
    token may only undergo one substitution.  The resulting h is itself marked
    protected so 8.1.267 cannot delete it."""
    ASPIRATES = {'kh', 'gh', 'th', 'dh', 'bh'}

    def transform(tokens):
        result = tokens[:]
        for i, t in enumerate(result):
            # Skip protected tokens — already an ādeśa, cannot substitute again
            if is_protected(t):
                continue
            if t in ASPIRATES and is_intervocalic_single(result, i):
                result[i] = protect('h')   # h° — protected from 8.1.267
        return result

    return _obligatory(forms, transform, '8.1.187', 'kh/gh/th/dh/bh → h (h-rule, intervocalic)')


def rule_8_1_195(forms: List[Form]) -> List[Form]:
    """8.1.195 OBLIGATORY — ṭ → ḍ intervocalically."""
    def transform(tokens):
        return ['ḍ' if (t == 'ṭ' and is_intervocalic_single(tokens, i)) else t
                for i, t in enumerate(tokens)]
    return _obligatory(forms, transform, '8.1.195', 'ṭ → ḍ intervocalic')


def rule_8_1_202(forms: List[Form]) -> List[Form]:
    """8.1.202 BAHULAM — ḍ → l intervocalically (many Jain texts also retain ḍ)."""
    def transform(tokens):
        return ['l' if (t == 'ḍ' and is_intervocalic_single(tokens, i)) else t
                for i, t in enumerate(tokens)]
    return _optional(forms, transform, '8.1.202', 'ḍ → l intervocalic (bahulam)')


def rule_8_1_228(forms: List[Form]) -> List[Form]:
    """8.1.228 OBLIGATORY — n → ṇ intervocalically (single, non-initial)."""
    def transform(tokens):
        result = tokens[:]
        for i, t in enumerate(result):
            if t == 'n' and is_intervocalic_single(result, i):
                result[i] = 'ṇ'
        return result
    return _obligatory(forms, transform, '8.1.228', 'n → ṇ intervocalic')


def rule_8_1_229(forms: List[Form]) -> List[Form]:
    """8.1.229 OPTIONAL — Word-initial n → ṇ."""
    def transform(tokens):
        if tokens and tokens[0] == 'n':
            result = tokens[:]
            result[0] = 'ṇ'
            return result
        return tokens
    return _optional(forms, transform, '8.1.229', 'Initial n → ṇ (opt.)')


def rule_8_1_237(forms: List[Form]) -> List[Form]:
    """8.1.237 OBLIGATORY — b → v intervocalically."""
    def transform(tokens):
        result = tokens[:]
        for i, t in enumerate(result):
            if t == 'b' and is_intervocalic_single(result, i):
                result[i] = 'v'
        return result
    return _obligatory(forms, transform, '8.1.237', 'b → v intervocalic')


def rule_8_1_245(forms: List[Form]) -> List[Form]:
    """8.1.245 BAHULAM — Word-initial y → j (many words retain initial y in poetry)."""
    def transform(tokens):
        if tokens and tokens[0] == 'y':
            result = tokens[:]
            result[0] = 'j'
            return result
        return tokens
    return _optional(forms, transform, '8.1.245', 'Initial y → j (bahulam)')


def rule_8_1_260(forms: List[Form]) -> List[Form]:
    """8.1.260 OBLIGATORY — ś, ṣ → s (universal; Prakrit has only one sibilant)."""
    def transform(tokens):
        return ['s' if t in ('ś', 'ṣ') else t for t in tokens]
    return _obligatory(forms, transform, '8.1.260', 'ś/ṣ → s (universal sibilant merge)')


# Additional Part-VII rules (intervocalic, added below rule_8_1_177 group)

def _optional_lenite(forms: List[Form], lenite_set: set,
                     rule_id: str, desc: str) -> List[Form]:
    """Bahulam elision of specific consonants in intervocalic single position."""
    result = []
    for f in forms:
        tokens = f.tokens
        positions = [i for i, t in enumerate(tokens)
                     if t in lenite_set and is_intervocalic_single(tokens, i)]
        if not positions:
            result.append(f)
            continue
        result.append(f)
        new_tokens = [t for i, t in enumerate(tokens) if i not in set(positions)]
        result.append(Form(tokens=new_tokens, rules=f.rules + [(rule_id, desc)]))
    return result


def rule_8_1_178(forms: List[Form]) -> List[Form]:
    """8.1.178 — Intervocalic single r is RETAINED in Prakrit.

    The bahulam r → ∅ deletion is not applied: when r stands alone between
    vowels it does not elide singularly, so this rule is a no-op (kept here to
    document the sūtra position). Left out of PIPELINE accordingly."""
    return forms


def rule_8_1_224(forms: List[Form]) -> List[Form]:
    """8.1.224 BAHULAM — Intervocalic j → y (alternate to j-deletion; rāja→rāya)."""
    def transform(tokens):
        result = tokens[:]
        for i, t in enumerate(result):
            if t == 'j' and is_intervocalic_single(result, i):
                result[i] = 'y'
        return result
    return _optional(forms, transform, '8.1.224', 'j → y intervocalic (bahulam)')


def rule_8_1_247(forms: List[Form]) -> List[Form]:
    """8.1.247 BAHULAM — Intervocalic single y → ∅ (māyā→māā, jaya→jaa)."""
    return _optional_lenite(forms, {'y'}, '8.1.247', 'y → ∅ intervocalic (bahulam)')


def rule_8_1_255(forms: List[Form]) -> List[Form]:
    """8.1.255 BAHULAM — Intervocalic single l → ∅ (kula→kua, śīla→sīa)."""
    return _optional_lenite(forms, {'l'}, '8.1.255', 'l → ∅ intervocalic (bahulam)')


def rule_8_1_261(forms: List[Form]) -> List[Form]:
    """8.1.261 BAHULAM — Intervocalic s → h (rasa→raha, nasa→naha).
    The resulting h is marked protected so 8.1.267 cannot further delete it —
    a token may only undergo one substitution per derivation."""
    def transform(tokens):
        result = tokens[:]
        for i, t in enumerate(result):
            if t == 's' and is_intervocalic_single(result, i):
                result[i] = protect('h')   # h° — protected from 8.1.267
        return result
    return _optional(forms, transform, '8.1.261', 's → h intervocalic (bahulam)')


def rule_8_1_267(forms: List[Form]) -> List[Form]:
    """8.1.267 BAHULAM — Intervocalic h → ∅ (gaha→gaa, lahu→lau)."""
    def transform(tokens):
        result = [t for i, t in enumerate(tokens)
                  if not (t == 'h' and is_intervocalic_single(tokens, i))]
        return result if len(result) != len(tokens) else tokens
    return _optional(forms, transform, '8.1.267', 'h → ∅ intervocalic (bahulam)')


# ---------------------------------------------------------------------------
# PART VIII — Consonant clusters: substitution
# ---------------------------------------------------------------------------

def _replace_cluster(tokens: List[str], old: List[str], new: List[str]) -> List[str]:
    """Replace first occurrence of consonant sequence `old` with `new`."""
    result = []
    i = 0
    while i < len(tokens):
        if tokens[i: i + len(old)] == old:
            result.extend(new)
            i += len(old)
        else:
            result.append(tokens[i])
            i += 1
    return result


def _replace_all_clusters(tokens: List[str], old: List[str], new: List[str]) -> List[str]:
    """Replace all occurrences of consonant sequence `old` with `new`."""
    result = []
    i = 0
    while i < len(tokens):
        if tokens[i: i + len(old)] == old:
            result.extend(new)
            i += len(old)
        else:
            result.append(tokens[i])
            i += 1
    return result


def _gem_inline(tokens, cluster_start, cluster_end, replacement):
    """
    Replace tokens[cluster_start:cluster_end] with `replacement` tokens,
    applying gemination to the first token of `replacement` if the preceding
    vowel allows it (8.2.89-93).
    e/o (guṇa) count as short in Prakrit → they allow gemination.
    Only ā/ī/ū/ṝ and ṃ block gemination (GEM_BLOCK_VOWELS, 8.2.92).

    The last token of the replacement is the ādeśa; it is marked as protected
    so no further substitution rule may act on it.
    """
    prev = tokens[cluster_start - 1] if cluster_start > 0 else None
    can_gem = (
        replacement
        and unprotect(replacement[0]) not in ('r', 'h')  # 8.2.93
        and prev is not None
        and is_vowel(prev)                                # must follow a vowel
        and prev not in GEM_BLOCK_VOWELS                  # not ā/ī/ū/ṝ
        and prev != 'ṃ'                                   # not anusvāra (8.2.92)
    )
    if can_gem:
        geminated = list(double_consonant(replacement[0])) + list(replacement[1:])
    else:
        geminated = list(replacement)
    # Mark the ādeśa (last element) as protected
    if geminated:
        geminated[-1] = protect(geminated[-1])
    return tokens[:cluster_start] + geminated + tokens[cluster_end:]


def rule_8_2_3(forms: List[Form]) -> List[Form]:
    """8.2.3 OBLIGATORY — kṣ → kkh (default) or cch (alternate).
    Matches k+ṣ and k+s (since 8.1.260 ṣ→s runs first in the pipeline)."""
    result = []
    for f in forms:
        tokens = f.tokens
        # Find all k+ṣ or k+s clusters (ṣ already converted to s by 8.1.260)
        indices = []
        for i in range(len(tokens) - 1):
            if tokens[i] == 'k' and tokens[i + 1] in ('ṣ', 's'):
                indices.append(i)
        if not indices:
            result.append(f)
            continue

        # kh variant (default)
        t_kh = tokens[:]
        offset = 0
        for i in indices:
            j = i + offset
            t_kh = _gem_inline(t_kh, j, j + 2, ['kh'])
            offset += len(double_consonant('kh')) - 2

        # ch variant
        t_ch = tokens[:]
        offset = 0
        for i in indices:
            j = i + offset
            t_ch = _gem_inline(t_ch, j, j + 2, ['ch'])
            offset += len(double_consonant('ch')) - 2

        result.append(Form(tokens=t_kh,
                           rules=f.rules + [('8.2.3', 'kṣ → kkh (default)')]))
        result.append(Form(tokens=t_ch,
                           rules=f.rules + [('8.2.3', 'kṣ → cch (alternate)')]))
    return result


def _gem_cluster_sub(tokens, old, new, rule_id, desc):
    """Replace all occurrences of `old` cluster with `new`, applying inline gemination.
    The ādeśa (last token of the replacement) is marked as protected so no
    subsequent substitution rule may act on it."""
    result = []
    i = 0
    changed = False
    while i < len(tokens):
        if tokens[i:i + len(old)] == old:
            prev = result[-1] if result else None
            can_gem = (
                new
                and unprotect(new[0]) not in ('r', 'h')
                and prev is not None
                and is_vowel(prev)
                and prev not in GEM_BLOCK_VOWELS
                and prev != 'ṃ'
            )
            if can_gem:
                gems = list(double_consonant(new[0])) + list(new[1:])
            else:
                gems = list(new)
            # Mark the ādeśa (last token) as protected
            if gems:
                gems[-1] = protect(gems[-1])
            result.extend(gems)
            i += len(old)
            changed = True
        else:
            result.append(tokens[i])
            i += 1
    return result if changed else tokens


def rule_8_2_13(forms: List[Form]) -> List[Form]:
    """8.2.13 OBLIGATORY — tya → cca (geminated)."""
    def transform(tokens):
        return _gem_cluster_sub(tokens, ['t', 'y'], ['c'], '8.2.13', 'tya→cca')
    return _obligatory(forms, transform, '8.2.13', 'tya → cca (tya-cluster)')


def rule_8_2_21(forms: List[Form]) -> List[Form]:
    """8.2.21 OBLIGATORY — śca → ccha (after short vowel).
    After 8.1.260 has run, ś is already s, so we match the s+c cluster."""
    def transform(tokens):
        return _gem_cluster_sub(tokens, ['s', 'c'], ['ch'], '8.2.21', 'śca→ccha')
    return _obligatory(forms, transform, '8.2.21', 'śca → ccha')


def rule_8_2_24(forms: List[Form]) -> List[Form]:
    """8.2.24 OBLIGATORY — dya, yya, rya → jja (geminated)."""
    def transform(tokens):
        t = _gem_cluster_sub(tokens, ['d', 'y'], ['j'], '8.2.24', 'dya→jja')
        t = _gem_cluster_sub(t, ['y', 'y'], ['j'], '8.2.24', 'yya→jja')
        t = _gem_cluster_sub(t, ['r', 'y'], ['j'], '8.2.24', 'rya→jja')
        return t
    return _obligatory(forms, transform, '8.2.24', 'dya/yya/rya → jja')


def rule_8_2_26(forms: List[Form]) -> List[Form]:
    """8.2.26 OBLIGATORY — dhya, hya → jha (→ jjha)."""
    def transform(tokens):
        t = _gem_cluster_sub(tokens, ['d', 'h', 'y'], ['jh'], '8.2.26', 'dhya→jjha')
        t = _gem_cluster_sub(t, ['h', 'y'], ['jh'], '8.2.26', 'hya→jjha')
        return t
    return _obligatory(forms, transform, '8.2.26', 'dhya/hya → jha')


def rule_8_2_34(forms: List[Form]) -> List[Form]:
    """8.2.34 OBLIGATORY — ṣṭa/ṣṭha → ṭṭha. Handles both s+ṭ and s+ṭh clusters
    (the latter occurs in pratiṣṭhāna-type words after 8.1.260 ṣ→s)."""
    def transform(tokens):
        t = _gem_cluster_sub(tokens, ['s', 'ṭ'], ['ṭh'], '8.2.34', 'ṣṭ→ṭṭh')
        t = _gem_cluster_sub(t, ['s', 'ṭh'], ['ṭh'], '8.2.34', 'ṣṭh→ṭṭh')
        return t
    return _obligatory(forms, transform, '8.2.34', 'ṣṭ/ṣṭh → ṭṭha')


def rule_8_2_42(forms: List[Form]) -> List[Form]:
    """8.2.42 OBLIGATORY — mna, jña → ṇṇa."""
    def transform(tokens):
        t = _gem_cluster_sub(tokens, ['m', 'n'], ['ṇ'], '8.2.42', 'mna→ṇṇa')
        t = _gem_cluster_sub(t, ['j', 'ñ'], ['ṇ'], '8.2.42', 'jña→ṇṇa')
        t = _gem_cluster_sub(t, ['j', 'n'], ['ṇ'], '8.2.42', 'jna→ṇṇa')
        return t
    return _obligatory(forms, transform, '8.2.42', 'mna/jña → ṇṇa')


def rule_8_2_45(forms: List[Form]) -> List[Form]:
    """8.2.45 OBLIGATORY — sta → tha → ttha (except samasta, stamba)."""
    def transform(tokens):
        # sta → 'th' digraph; gemination applied inline
        result = []
        i = 0
        while i < len(tokens):
            if tokens[i] == 's' and i + 1 < len(tokens) and tokens[i + 1] == 't':
                prev = tokens[i - 1] if i > 0 else None
                can_gem = (prev is not None and is_vowel(prev)
                           and prev not in GEM_BLOCK_VOWELS and prev != 'ṃ')
                if can_gem:
                    result.extend(['t', protect('th')])   # ttha (gem-copy + protected ādeśa)
                else:
                    result.append(protect('th'))           # just tha (protected ādeśa)
                i += 2
            else:
                result.append(tokens[i])
                i += 1
        return result
    return _obligatory(forms, transform, '8.2.45', 'sta → ttha (sta-cluster → geminated aspirate)')


def rule_8_2_52(forms: List[Form]) -> List[Form]:
    """8.2.52 OBLIGATORY — ḍma, kma → pp."""
    def transform(tokens):
        t = _gem_cluster_sub(tokens, ['ḍ', 'm'], ['p'], '8.2.52', 'ḍma→pp')
        t = _gem_cluster_sub(t, ['k', 'm'], ['p'], '8.2.52', 'kma→pp')
        return t
    return _obligatory(forms, transform, '8.2.52', 'ḍma/kma → pp')


def rule_8_2_53(forms: List[Form]) -> List[Form]:
    """8.2.53 OBLIGATORY — spa → pha (→ ppha)."""
    def transform(tokens):
        return _gem_cluster_sub(tokens, ['s', 'p'], ['ph'], '8.2.53', 'spa→ppha')
    return _obligatory(forms, transform, '8.2.53', 'spa → ph (→ ppha)')


def rule_8_2_61(forms: List[Form]) -> List[Form]:
    """8.2.61 OBLIGATORY — nma → mm."""
    def transform(tokens):
        return _gem_cluster_sub(tokens, ['n', 'm'], ['m'], '8.2.61', 'nma→mm')
    return _obligatory(forms, transform, '8.2.61', 'nma → mm')


def rule_8_2_9(forms: List[Form]) -> List[Form]:
    """8.2.9 OBLIGATORY — sth → ṭṭha (sthāna-class; precedes sta→ttha rule)."""
    def transform(tokens):
        return _gem_cluster_sub(tokens, ['s', 'th'], ['ṭh'], '8.2.9', 'sth→ṭṭha')
    return _obligatory(forms, transform, '8.2.9', 'sth → ṭṭha (sthāna-class)')


def rule_8_2_29(forms: List[Form]) -> List[Form]:
    """8.2.29 OBLIGATORY — ny → ñña (palatal nasal assimilation)."""
    def transform(tokens):
        return _gem_cluster_sub(tokens, ['n', 'y'], ['ñ'], '8.2.29', 'ny→ñña')
    return _obligatory(forms, transform, '8.2.29', 'ny → ñña (palatal assimilation)')


def rule_8_2_43(forms: List[Form]) -> List[Form]:
    """8.2.43-44 OBLIGATORY — kna/gna → ṇṇa (velar + nasal → retroflex geminate)."""
    def transform(tokens):
        t = _gem_cluster_sub(tokens, ['k', 'n'], ['ṇ'], '8.2.43', 'kna→ṇṇa')
        t = _gem_cluster_sub(t,        ['g', 'n'], ['ṇ'], '8.2.44', 'gna→ṇṇa')
        return t
    return _obligatory(forms, transform, '8.2.43-44', 'kna/gna → ṇṇa')


def rule_8_2_63(forms: List[Form]) -> List[Form]:
    """8.2.63 OPTIONAL — rya → ra (brahmacarya-class; vs 8.2.24 → ja)."""
    def transform(tokens):
        return _replace_all_clusters(tokens, ['r', 'y'], ['r'])
    return _optional(forms, transform, '8.2.63', 'rya → ra (opt.; brahmacarya-class)')


def rule_8_2_74(forms: List[Form]) -> List[Form]:
    """8.2.74 OBLIGATORY — hma/sma → mha (no further gemination — mha is terminal)."""
    def transform(tokens):
        t = _replace_all_clusters(tokens, ['h', 'm'], ['m', 'h'])
        t = _replace_all_clusters(t, ['s', 'm'], ['m', 'h'])
        return t
    return _obligatory(forms, transform, '8.2.74', 'hma/sma → mha')


def rule_8_2_75(forms: List[Form]) -> List[Form]:
    """8.2.75 OBLIGATORY — sna/ṣṇa/hna → ṇha (terminal Prakrit cluster)."""
    def transform(tokens):
        t = _replace_all_clusters(tokens, ['s', 'n'], ['ṇ', 'h'])
        t = _replace_all_clusters(t, ['h', 'n'], ['ṇ', 'h'])
        t = _replace_all_clusters(t, ['s', 'ṇ'], ['ṇ', 'h'])
        t = _replace_all_clusters(t, ['h', 'ṇ'], ['ṇ', 'h'])
        return t
    return _obligatory(forms, transform, '8.2.75', 'sna/śna/ṣṇa/hna → ṇha')


def rule_8_2_76(forms: List[Form]) -> List[Form]:
    """8.2.76 OBLIGATORY — hla/hra → lha."""
    def transform(tokens):
        t = _replace_all_clusters(tokens, ['h', 'r'], ['l', 'h'])
        t = _replace_all_clusters(t, ['h', 'l'], ['l', 'h'])
        return t
    return _obligatory(forms, transform, '8.2.76', 'hla/hra → lha')


# ---------------------------------------------------------------------------
# PART IX — Cluster reduction, gemination, epenthesis
# ---------------------------------------------------------------------------

# Aspirate geminate pairs (k+kh etc.) produced by 8.2.90 — must not be re-reduced
_ASPIRATE_GEMINATES = frozenset({
    ('k', 'kh'), ('g', 'gh'), ('c', 'ch'), ('j', 'jh'),
    ('ṭ', 'ṭh'), ('ḍ', 'ḍh'), ('t', 'th'), ('d', 'dh'),
    ('p', 'ph'), ('b', 'bh'),
})

# Terminal Prakrit clusters from 8.2.74-76 that must not be reduced further
_PROTECTED_CLUSTERS = frozenset({
    ('m', 'h'), ('ṇ', 'h'), ('l', 'h'), ('n', 'h'),
})


def rule_8_2_77_79(forms: List[Form]) -> List[Form]:
    """
    8.2.77 — Upper member (k,g,ṭ,ḍ,t,d,p,ś,ṣ,s) + C → elide upper, double lower.
    8.2.78 — C₁ + lower (m,n,y) → elide lower, double upper C₁.
    8.2.79 — r, l, v in any cluster → elided; survivor doubled if eligible.
    Gemination is applied INLINE (8.2.89-93): only after short V, never r/h, never after long V/ṃ.
    Aspirate geminates (k+kh etc.) and terminal clusters (mha, ṇha, lha) are preserved.
    """

    def reduce_once(tokens):
        result = []
        i = 0
        changed = False

        while i < len(tokens):
            t = tokens[i]

            if (is_consonant(t)
                    and i + 1 < len(tokens)
                    and is_consonant(tokens[i + 1])):
                c1, c2 = t, tokens[i + 1]
                # Use bare (unprotected) forms for all logic; preserve markers in result
                c1b, c2b = unprotect(c1), unprotect(c2)

                # Skip valid Prakrit geminates and protected clusters
                if (c1b == c2b
                        or (c1b, c2b) in _ASPIRATE_GEMINATES
                        or (c1b, c2b) in _PROTECTED_CLUSTERS):
                    result.append(c1)
                    i += 1
                    continue

                prev = result[-1] if result else None

                def gem_and_add(survivor, _prev=prev):
                    if (unprotect(survivor) not in ('r', 'h')
                            and _prev is not None
                            and is_vowel(_prev)
                            and _prev not in GEM_BLOCK_VOWELS
                            and _prev != 'ṃ'):
                        result.extend(double_consonant(survivor))
                    else:
                        result.append(survivor)

                # 8.2.79: c1 is r/l/v → elide c1, keep (and gem) c2
                if c1b in CLUSTER_ALWAYS_ELIDE:
                    gem_and_add(c2)
                    changed = True
                    i += 2
                    continue

                # 8.2.79: c2 is r/l/v → elide c2, keep (and gem) c1
                if c2b in CLUSTER_ALWAYS_ELIDE:
                    gem_and_add(c1)
                    changed = True
                    i += 2
                    continue

                # 8.2.78: c2 is m/n/y → elide c2, keep (and gem) c1
                if c2b in LOWER_ELIDE:
                    gem_and_add(c1)
                    changed = True
                    i += 2
                    continue

                # 8.2.77: c1 in UPPER_ELIDE → elide c1, keep (and gem) c2
                if c1b in UPPER_ELIDE:
                    gem_and_add(c2)
                    changed = True
                    i += 2
                    continue

                # Fallback: elide c1, keep (and gem) c2
                gem_and_add(c2)
                changed = True
                i += 2
                continue

            result.append(t)
            i += 1

        return result, changed

    def reduce_clusters(tokens):
        result = tokens[:]
        for _ in range(10):
            result, changed = reduce_once(result)
            if not changed:
                break
        return result

    return _obligatory(forms, reduce_clusters, '8.2.77-79',
                       'Cluster reduction: r/l/v elided, upper member elided, '
                       'lower member (m/n/y) elided; gemination inline (8.2.89-93)')


def rule_ya_shruti(forms: List[Form]) -> List[Form]:
    """
    Ya-śruti (y-epenthesis): optionally insert glide 'y' between two adjacent
    vowels (hiatus) created by consonant elision.  Applies after all elision
    rules. The form without the glide is always preserved (bahulam).
    Example: rāa (← rāja) → rāya; dea → deya; loa → loya.
    """
    def insert_y(tokens: List[str]) -> List[str]:
        result = []
        i = 0
        while i < len(tokens):
            result.append(tokens[i])
            if (is_vowel(tokens[i])
                    and i + 1 < len(tokens)
                    and is_vowel(tokens[i + 1])):
                result.append('y')
            i += 1
        return result

    return _optional(forms, insert_y, 'ya-śruti',
                     'V+V hiatus → V+y+V (ya-śruti, y-glide epenthesis)')


# ---------------------------------------------------------------------------
# Aggregate pipelines
# ---------------------------------------------------------------------------

# Ordered rule pipeline
PIPELINE: List[Callable[[List[Form]], List[Form]]] = [
    # 0. Universal sibilant merge (must be first; affects cluster detection)
    rule_8_1_260,

    # 1. Diphthong / vowel substitutions
    rule_8_1_148,   # ai → e
    rule_8_1_159,   # au → o
    rule_8_1_126,   # ṛ → a (default)
    rule_8_1_131,   # ṛ → u (optional alternate)
    rule_8_1_128,   # ṛ → i (optional alternate)

    # 2. Long V shortens before cluster
    rule_8_1_84,

    # 3. Universal initial consonant normalizations (dhuṇḍhikā phase 3:
    #    these apply to the root-initial consonant before cluster rules see it)
    rule_8_1_245,   # initial y → j (bahulam)
    rule_8_1_229,   # initial n → ṇ (opt.)

    # 4. Cluster substitutions (specific, must precede general reduction)
    # kṣ MUST run before sma/sna rules — otherwise the 's' (from ṣ→s) in kṣm/kṣn
    # is grabbed by rule_8_2_74/75 before rule_8_2_3 can handle the kṣ cluster.
    rule_8_2_3,     # kṣ → kkh/cch  (FIRST: protects kṣm, kṣn, kṣṇ sequences)
    rule_8_2_74,    # hma/sma → mha
    rule_8_2_75,    # sna/ṣṇa/hna → ṇha
    rule_8_2_76,    # hla/hra → lha
    rule_8_2_13,    # tya → ca
    rule_8_2_21,    # śca → ccha  (after tya so s+c from non-śca is not affected)
    rule_8_2_63,    # rya → ra (optional, BEFORE 8.2.24 so both sura & sujja forms live)
    rule_8_2_24,    # dya/rya/yya → ja  (obligatory; 8.2.63 fork already made above)
    rule_8_2_26,    # dhya/hya → jha
    rule_8_2_34,    # ṣṭ/ṣṭh → ṭṭh
    rule_8_2_42,    # mna/jña → ṇ
    rule_8_2_9,     # sth → ṭṭha  (BEFORE sta rule)
    rule_8_2_45,    # sta → ttha
    rule_8_2_29,    # ny → ñña    (BEFORE general reduction)
    rule_8_2_43,    # kna/gna → ṇṇa
    rule_8_2_52,    # ḍma/kma → p
    rule_8_2_53,    # spa → pha
    rule_8_2_61,    # nma → m

    # 5. Anusvāra BEFORE cluster reduction: nasal+C → ṃ+C so that nta/nda/mba
    #    clusters are not wrongly reduced by 8.2.77-79.
    rule_8_1_25,    # nasal (n/m/ṅ/ñ/ṇ) + C → ṃ + C

    # 6. General cluster reduction (nasals already converted → safe)
    rule_8_2_77_79,

    # 7. Final consonant deletion (after cluster work, stem is cleaner)
    rule_8_1_11,

    # 8. Word-final m → ṃ
    rule_8_1_23,    # m# → ṃ

    # 9. Visarga
    rule_8_1_37,    # aḥ → o

    # 10. Intervocalic single consonant rules (Part VII)
    rule_8_1_177,      # k/g/c/j/t/d/v → ∅ (bahulam)
    rule_8_1_179_231,  # p → v / ∅
    rule_8_1_187,      # kh/gh/th/dh/bh → h
    rule_8_1_195,      # ṭ → ḍ
    rule_8_1_202,      # ḍ → l (bahulam)
    rule_8_1_224,      # j → y (bahulam)
    rule_8_1_228,      # n → ṇ
    rule_8_1_237,      # b → v
    # rule_8_1_178 removed: intervocalic single r is retained (no bahulam r → ∅)
    rule_8_1_247,      # y → ∅ (bahulam) [8.1.247]
    rule_8_1_255,      # l → ∅ (bahulam) [8.1.255]
    rule_8_1_261,      # s → h (bahulam) [8.1.261]
    rule_8_1_267,      # h → ∅ (bahulam) [8.1.267]

    # 11. Ya-śruti: optional y-glide between adjacent vowels (hiatus resolution)
    rule_ya_shruti,
]
