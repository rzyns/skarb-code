from dict_helpers import (
    build_lemma_from_corpus_entry,
    check_lemma_is_invalid,
    DISCARDED_INVALID_POS_VARNAME,
    DISCARDED_DERIVED_VARNAME,
    extract_corpus_entry_data,
    extract_head_words,
    sort_headwords,
    WIKTIONARY_HEAD_WORD_TYPES_TO_IGNORE,
)

TEST_FULL_NOUN_ENTRY = {
    'pos': 'noun',
    'heads': [{'1': 'm-an', 'dim': 'piesek', 'aug': 'psisko', 'template_name': 'pl-noun'}],
    'forms': [
        {'form': 'piesek', 'tags': ['diminutive']},
        {'form': 'psisko', 'tags': ['augmentative']}],
    'inflection': [{'1': 'p', '2': 's', '3': 'pies', 'dats': 'psu', 'template_name': 'pl-decl-noun-masc-ani'}],
    'categories': ['Dogs', 'Foxes', 'Law enforcement', 'Male animals', 'Male occupations', 'Mustelids', 'Polish nouns with multiple animacies'],
    'word': 'pies',
    'lang': 'Polish',
    'lang_code': 'pl',
    'wikipedia': ['pl:pies'],
    'sounds': [{'ipa': '/pʲɛs/'}, {'audio': 'Pl-pies.ogg', 'text': 'Audio'}],
    'derived': [
        {'word': 'pieseczek', 'tags': ['diminutive']},
        {'word': 'piesek', 'tags': ['diminutive']},
        {'word': 'piesunio', 'tags': ['diminutive']},
        {'word': 'psiaczek', 'tags': ['diminutive']},
        {'word': 'psiątko', 'tags': ['diminutive']},
        {'word': 'psinka', 'tags': ['diminutive']},
        {'word': 'pieski', 'tags': ['adjective']},
        {'word': 'psi', 'tags': ['adjective']},
        {'word': 'psowaty', 'tags': ['adjective']},
        {'word': 'psio', 'tags': ['adverbs']},
        {'word': 'piesko', 'tags': ['adverbs']},
        {'word': 'psioczyć', 'tags': ['verb']}],
    'senses': [
        {'tags': ['animate', 'masculine'], 'glosses': ['A dog (Canis lupus familiaris).'], 'id': 'pies-noun-zipbMNBV'},
        {'tags': ['animate', 'masculine'], 'glosses': ['A male dog.'], 'id': 'pies-noun-DJsfS6hT'},
        {'categories': ['Hunting'], 'topics': ['agriculture', 'hunting', 'lifestyle'], 'tags': ['animate', 'masculine'], 'glosses': ['A male fox or badger.'], 'id': 'pies-noun-3fKPhsEA'}
    ]
}


TEST_VERB_W_SYNONYMS_ENTRY = {
    'pos': 'verb',
    'heads': [{'a': 'i', 'pf': 'podjąć', 'template_name': 'pl-verb'}],
    'forms': [{'form': 'podjąć', 'tags': ['perfective']}],
    'inflection': [{'1': 'podejm', '2': 'pp', 'template_name': 'pl-conj-ai-uję'}],
    'word': 'podejmować',
    'lang': 'Polish',
    'lang_code': 'pl',
    'sounds': [
        {'ipa': '/pɔ.dɛjˈmɔ.vat͡ɕ/'},
        {'audio': 'Pl-podejmować.ogg', 'text': 'Audio'}
    ],
    'senses': [
        {'synonyms': [{'word': 'unosić'}], 'tags': ['archaic', 'imperfect', 'transitive'], 'glosses': ['to lift up, to raise'], 'id': 'podejmować-verb-M.OhOjSj'},
        {'tags': ['imperfect', 'transitive'], 'glosses': ['to collect, to withdraw (e.g. money from a bank)'], 'id': 'podejmować-verb-ZudYby5s'},
        {'synonyms': [{'word': 'przedsiębrać'}], 'tags': ['imperfect', 'transitive'], 'glosses': ['to take up, to engage in'], 'id': 'podejmować-verb-5GAxHREl'},
        {'synonyms': [{'word': 'wprowadzać'}], 'tags': ['imperfect', 'transitive'], 'glosses': ['to undertake, to initiate, to instigate'], 'id': 'podejmować-verb-9s.wKYGC'},
        {'synonyms': [{'word': 'gościć'}], 'tags': ['imperfect', 'transitive'], 'glosses': ['to host, to entertain, to receive'], 'id': 'podejmować-verb-kNy49NlF'},
        {'tags': ['imperfect', 'reflexive'], 'glosses': ['to commit to, to decide upon'], 'id': 'podejmować-verb-dD2ySCRf'}
    ]
}

TEST_VERB_W_CONJ_ENTRY = {
    'pos': 'verb',
    'heads': [{'a': 'i', 'freq': 'miewać', 'template_name': 'pl-verb'}],
    'forms': [{'form': 'miewać', 'tags': ['frequentative']}],
    'inflection': [
        {
            '1': 'mieć',
            '2': 'mam',
            '3': 'ma',
            '4': 'mają',
            '5': 'mia',
            '6': 'mia',
            '7': 'mie',
            '8': 'miej',
            'ip': 'miano',
            'template_name': 'pl-conj-ai'
        }
    ],
    'word': 'mieć',
    'lang': 'Polish',
    'lang_code': 'pl',
    'sounds': [{'ipa': '/mʲɛt͡ɕ/'}, {'homophone': 'mieć'}, {'audio': 'Pl-mieć.ogg', 'text': 'audio1'}, {'audio': 'Pl-miedź.ogg', 'text': 'audio2'}],
    'related': [{'word': 'mieć nadzieję'}, {'word': 'mienie'}],
    'senses': [
        {'tags': ['imperfect'], 'glosses': ['to have'], 'id': 'mieć-verb-WkO.FK2E'},
        {'tags': ['imperfect'], 'glosses': ['to be (for an age)'], 'id': 'mieć-verb-3odylZTa'},
        {'tags': ['auxiliary', 'imperfect'], 'glosses': ['must, have to, need to'], 'id': 'mieć-verb-DTcCIu9G'},
        {'tags': ['imperfect'], 'glosses': ['to feel something'], 'id': 'mieć-verb-KzyT.CFm'}
    ]
}


TEST_DERIVED_ENTRY = {
    'pos': 'noun',
    'heads': [{'1': 'pl', '2': 'noun form', 'g': 'm', 'template_name': 'head'}],
    'word': 'psa',
    'lang': 'Polish',
    'lang_code': 'pl',
    'sounds': [{'ipa': '/psa/'}],
    'senses': [
        {
            'tags':
                ['accusative', 'form-of', 'genitive', 'masculine', 'singular'],
            'glosses': ['accusative/genitive singular of pies'],
            'form_of': ['pies'],
            'id': 'psa-noun'
        }
    ]
}

TEST_UNTAGGED_DERIVED_ENTRY = {
    'pos': 'noun',
    'heads': [{'1': 'pl', '2': 'noun form', 'g': 'm-in', 'template_name': 'head'}],
    'word': 'abaku',
    'lang': 'Polish',
    'lang_code': 'pl',
    'sounds': [{'ipa': '/aˈba.ku/'}],
    'senses': [{'tags': ['inanimate', 'masculine'], 'glosses': ['genitive/locative/vocative singular of abak'], 'id': 'abaku-noun'}]
}


TEST_INVALID_POS_ENTRY = {
    'pos': 'character',
    'heads': [{'1': 'pl', '2': 'letter', '3': 'upper case', '4': '', '5': 'lower case', '6': 'a', 'template_name': 'head'}],
    'forms': [{'form': 'a', 'tags': ['lower-case']}],
    'word': 'A',
    'lang': 'Polish',
    'lang_code': 'pl',
    'sounds': [{'ipa': '/a/'}],
    'senses': [{'tags': ['upper-case'], 'glosses': ['The first letter of the Polish alphabet, written in the Latin script.'], 'id': 'A-character'}]
}


def test_sort_headwords():
    scrambled_chars = [
        "k",
        "l",
        "a",
        "ą",
        "i",
        "b",
        "h",
        "j",
        "c",
        "ę",
        "f",
        "g",
        "ć",
        "d",
        "e",
        "ł",
        "m",
        "n",
        "ż",
        "ń",
        "y",
        "z",
        "ś",
        "t",
        "u",
        "v",
        "ó",
        "p",
        "q",
        "r",
        "s",
        "w",
        "x",
        "ź",
        "o",
    ]
    expected_order = [
        "a",
        "ą",
        "b",
        "c",
        "ć",
        "d",
        "e",
        "ę",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "ł",
        "m",
        "n",
        "ń",
        "o",
        "ó",
        "p",
        "q",
        "r",
        "s",
        "ś",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "ź",
        "ż"
    ]
    assert sort_headwords(scrambled_chars) == expected_order


def test_extract_corpus_entry_data():
    expected_result = (
        "noun",
        [
            {'tags': ['animate', 'masculine'], 'glosses': ['A dog (Canis lupus familiaris).'], 'id': 'pies-noun-zipbMNBV'},
            {'tags': ['animate', 'masculine'], 'glosses': ['A male dog.'], 'id': 'pies-noun-DJsfS6hT'},
            {'categories': ['Hunting'], 'topics': ['agriculture', 'hunting', 'lifestyle'], 'tags': ['animate', 'masculine'], 'glosses': ['A male fox or badger.'], 'id': 'pies-noun-3fKPhsEA'}
        ],
        "pies",
    )
    assert extract_corpus_entry_data(TEST_FULL_NOUN_ENTRY) == expected_result


def test_build_lemma_from_corpus_entry():
    entry = TEST_FULL_NOUN_ENTRY
    lemma = build_lemma_from_corpus_entry(entry)

    assert lemma.headword == "pies"
    assert lemma.morph_cat == "noun"
    assert lemma.meanings == [
        {'tags': ['animate', 'masculine'], 'glosses': ['A dog (Canis lupus familiaris).'], 'id': 'pies-noun-zipbMNBV'},
        {'tags': ['animate', 'masculine'], 'glosses': ['A male dog.'], 'id': 'pies-noun-DJsfS6hT'},
        {'categories': ['Hunting'], 'topics': ['agriculture', 'hunting', 'lifestyle'], 'tags': ['animate', 'masculine'], 'glosses': ['A male fox or badger.'], 'id': 'pies-noun-3fKPhsEA'}
    ]


def test_check_lemma_is_invalid():
    only_derived = build_lemma_from_corpus_entry(TEST_DERIVED_ENTRY)
    assert check_lemma_is_invalid(only_derived) == DISCARDED_DERIVED_VARNAME

    for pos in WIKTIONARY_HEAD_WORD_TYPES_TO_IGNORE:
        copy_entry = TEST_INVALID_POS_ENTRY.copy()
        copy_entry["pos"] = pos
        invalid_pos = build_lemma_from_corpus_entry(copy_entry)
        assert check_lemma_is_invalid(invalid_pos) == DISCARDED_INVALID_POS_VARNAME


def test_extract_head_words():
    corpus = [
        TEST_FULL_NOUN_ENTRY,
        TEST_DERIVED_ENTRY,
        TEST_INVALID_POS_ENTRY
    ]
    extracted, discarded = extract_head_words(corpus)
    assert len(extracted) == 1
    assert len(discarded[DISCARDED_DERIVED_VARNAME]) == 1
    assert len(discarded[DISCARDED_INVALID_POS_VARNAME]) == 1
    assert discarded[DISCARDED_DERIVED_VARNAME + "_count"] == 1
    assert discarded[DISCARDED_INVALID_POS_VARNAME + "_count"] == 1
    assert extracted[0].headword == "pies"
    assert extracted[0].morph_cat == "noun"
    assert extracted[0].meanings == [
        {'tags': ['animate', 'masculine'], 'glosses': ['A dog (Canis lupus familiaris).'], 'id': 'pies-noun-zipbMNBV'},
        {'tags': ['animate', 'masculine'], 'glosses': ['A male dog.'], 'id': 'pies-noun-DJsfS6hT'},
        {'categories': ['Hunting'], 'topics': ['agriculture', 'hunting', 'lifestyle'], 'tags': ['animate', 'masculine'], 'glosses': ['A male fox or badger.'], 'id': 'pies-noun-3fKPhsEA'}
    ]
    assert discarded[DISCARDED_DERIVED_VARNAME][0] == TEST_DERIVED_ENTRY
    assert discarded[DISCARDED_INVALID_POS_VARNAME][0] == TEST_INVALID_POS_ENTRY


def test_lemma_definitions():
    entry = TEST_FULL_NOUN_ENTRY
    lemma = build_lemma_from_corpus_entry(entry)
    assert lemma.definitions == [
        {
            "definition": 'A dog (Canis lupus familiaris).',
            "derived": False,
            "derived_from": []
        },
        {
            "definition": 'A male dog.',
            "derived": False,
            "derived_from": []
        },
        {
            "definition": 'A male fox or badger.',
            "derived": False,
            "derived_from": []
        },
    ]
    entry = TEST_DERIVED_ENTRY
    lemma = build_lemma_from_corpus_entry(entry)
    assert lemma.definitions == [
        {
            "definition": 'accusative/genitive singular of pies',
            "derived": True,
            "derived_from": "pies"
        },
    ]


def test_lemma_generate_noun_lemma_html_entry():
    entry = TEST_FULL_NOUN_ENTRY
    lemma = build_lemma_from_corpus_entry(entry)
    assert lemma.generate_lemma_html_entry() == '\n    <idx:entry name="Polish" scriptable="yes" spell="yes">' +\
        '\n    <idx:short><a id="0"></a>' +\
        '\n    <idx:orth><b>pies</b>' +\
        '\n    <idx:infl>' +\
        '\n    <idx:iform name="subst:sg:nom" value="pies"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:sg:gen.acc" value="psa"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:pl:loc" value="psach"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:pl:inst" value="psami"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:sg:inst" value="psem"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:sg:loc" value="psie"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:pl:dat" value="psom"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:pl:nom.voc" value="psowie"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:sg:dat" value="psu"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:pl:nom.acc.voc" value="psy"/></idx:iform>' +\
        '\n    \n    <idx:iform name="subst:pl:gen.acc" value="psów"/></idx:iform>' +\
        '\n    </idx:infl>' +\
        '\n    </idx:orth>' +\
        '\n    <div><i>Noun</i></div>' +\
        '\n    <div><ol>' +\
        '\n    <li>A dog (Canis lupus familiaris).</li>' +\
        '\n    \n    <li>A male dog.</li>' +\
        '\n    \n    <li>A male fox or badger.</li>' +\
        '\n    </ol></div>' +\
        '\n    ' +\
        '\n    ' +\
        '\n    </idx:short>' +\
        '\n    </idx:entry>\n    '


def test_lemma_generate_verb_lemma_html_entry():
    entry = TEST_VERB_W_CONJ_ENTRY
    lemma = build_lemma_from_corpus_entry(entry)
    assert lemma.generate_lemma_html_entry() == '\n    <idx:entry name="Polish" scriptable="yes" spell="yes">' +\
        '\n    <idx:short><a id="0"></a>' +\
        '\n    <idx:orth><b>mieć</b>' +\
        '\n    <idx:infl>' +\
        '\n    <idx:iform name="fin:sg:ter:imperf" value="ma"/></idx:iform>' +\
        '\n    \n    <idx:iform name="fin:pl:sec:imperf" value="macie"/></idx:iform>' +\
        '\n    \n    <idx:iform name="fin:pl:ter:imperf" value="mają"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pcon:imperf" value="mając"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:sg:nom.voc:f:imperf:aff" value="mająca"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:pl:nom.acc.voc:m2.m3.f.n:imperf:aff" value="mające"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:sg:acc:m1.m2:imperf:aff" value="mającego"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:sg:gen.dat.loc:f:imperf:aff" value="mającej"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:sg:dat:m1.m2.m3.n:imperf:aff" value="mającemu"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pacta" value="mająco"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:pl:nom.voc:imperf:aff" value="mający"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:pl:acc:imperf:aff" value="mających"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:pl:dat:m1.m2.m3.f.n:imperf:aff" value="mającym"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:pl:inst:m1.m2.m3.f.n:imperf:aff" value="mającymi"/></idx:iform>' +\
        '\n    \n    <idx:iform name="pact:sg:acc.inst:f:imperf:aff" value="mającą"/></idx:iform>' +\
        '\n    \n    <idx:iform name="fin:sg:pri:imperf" value="mam"/></idx:iform>' +\
        '\n    \n    <idx:iform name="fin:pl:pri:imperf" value="mamy"/></idx:iform>' +\
        '\n    \n    <idx:iform name="fin:sg:sec:imperf" value="masz"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:sg:nom.voc:f:imperf:aff" value="miana"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:pl:nom.acc.voc:m2.m3.f.n:imperf:aff" value="miane"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:sg:acc:m1.m2:imperf:aff" value="mianego"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:sg:gen.dat.loc:f:imperf:aff" value="mianej"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:sg:dat:m1.m2.m3.n:imperf:aff" value="mianemu"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:pl:nom.voc:imperf:aff" value="miani"/></idx:iform>' +\
        '\n    \n    <idx:iform name="imps:imperf" value="miano"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:sg:acc:imperf:aff" value="miany"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:pl:acc:imperf:aff" value="mianych"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:pl:dat:m1.m2.m3.f.n:imperf:aff" value="mianym"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:pl:inst:m1.m2.m3.f.n:imperf:aff" value="mianymi"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ppas:sg:acc.inst:f:imperf:aff" value="mianą"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:m1.m2.m3:ter:imperf" value="miał"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:f:imperf" value="miała"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:f:ter:imperf" value="miałaby"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:f:pri:imperf" value="miałabym"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:f:sec:imperf" value="miałabyś"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:f:pri:imperf" value="miałam"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:f:sec:imperf" value="miałaś"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:m1.m2.m3:ter:imperf" value="miałby"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:m1.m2.m3:pri:imperf" value="miałbym"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:m1.m2.m3:sec:imperf" value="miałbyś"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:m1.m2.m3:pri:imperf" value="miałem"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:m1.m2.m3:sec:imperf" value="miałeś"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:n:imperf" value="miało"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:n:ter:imperf" value="miałoby"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:n:pri:imperf" value="miałobym"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:sg:n:sec:imperf" value="miałobyś"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:n:pri:imperf" value="miałom"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:sg:n:sec:imperf" value="miałoś"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:pl:m2.m3.f.n:imperf" value="miały"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:pl:m2.m3.f.n:ter:imperf" value="miałyby"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:pl:m2.m3.f.n:sec:imperf" value="miałybyście"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:pl:m2.m3.f.n:pri:imperf" value="miałybyśmy"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:pl:m2.m3.f.n:sec:imperf" value="miałyście"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:pl:m2.m3.f.n:pri:imperf" value="miałyśmy"/></idx:iform>' +\
        '\n    \n    <idx:iform name="impt:sg:sec:imperf" value="miej"/></idx:iform>' +\
        '\n    \n    <idx:iform name="impt:pl:sec:imperf" value="miejcie"/></idx:iform>' +\
        '\n    \n    <idx:iform name="impt:pl:pri:imperf" value="miejmy"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:pl:imperf" value="mieli"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:pl:ter:imperf" value="mieliby"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:pl:sec:imperf" value="mielibyście"/></idx:iform>' +\
        '\n    \n    <idx:iform name="cond:pl:pri:imperf" value="mielibyśmy"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:pl:sec:imperf" value="mieliście"/></idx:iform>' +\
        '\n    \n    <idx:iform name="praet:pl:pri:imperf" value="mieliśmy"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ger:pl:nom.acc:n:imperf:aff" value="mienia"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ger:pl:loc:n:imperf:aff" value="mieniach"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ger:pl:inst:n:imperf:aff" value="mieniami"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ger:sg:nom.acc:n:imperf:aff" value="mienie"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ger:sg:inst:n:imperf:aff" value="mieniem"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ger:pl:dat:n:imperf:aff" value="mieniom"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ger:sg:dat.loc:n:imperf:aff" value="mieniu"/></idx:iform>' +\
        '\n    \n    <idx:iform name="inf:imperf" value="mieć"/></idx:iform>' +\
        '\n    \n    <idx:iform name="ger:pl:gen:n:imperf:aff" value="mień"/></idx:iform>' +\
        '\n    </idx:infl>' +\
        '\n    </idx:orth>' +\
        '\n    <div><i>Verb</i></div>' +\
        '\n    <div><ol>' +\
        '\n    <li>to have</li>' +\
        '\n    \n    <li>to be (for an age)</li>' +\
        '\n    \n    <li>must, have to, need to</li>' +\
        '\n    \n    <li>to feel something</li>' +\
        '\n    </ol></div>' +\
        '\n    \n    <div>frequentative form: <a href="">miewać</a></div>' +\
        '\n    \n    \n    </idx:short>\n    </idx:entry>\n    '
