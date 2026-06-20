"""
Sanskrit→Prakrit translation engine.
Orchestrates the rule pipeline and exception lookup.
"""

from typing import List, Tuple, Dict, Optional
from .utils import tokenize, detokenize, strip_vibhakti
from .exceptions import lookup
from .rules import Form, PIPELINE, rule_ya_shruti


def deduplicate(forms: List[Form]) -> List[Form]:
    """Keep only one Form per unique surface string (first occurrence wins)."""
    seen: Dict[str, bool] = {}
    result = []
    for f in forms:
        s = f.surface()
        if s and s not in seen:
            seen[s] = True
            result.append(f)
    return result


def _apply_pipeline(tokens: List[str]) -> List[Form]:
    """Run the full rule pipeline on a token list, returning all possible forms."""
    forms = [Form(tokens=tokens)]
    for rule_fn in PIPELINE:
        forms = rule_fn(forms)
        # Cap forms to prevent combinatorial explosion (bahulam branches fast)
        if len(forms) > 64:
            forms = deduplicate(forms)[:64]
    return deduplicate(forms)


def _is_bahulam(f: Form) -> bool:
    """A form is bahulam-derived if any rule in its trace is an optional/bahulam rule."""
    return any('bahulam' in desc.lower() for _, desc in f.rules)


def _order_bahulam_last(forms: List[Form]) -> List[Form]:
    """Stable-sort forms so obligatory-only forms come first and any form
    produced via a bahulam (optional) rule is kept at the end, in order."""
    return sorted(forms, key=_is_bahulam)


def _soften_k_forms(forms: List[Form]) -> List[Form]:
    """
    For each form containing 'k', produce an additional form with k→g (voicing).
    The original forms are kept; softened forms are appended with _softened=True.
    """
    extra = []
    for f in forms:
        if 'k' in f.tokens:
            new_tokens = ['g' if t == 'k' else t for t in f.tokens]
            sf = Form(tokens=new_tokens,
                      rules=f.rules + [('soften', 'k → g (voiced softening)')])
            sf._softened = True
            extra.append(sf)
    # Re-deduplicate combined list
    return deduplicate(forms + extra)


class TranslationResult:
    """Container for translation output."""

    def __init__(self,
                 original_input: str,
                 stem: str,
                 vibhakti_stripped: Optional[str],
                 forms: List[Form],
                 from_exception: bool = False):
        self.original_input = original_input
        self.stem = stem
        self.vibhakti_stripped = vibhakti_stripped
        self.forms = forms
        self.from_exception = from_exception

    def as_dict(self) -> dict:
        return {
            'original_input': self.original_input,
            'stem': self.stem,
            'vibhakti_stripped': self.vibhakti_stripped,
            'from_exception': self.from_exception,
            'has_k': any('k' in f.surface() for f in self.forms),
            'forms': [
                {
                    'prakrit': f.surface(),
                    'rules': f.rules,
                    'softened': getattr(f, '_softened', False),
                }
                for f in self.forms
            ],
        }


class SanskritPrakritTranslator:
    """
    Main translator class.

    Usage:
        translator = SanskritPrakritTranslator()
        result = translator.translate('rāja')
        for form in result.forms:
            print(form.surface(), form.rules)
    """

    def translate(self, word: str, soften_k: bool = False) -> TranslationResult:
        word = word.strip()
        if not word:
            return TranslationResult(word, word, None, [])

        # Step 1: Vibhakti stripping
        stem, stripped_ending = strip_vibhakti(word)

        # Step 2: Check lexical exceptions (on both the original and stripped stem)
        for candidate in [stem, word]:
            exc = lookup(candidate)
            if exc:
                forms = []
                for prakrit, rule_ids, desc in exc:
                    rule_trace = [(rid, '') for rid in rule_ids]
                    if desc:
                        rule_trace.append(('lexical', desc))
                    forms.append(Form(tokens=tokenize(prakrit), rules=rule_trace))
                # Apply ya-śruti to exception forms that have hiatus
                forms = rule_ya_shruti(forms)
                forms = deduplicate(forms)
                if soften_k:
                    forms = _soften_k_forms(forms)
                forms = _order_bahulam_last(forms)
                return TranslationResult(
                    original_input=word,
                    stem=candidate,
                    vibhakti_stripped=stripped_ending,
                    forms=forms,
                    from_exception=True,
                )

        # Step 3: Run the rule pipeline
        tokens = tokenize(stem)
        if not tokens:
            return TranslationResult(word, stem, stripped_ending, [])

        forms = _apply_pipeline(tokens)
        if soften_k:
            forms = _soften_k_forms(forms)
        forms = _order_bahulam_last(forms)
        return TranslationResult(
            original_input=word,
            stem=stem,
            vibhakti_stripped=stripped_ending,
            forms=forms,
            from_exception=False,
        )
