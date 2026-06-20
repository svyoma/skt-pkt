# Hemacandra's Sanskrit → Prakrit Translator

A rule-based web application that derives Prakrit forms from Sanskrit stems using the complete phonological grammar of **Hemacandra's *Siddhahemaśabdānuśāsana***, Adhyāya VIII, Pādas 1–2 (489 sūtras).

Enter any Sanskrit stem in IAST and receive all phonologically valid Prakrit forms, each annotated with the exact sūtra numbers applied.

---

## What This Does

Sanskrit and the Prakrits (Māhārāṣṭrī, Ardhamāgadhī, Śaurasenī, Apabhraṃśa) share a systematic phonological relationship codified by the Jain scholar **Hemacandra** (c. 1088–1172 CE) in his grammar. Each sūtra is a rule license: under the *bahulam* principle (8.1.2), rules are not commands but options — so a single Sanskrit word can produce several equally valid Prakrit forms.

**Examples:**

| Sanskrit | Prakrit forms | Rules applied |
|----------|--------------|---------------|
| rāja     | rāja, rāa, rāya | retained / 8.1.177 (j→∅) / 8.1.224 (j→y) |
| dharma   | dhamma | 8.2.79 r-elision, 8.2.89 gemination |
| kṛṣṇa   | kaṇha, kiṇha | 8.1.126 (ṛ→a) or 8.1.128 (ṛ→i), 8.2.75 (kṣṇ→ṇh) |
| vṛṣabha  | vahaha, vasaha | 8.1.126, 8.2.79, 8.1.187 (bh→h), 8.1.177 |
| satya    | sacca | 8.2.13 (tya→ca), 8.2.89 (gemination) |
| hasta    | hattha | 8.2.45 (sta→ttha) |

---

## Linguistic Background

### Hemacandra's Grammar

The *Siddhahemaśabdānuśāsana* (c. 1150 CE) is the most comprehensive Prakrit grammar written in Sanskrit. Adhyāya 8 covers Prākrit, and Pādas 1–2 contain the complete phonological rule set for transforming Sanskrit words into Prakrit. The grammar is cited by the auto-commentary *Dhuṇḍhikā* (also called *Vyutpatti-Dīpikā*), which provides 3,304 worked derivation examples — the source used to determine correct rule ordering in this implementation.

### Key Principles

**Bahulam (8.1.2)** — "Variably." Rules are licenses, not commands. When a sūtra says "x → y," both the original and the transformed form are valid. The engine produces all valid variants.

**Nipātana** — Truly irregular forms listed explicitly in the grammar (sūtras 8.1.17–8.1.21, 8.2.125–8.2.144). Examples: *vṛkṣa* → *rukkha*, *gṛha* → *ghara*, *snuṣā* → *suṇhā*. These override the rule engine.

**Single-substitution principle** — A phoneme position undergoes at most one substitution per derivation. If *kṣ* becomes *kh* (8.2.3), that *kh* is protected and cannot further become *h* (8.1.187). Gemination is the only permitted follow-on operation.

**IAST** (International Alphabet of Sanskrit Transliteration) — The input/output format. Uses Unicode diacritics: ā ī ū ṛ ṝ ḷ ṃ ḥ ś ṣ ñ ṅ ṇ ḍ ṭ etc.

---

## Rule Pipeline

The engine applies 46 rules across 11 ordered phases, derived from the *Dhuṇḍhikā* corpus:

| Phase | Rules | Description |
|-------|-------|-------------|
| 0 | 8.1.260 | ś/ṣ → s (universal sibilant merger — must be first) |
| 1 | 8.1.148, 8.1.159, 8.1.126, 8.1.131, 8.1.128 | Vowel substitutions (ai→e, au→o, ṛ→a/i/u) |
| 2 | 8.1.84 | Long vowel shortens before consonant cluster |
| 3 | 8.1.245, 8.1.229 | Initial y→j, initial n→ṇ |
| 4 | 8.2.3, 8.2.74–76, 8.2.13, 8.2.21, 8.2.63, 8.2.24, 8.2.26, 8.2.34, 8.2.42, 8.2.9, 8.2.45, 8.2.29, 8.2.43, 8.2.52, 8.2.53, 8.2.61 | Specific cluster substitutions |
| 5 | 8.1.25 | Class nasal → anusvāra before varga consonant |
| 6 | 8.2.77–79 | General cluster reduction with inline gemination (8.2.89–93) |
| 7 | 8.1.11 | Final consonant deletion |
| 8 | 8.1.23 | Word-final m → ṃ |
| 9 | 8.1.37 | Visarga -aḥ → -o |
| 10 | 8.1.177, 8.1.179+231, 8.1.187, 8.1.195, 8.1.202, 8.1.224, 8.1.228, 8.1.237, 8.1.178, 8.1.247, 8.1.255, 8.1.261, 8.1.267 | Intervocalic single consonant rules |
| 11 | ya-śruti | Optional y-glide between adjacent vowels (hiatus) |

### Key Rules Explained

- **8.1.177** — Core lenition: k, g, c, j, t, d, v → ∅ between vowels (bahulam). Each site branches independently.
- **8.1.187** — H-rule: kh, gh, th, dh, bh → h intervocalically (obligatory). Output *h* is protected.
- **8.1.261** — s → h intervocalically (bahulam). Output *h* is protected (cannot cascade to deletion).
- **8.1.267** — h → ∅ intervocalically (bahulam). Only original Sanskrit *h*, not substituted *h*.
- **8.2.3** — kṣ → kkh (default) or cch (alternate). Runs first in Phase 4.
- **8.2.45** — sta → ttha (cluster assimilation with gemination).
- **8.2.77–79** — General cluster reduction: r/l/v always elide; upper member (k,g,t,d,p,s…) elides; lower member (m,n,y) elides; survivor geminates if eligible.
- **8.2.89–93** — Gemination is applied inline within each cluster rule. Blocks: long vowels ā/ī/ū/ṝ and anusvāra ṃ. Note: *e* and *o* (guṇa vowels) count as short and DO allow gemination.

### Exception System

Entries in `translator/exceptions.py` fall into three categories:

1. **Nipātana** — Grammatically irregular forms, explicitly listed by Hemacandra. Must remain as exceptions regardless of pipeline improvements (e.g., *vṛkṣa* → *rukkha*, *gṛha* → *ghara*).

2. **Engine patches** — Words where the pipeline gives the wrong result due to an implementation limitation. These are documented inline (e.g., *agni*: pipeline over-applies 8.2.43 to gn→ṇṇ, but gni should give *aggi* via 8.2.78).

3. **Redundant** — Words previously hard-coded but now correctly handled by the pipeline. Removed to allow the engine to produce all valid bahulam forms (e.g., *rāja*, *loka*, *deva* were removed because the pipeline now correctly generates all three forms each).

---

## Project Structure

```
hemacandra-translator/
├── app.py                  # Flask routes (local development entry point)
├── api/
│   └── index.py            # Vercel serverless entry point
├── translator/
│   ├── __init__.py
│   ├── utils.py            # IAST tokenizer, phoneme sets, protection marker
│   ├── rules.py            # 46 rule functions + PIPELINE list
│   ├── exceptions.py       # Nipātana + engine patches
│   └── engine.py           # Orchestrator: exception lookup → pipeline → dedup
├── templates/
│   └── index.html          # Single-page UI with Jinja2 macros
├── static/
│   └── style.css           # Earthy parchment aesthetic
├── vercel.json             # Vercel deployment configuration
├── requirements.txt        # Python dependencies
├── .gitignore
└── LICENSE                 # MIT
```

---

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/hemacandra-translator.git
cd hemacandra-translator

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://localhost:5001` in your browser.

### API Usage

The translator exposes a JSON API:

```bash
curl -X POST http://localhost:5001/translate \
  -H "Content-Type: application/json" \
  -d '{"word": "rāja"}'
```

Response:

```json
{
  "original_input": "rāja",
  "stem": "rāja",
  "vibhakti_stripped": null,
  "from_exception": false,
  "has_k": false,
  "forms": [
    {
      "prakrit": "rāja",
      "rules": [],
      "softened": false
    },
    {
      "prakrit": "rāa",
      "rules": [["8.1.177", "j → ∅ intervocalic (bahulam)"]],
      "softened": false
    },
    {
      "prakrit": "rāya",
      "rules": [["8.1.224", "j → y intervocalic (bahulam)"]],
      "softened": false
    }
  ]
}
```

Optional parameter `soften_k: true` adds voiced variants (k → g) for all forms containing k.

The UI also supports a non-AJAX form endpoint at `POST /translate_form` for progressive enhancement.

---

## Deployment on Vercel

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/hemacandra-translator)

### Manual Deploy

1. Install the Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project root and follow the prompts.
3. For subsequent deploys: `vercel --prod`

The `vercel.json` routes all requests through `api/index.py`, which re-exports the Flask `app`. Static files and templates are bundled with the serverless function automatically.

> **Note:** Vercel's free tier has a 250 MB function size limit and 10-second execution timeout. This app is well within both limits (pure Python, no ML models).

---

## Technical Notes

### Ādeśa Protection Marker

The single-substitution principle is enforced at the token level. When a cluster rule substitutes a phoneme (e.g., kṣ → kh via 8.2.3), the output token is marked with a Unicode degree symbol: `kh°`. Subsequent rules skip marked tokens:

- `rule_8_1_187` checks `is_protected(t)` and skips `kh°`, preventing cascade kh→h.
- `rule_8_1_267` checks `t == 'h'` which fails for `h°`, preventing s→h→∅ cascade.
- `double_consonant()` strips the marker before the gemination copy but preserves it on the ādeśa copy.
- `detokenize()` strips all markers for surface output.

### Bahulam Branching

Each optional rule doubles the form list. The engine caps forms at 64 per pipeline stage (with deduplication) to prevent combinatorial explosion from deeply branching words. Rule 8.1.177 branches once per elision *site* independently, plus one all-deleted branch.

### Vibhakti Stripping

The engine attempts to strip common Sanskrit case endings (nominative, accusative, genitive, etc.) before processing. This allows inflected forms like *rājasya* → stem *rāja* → Prakrit forms. The stripped ending is reported in the response.

---

## License

MIT License — see [LICENSE](LICENSE).

---

## References

- Hemacandra. *Siddhahemaśabdānuśāsana*, Adhyāya 8, Pādas 1–2. (c. 1150 CE)
- *Dhuṇḍhikā* (*Vyutpatti-Dīpikā*) — auto-commentary with 3,304 worked derivations; primary source for rule ordering
- Pischel, R. *Comparative Grammar of the Prākrit Languages*. Motilal Banarsidass, 1981.
- Warder, A.K. *Introduction to Pali*. Pali Text Society, 1963. (for comparative Pali forms)
