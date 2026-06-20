"""
Lexical exceptions: Sanskrit stem → list of Prakrit forms.
These whole-word substitutions take priority over the rule engine.
Sources: Hemacandra's Siddhahemaśabdānuśāsana 8.1–8.2 auto-commentary.

Each value is a list of (prakrit_form, [rule_ids], description) tuples.

Three distinct kinds of entry live here:

  1. NIPĀTANA — forms explicitly listed by Hemacandra as grammatical exceptions
     (sūtras 8.1.17–8.1.21, 8.1.77, 8.2.125–8.2.144). Must stay here.

  2. ENGINE PATCHES — words where the rule pipeline gives the wrong result and the
     correct forms must be hard-coded. Examples: agni (pipeline gives aṇṇi via
     8.2.43 over-applying gna→ṇṇ to gni; correct is aggi via 8.2.78); mṛga (ṛ→i
     variants unreachable because 8.1.126 obligatory ṛ→a fires first). Must stay
     here until the underlying pipeline bug is fixed.

  3. REDUNDANT — words whose correct forms the pipeline already derives correctly.
     These are kept only if removing them would suppress valid pipeline-produced
     bahulam forms. Any entry that blocks extra forms the pipeline would correctly
     generate has been removed; the pipeline now handles those words fully.
"""

from typing import List, Tuple, Dict

# Type: stem → list of (prakrit_form, rule_ids, note)
EXCEPTIONS: Dict[str, List[Tuple[str, List[str], str]]] = {

    # ── 8.1.17 ─────────────────────────────────────────────────────────────
    'kṣudh': [('chuhā', ['8.1.17'], 'kṣudh → chuhā (fem.)')],

    # ── 8.1.19 ─────────────────────────────────────────────────────────────
    'diś':   [('disā', ['8.1.19'], 'diś → disā (final C → sa)')],
    'prāvṛṣ':[('pāusā', ['8.1.19'], 'prāvṛṣ → pāusā')],

    # ── 8.1.21 ─────────────────────────────────────────────────────────────
    'kakubh':[('kaühā', ['8.1.21'], 'kakubh → kaühā')],

    # ── 8.1.77 ─────────────────────────────────────────────────────────────
    'āryā':  [('ajjū', ['8.1.77'], 'āryā (mother-in-law) → ajjū'),
              ('ajjā', ['8.1.77'], 'āryā (general) → ajjā')],

    # ── 8.2.125 ────────────────────────────────────────────────────────────
    'stoka': [('thokka', ['8.2.125'], 'stoka → thokka'),
              ('thova',  ['8.2.125'], 'stoka → thova'),
              ('theva',  ['8.2.125'], 'stoka → theva'),
              ('thoa',   ['8.2.125'], 'stoka → thoa')],

    # ── 8.2.126 ────────────────────────────────────────────────────────────
    'duhitṛ':[('dhūā',  ['8.2.126'], 'duhitṛ → dhūā'),
              ('duhiā', ['8.2.126'], 'duhitṛ → duhiā')],
    'bhaginī':[('bahiṇī', ['8.2.126'], 'bhaginī → bahiṇī'),
               ('bhaïṇī',['8.2.126'], 'bhaginī → bhaïṇī')],

    # ── 8.2.127 ────────────────────────────────────────────────────────────
    'vṛkṣa': [('rukkha', ['8.2.127'],              'nipātana: v→r, ṛ→u, kṣ→kkh'),
              ('vakkha', ['8.1.126', '8.2.3'],     'ṛ→a, kṣ→kkh (regular)'),
              ('vaccha', ['8.1.126', '8.2.3'],     'ṛ→a, kṣ→cch (regular, alt.)'),
              ('vikkha', ['8.1.128', '8.2.3'],     'ṛ→i, kṣ→kkh (regular)'),
              ('viccha', ['8.1.128', '8.2.3'],     'ṛ→i, kṣ→cch (regular, alt.)')],
    'kṣipta':[('chūḍha', ['8.2.127'], 'kṣipta → chūḍha')],

    # ── 8.2.128 ────────────────────────────────────────────────────────────
    'vanitā':[('vilayā', ['8.2.128'], 'vanitā → vilayā'),
              ('vaniā',  ['8.2.128'], 'vanitā → vaniā')],

    # ── 8.2.130 ────────────────────────────────────────────────────────────
    'strī':  [('itthī', ['8.2.130'], 'strī → itthī'),
              ('thī',   ['8.2.130'], 'strī → thī')],

    # ── 8.2.131 ────────────────────────────────────────────────────────────
    'dhṛti': [('dihi', ['8.2.131'], 'dhṛti → dihi')],

    # ── 8.2.132 ────────────────────────────────────────────────────────────
    'mārjāra':[('mañjara', ['8.2.132'], 'mārjāra → mañjara'),
               ('vañjara', ['8.2.132'], 'mārjāra → vañjara'),
               ('majjāra', ['8.2.132'], 'mārjāra → majjāra')],

    # ── 8.2.133 ────────────────────────────────────────────────────────────
    'vaiḍūrya':[('verulia', ['8.2.133'], 'vaiḍūrya → verulia'),
                ('veḍujja', ['8.2.133'], 'vaiḍūrya → veḍujja')],

    # ── 8.2.134 ────────────────────────────────────────────────────────────
    'idānīm':[('eṇhiṃ',  ['8.2.134'], 'idānīm → eṇhiṃ'),
              ('ettāhe', ['8.2.134'], 'idānīm → ettāhe')],

    # ── 8.2.135 ────────────────────────────────────────────────────────────
    'pūrva': [('purima', ['8.2.135'], 'pūrva → purima'),
              ('puvva',  ['8.2.135'], 'pūrva → puvva')],

    # ── 8.2.136 ────────────────────────────────────────────────────────────
    'trasta':[('hittha', ['8.2.136'], 'trasta → hittha'),
              ('taṭṭha', ['8.2.136'], 'trasta → taṭṭha'),
              ('tattha', ['8.2.136'], 'trasta → tattha')],

    # ── 8.2.138 (selected) ─────────────────────────────────────────────────
    'malina': [('maïla', ['8.2.138'], 'malina → maïla')],
    'ubhaya': [('avaha',  ['8.2.138'], 'ubhaya → avaha')],
    'śukti':  [('sippi',  ['8.2.138'], 'śukti → sippi')],
    'padāti': [('pāikka', ['8.2.138'], 'padāti → pāikka')],

    # ── 8.2.139 ────────────────────────────────────────────────────────────
    'daṃṣṭrā':[('dāḍhā', ['8.2.139'], 'daṃṣṭrā → dāḍhā')],

    # ── 8.2.140 ────────────────────────────────────────────────────────────
    'bahis': [('bāhiṃ',  ['8.2.140'], 'bahis → bāhiṃ'),
              ('bāhira', ['8.2.140'], 'bahis → bāhira')],

    # ── 8.2.141 ────────────────────────────────────────────────────────────
    'adhas': [('heṭṭha', ['8.2.141'], 'adhas → heṭṭha')],

    # ── 8.2.143 ────────────────────────────────────────────────────────────
    'tiryac':[('tiricchi', ['8.2.143'], 'tiryac → tiricchi')],

    # ── 8.2.144 ────────────────────────────────────────────────────────────
    'gṛha':  [('ghara', ['8.2.144'], 'gṛha → ghara (not before pati)')],

    # ── Common well-attested forms (multi-rule) ─────────────────────────────
    'kṛṣṇa': [('kaṇha', ['8.1.126', '8.1.260', '8.2.75'],
               'kṛṣṇa: ṛ→a, ṣ→s, kṣṇ-cluster → ṇha'),
              ('kiṇha', ['8.1.128', '8.1.260', '8.2.75'],
               'kṛṣṇa: ṛ→i, ṣ→s, → ṇha')],

    'brahman':[('bamha',  ['8.2.74', '8.2.79'],
                'brahman: r-elision, hm → mh, final-n elision'),
               ('brahma', ['8.2.93'], 'brahman: standard form')],

    'lakṣmī': [('lakkhi', ['8.2.3', '8.2.89'],
                'lakṣmī: kṣ→kh→kk, mī→hi')],

    'viṣṇu':  [('viṇhu', ['8.1.260', '8.2.75'],
                'viṣṇu: ṣ→s, sṇ→ṇh')],

    'kṛpā':   [('kipā',  ['8.1.128'], 'kṛpā: ṛ→i (kṛpā-class)')],

    'mṛtyu':  [('maccu', ['8.1.130', '8.2.13'],
                'mṛtyu: ṛ→a, tyu→cu')],

    'śṛṅga':  [('siṅga', ['8.1.130', '8.1.260'],
                'śṛṅga: ṛ→i, ś→s')],

    'ṛṣi':    [('isi',  ['8.1.140'], 'ṛṣi: ṛ→ri (kevala), i-elision → isi')],

    'ṛtu':    [('utu',  ['8.1.131'], 'ṛtu: ṛ→u (ṛtu-class)')],

    # ENGINE PATCH: pipeline can only produce ṛ→a forms (8.1.126 obligatory fires
    # first, eliminating ṛ before 8.1.128 sees it). ṛ→i forms require the exception.
    # Including ṛ→a forms here too because the exception overrides the pipeline.
    'mṛga':   [('maga', ['8.1.126'],             'mṛga: ṛ→a, g retained'),
               ('maa',  ['8.1.126', '8.1.177'],  'mṛga: ṛ→a, g→∅ intervocalic'),
               ('miga', ['8.1.128'],             'mṛga: ṛ→i, g retained'),
               ('mia',  ['8.1.128', '8.1.177'],  'mṛga: ṛ→i, g→∅ intervocalic')],

    'svapna': [('siviṇa', ['8.2.108'], 'svapna: i-epenthesis → siviṇo form'),
               ('sappaṇa',['8.2.77', '8.2.89'], 'svapna: cluster reduction')],

    # ── 8.2.116 ────────────────────────────────────────────────────────────
    # Varṇa-viparyaya (metathesis): sporadic r/ṇ transposition in listed words.
    # Not derivable by the general pipeline, so listed here as nipātana.
    'kareṇū':   [('kaṇerū',  ['8.2.116'], 'kareṇū → kaṇerū (r/ṇ metathesis)')],
    'vārāṇasī': [('bāṇārasī', ['8.2.116'], 'vārāṇasī → bāṇārasī (r/ṇ metathesis, v→b)')],

    # Particles / indeclinables (Part XI)
    'api':    [('pi',   ['8.1.41'], 'api: a- elided → pi'),
               ('avi',  ['8.1.41'], 'api: opt. a- → avi')],
    'iti':    [('tti',  ['8.1.42'], 'iti: i- elided after V → tti'),
               ('ti',   ['8.1.42'], 'iti: i- elided → ti')],
    'iva':    [('vva',  ['8.2.182'], 'iva → vva'),
               ('va',   ['8.2.182'], 'iva → va'),
               ('via',  ['8.2.182'], 'iva → via')],
    'eva':    [('eva',  [], 'eva retained'),
               ('cia',  ['8.2.184'], 'eva: emphatic cia')],

    # Numbers
    'eka':    [('ekka',  ['8.2.98'], 'eka: gemination → ekka')],
    'dvi':    [('du',    ['8.1.94'], 'dvi: i→u')],
    'tri':    [('ti',    ['8.1.177'], 'tri: r-cluster → ti')],
    'catur':  [('cau',   ['8.1.177'], 'catur → cau')],
    'pañca':  [('paṃca', ['8.1.25'],  'pañca: ñ→ṃ before c')],
    'ṣaṣ':   [('cha',   ['8.1.265'], 'ṣaṣ → cha')],
    'sapta':  [('satta', ['8.2.45', '8.2.89'], 'sapta: pt cluster → tta → satta')],
    'aṣṭa':  [('aṭṭha', ['8.2.34', '8.2.89'], 'aṣṭa → aṭṭha')],
    'nava':   [('ṇava',  ['8.1.229'], 'nava: n→ṇ initial')],
    'daśan':  [('dasa',  ['8.1.260'], 'daśan: ś→s, final n elision')],

    # Common Sanskrit nouns
    # NOTE: loka, māyā, rāja, deva, śiva, bhava, nāga, nāman, vāri — REMOVED.
    # All were suppressing valid bahulam forms the pipeline now produces correctly:
    #   loka  → pipeline gives loa + loka + loya (ya-śruti on hiatus oa)
    #   māyā  → pipeline gives māā + māyā
    #   rāja  → pipeline gives rāa + rāja + rāya (j→y via 8.1.224)
    #   deva  → pipeline gives dea + deva + deya
    #   śiva  → pipeline gives sia + siva + siya
    #   bhava → pipeline gives bhaa + bhava + bhaya
    #   nāga  → pipeline gives all 6 forms (n-retained + n→ṇ × g-retained/g-deleted)
    #   nāman → pipeline gives nāma + ṇāma (n-retained form was missing)
    #   vāri  → pipeline gives vāri + vāi + vāyi (r-elision forms were missing)

    'śrī':    [('siri',  ['8.1.260', '8.2.104'], 'śrī: ś→s, i-epenthesis')],

    'karma':  [('kamma', ['8.2.79', '8.2.89'], 'karma: r-elision, m-gemination')],

    'dharma': [('dhamma', ['8.2.79', '8.2.89'], 'dharma: r-elision, m-gemination')],

    'mitra':  [('mitta', ['8.2.79', '8.2.89'], 'mitra: r-elision, t-gemination')],

    'putra':  [('putta', ['8.2.79', '8.2.89'], 'putra: r-elision, t-gemination')],

    'sarpa':  [('sappa', ['8.2.79', '8.2.89'], 'sarpa: r-elision, p-gemination')],

    'varṣa':  [('vassa', ['8.1.260', '8.2.79', '8.2.89'],
                'varṣa: ṣ→s, r-elision, s-gemination')],

    'śabda':  [('sadda', ['8.1.260', '8.2.77', '8.2.89'],
                'śabda: ś→s, bd cluster → dd')],

    'jagat':  [('jaga',  ['8.1.11'], 'jagat: final t elision'),
               ('jagaṃ', ['8.1.23'], 'jagat: final t→ṃ')],

    'manas':  [('maṇa',  ['8.1.11', '8.1.228'],
                'manas: final s elision, n→ṇ')],

    'tapas':  [('tava',  ['8.1.11', '8.1.231'],
                'tapas: final s elision, p→v')],

    'vayas':  [('vaya',  ['8.1.11', '8.1.177'],
                'vayas: final s elision, y→∅')],

    'śiras':  [('sira',  ['8.1.260', '8.1.11'],
                'śiras: ś→s, final s elision')],

    # mukha, sukha REMOVED — pipeline gives muha/suha (8.1.187) + mua/sua (h→∅ 8.1.267)
    # + muya/suya (ya-śruti). mua and sua are attested Ardhamāgadhī forms.

    'duḥkha': [('dukha', ['8.2.72'], 'duḥkha: cluster → h (opt.)')],

    'hasta':  [('hattha', ['8.2.45', '8.2.89'], 'hasta: st→th→ttha')],

    'sthāna': [('ṭhāṇa', ['8.2.9', '8.1.228'],
                'sthāna: st→ṭh, n→ṇ')],

    'satya':  [('sacca', ['8.2.13', '8.2.89'], 'satya: tya→ca→cca')],

    'jñāna':  [('ṇāṇa',  ['8.2.42', '8.1.228'],
                'jñāna: jñ→ṇ, n→ṇ')],

    'kāma':   [('kāma',  [], 'kāma: retained (m after ā not elided)')],

    # rāja REMOVED — pipeline correctly produces rāja + rāa (j→∅) + rāya (j→y 8.1.224).

    # ENGINE PATCH: pipeline gives aṇṇi (8.2.43 gna→ṇṇa over-applies to gni);
    # correct Prakrit form is aggi via 8.2.78 (n as lower member, elide, gem g).
    'agni':   [('aggi',  ['8.2.78', '8.2.89'],
                'agni: gn→gg (n is lower, elided; g doubled)')],

    'vāyu':   [('vāu',   ['8.1.177'], 'vāyu: y→∅ intervocalic'),
               ('vāyu',  [], 'vāyu: retained')],

    'pṛthivī':[('paḍhavī', ['8.1.88', '8.1.195'],
                'pṛthivī: ṛ→a, th→ḍh variant')],

    # nara: removed from exceptions — rule engine produces all forms correctly:
    # nara (retained), ṇara (n→ṇ opt.), naa / ṇaa (r→∅ bahulam), naya / ṇaya (ya-śruti)

    'tīrtha': [('tittha', ['8.1.104', '8.2.45'],
                'tīrtha: ī→u (h-variant), rt cluster')],

    'vyākaraṇa': [('vāgaraṇa', ['8.1.268'],
                   'vyākaraṇa: vy-cluster reduction')],

    'ācārya': [('ajjhāvaa', ['8.1.73', '8.2.26'],
                'ācārya: ā→i (ācārya form), rya→jha'),
               ('āiriya',   ['8.1.73'],
                'ācārya: standard Ardhamāgadhī')],

    'śayyā':  [('sejjā', ['8.1.57', '8.2.89'],
                'śayyā: ś→s, init-V→e (śayyā-class), yy→jj')],

    # patha, tatha, katha REMOVED — pipeline gives paha/taha/kaha (8.1.187)
    # + paa/taa/kaa (h→∅ 8.1.267) + paya/taya/kaya (ya-śruti). All are attested.

    # vāri REMOVED — pipeline produces vāri + vāi (r→∅ 8.1.178) + vāyi (ya-śruti)

    'anna':   [('aṇṇa',  ['8.1.228', '8.2.89'],
                'anna: n→ṇ, gemination')],

    'kanna':  [('kaṇṇa', ['8.1.228', '8.2.89'],
                'kanna: n→ṇ, gemination')],

    'parvata':[('pavvata', ['8.2.79', '8.2.89'],
                'parvata: r-elision, v-gemination')],

    'sarva':  [('savva', ['8.2.79', '8.2.89'],
                'sarva: r-elision, v-gemination')],

    # sūrya, kārya, ārya: removed from exceptions — the rule engine correctly
    # shortens the long vowel (8.1.84) before the rya cluster, then applies
    # 8.2.24 (rya→jja) or 8.2.63 (rya→ra) with proper gemination.

    'jaya':   [('jaa',   ['8.1.177'], 'jaya: y→∅'),
               ('jaya',  [], 'jaya: retained')],

    'vijaya':  [('vijaa',  ['8.1.177'], 'vijaya: y→∅'),
                ('vijaya', [], 'vijaya: retained')],

    'avyaya': [('avvaya', ['8.2.99'], 'avyaya: v-gemination')],

    'saṃsāra':[('saṃsāra', ['8.1.25'], 'saṃsāra: ṃ retained')],

    # ── 8.1.261 special (nipātana) ─────────────────────────────────────────
    # 8.1.261 allows s→h (general bahulam) but also s→ṇ in snuṣā only.
    # suṇhā is the attested Prakrit; the ṇ comes from ṣ→ṇ (not ṣ→s→h).
    'snuṣā': [('suṇhā', ['8.1.261'], 'snuṣā → suṇhā: ṣ→ṇ (nipātana per 8.1.261)')],

    # ── 8.2.86 ─────────────────────────────────────────────────────────────
    # śmaśru-class: initial ś deleted before m (8.2.86); cannot be derived by
    # rule engine since 8.1.260 (ś→s) runs first, making the ś undetectable.
    'śmaśru':  [('maṃsu',  ['8.2.86', '8.1.260', '8.2.79', '8.1.25'],
                 'śmaśru: initial ś elided (8.2.86), ś→s, r-elision'),
                ('massu',  ['8.2.86', '8.1.260', '8.2.79'],
                 'śmaśru: initial ś elided, s+r cluster → ss')],
    'śmaśāna': [('masāṇa', ['8.2.86', '8.1.260', '8.1.228'],
                 'śmaśāna: initial ś elided (8.2.86), ś→s, n→ṇ intervocalic')],

    # ── 8.2.21 (āścarya-class) ─────────────────────────────────────────────
    # āścarya: rya→ria via 8.2.67 (not in engine); add attested Prakrit forms.
    'āścarya': [('accharia', ['8.1.84', '8.2.21', '8.2.67'],
                 'āścarya: ā→a (8.1.84), śca→ccha (8.2.21), rya→ria (8.2.67)'),
                ('acchajja', ['8.1.84', '8.2.21', '8.2.24'],
                 'āścarya: ā→a (8.1.84), śca→ccha (8.2.21), rya→jja (8.2.24)')],
}


def lookup(stem: str) -> List[Tuple[str, List[str], str]]:
    """Return exception entries for the stem, or empty list if not found."""
    return EXCEPTIONS.get(stem.strip(), [])
