from collections import defaultdict, namedtuple
import morfeusz2
import json

# CONSTANTS
KAIKKI_UNROLLED_WIKTIONARY_URL = "https://kaikki.org/dictionary/Polish/kaikki.org-dictionary-Polish.json"

WIKTIONARY_ENTRIES_TO_IGNORE = [
    "name",
    "character",
    "punct",
    "abbrev",
    "det",
    "infix",
    "particle",
    "phrase",
    "prefix",
    "prep_phrase",
    "suffix",
]

MORFEUSZ_TAGS_TO_IGNORE = [
    "wok",
    "nwok",
    "neg",
    "depr",
    "pun"
    "nakc",
    "aglt",
    "adja",
    "brev",
    "pun",
]

MORFEUSZ_BAD_QUALIFS = [
    "daw.",
    "pisane_łącznie_z_przyimkiem",
]

MORFEUSZ_UNKNOWN_WORD_TAG = "ign"

INFLECTED_FORM_STR = "form_of"

DICTIONARY_BODY_TEMPLATE = """
<html xmlns:math="http://exslt.org/math" xmlns:svg="http://www.w3.org/2000/svg"
xmlns:tl="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"
xmlns:saxon="http://saxon.sf.net/" xmlns:xs="http://www.w3.org/2001/XMLSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:cx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"
xmlns:mmc="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"
xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">
<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
<body>
<mbp:frameset>{dict_body}</mbp:frameset>
</body>
"""

DICTIONARY_GENERIC_ENTRY_TEMPLATE = """
<idx:entry name="Polish" scriptable="yes" spell="yes">
<idx:short><a id="{entry_id}"></a>
<idx:orth><b>{word}</b>
{inflection_entries}
</idx:orth>
<div><ol>{definitions}</ol></div>
</idx:short>
</idx:entry>
"""

DICTIONARY_ENTRY_INFLECTION_TEMPLATE = """
<idx:iform name="{inflection_type}" value="{word}"/></idx:iform>
"""

DICTIONARY_DEFINITIONS_ENTRY_TEMPLATE = """
<li>{definition}</li>
"""

# Process Wiktionary corpus
wiktionary_data = []
with open("../../Desktop/kaikki.org-dictionary-Polish.json", encoding="utf-8") as myfile:
    for line in myfile.readlines():
        wiktionary_data.append(json.loads(line))

all_entries = []
base_form_entries = defaultdict(set)
form_of_entries = defaultdict(dict)
bad_entries = {}

# Discriminating between base and inflected/conjugated forms
for entry in wiktionary_data:
    pos = entry["pos"]
    if pos in WIKTIONARY_ENTRIES_TO_IGNORE:
        continue
    word = entry["word"]
    senses = entry.get("senses", [])
    for sense in senses:
        glosses = sense.get("glosses", None)
        if not glosses:
            continue
        form_of = sense.get(INFLECTED_FORM_STR)
        if form_of:
            key = form_of[0]
            form_of_entries[key][word] = glosses
        else:
            base_form_entries[word].update(glosses)

# Refining entries using Morfeusz
morf = morfeusz2.Morfeusz(expand_tags=True)
GeneratedEntry = namedtuple(
    "GeneratedEntry", ["generated_form", "base_form", "tags", "frequency", "qualifiers"]
)

for entry in base_form_entries.keys():

    # Only looking at one-word heads, not phrases
    if len(entry.split(" ")) == 1:
        generated = morf.generate(entry)
        generated_named = [GeneratedEntry(*element) for element in generated]
        for generated_entry in generated_named:
            split_tags = generated_entry.tags.split(":")

            for tag in split_tags:
                # Flag anything that Morfeusz doesn't recognise - we can reuse it later to refine
                # the head words
                if tag == MORFEUSZ_UNKNOWN_WORD_TAG:
                    bad_entries[entry] = generated_entry
                # Skip tags for abbreviation, non-accepted forms, etc.
                if tag in MORFEUSZ_TAGS_TO_IGNORE:
                    continue

            # Skip certain qualifiers that don't lead to useful derived forms
            for qualif in MORFEUSZ_BAD_QUALIFS:
                if qualif in generated_entry.qualifiers:
                    continue

            # Add anything that made it to this point to the inflected entries
            if not form_of_entries[entry].get(generated_entry.generated_form):
                form_of_entries[entry][generated_entry.generated_form] = [generated_entry.tags]

# Creating entries from Wiktionary corpus
enumerated_entries = enumerate(base_form_entries.items(), start=1)
for i, (entry, definitions) in sorted(enumerated_entries, key=lambda x: x[1][0]):
    # Finding all inflected entries for base entry
    inflected_entries = form_of_entries.get(entry, {})
    inflected_entries_iforms = []
    for inflected_entry, gloss in inflected_entries.items():
        inflected_entries_iforms.append(DICTIONARY_ENTRY_INFLECTION_TEMPLATE.format(
            inflection_type=gloss[0],
            word=inflected_entry
        ))
    if inflected_entries_iforms:
        # Add proper enclosing tags if we found inflected entries
        inflected_entries_iforms.append("</idx:infl>")
        inflected_entries_iforms.insert(0, "<idx:infl>")

    # Creating formatted entries
    definition_lis = []

    for definition in definitions:
        definition_lis.append(DICTIONARY_DEFINITIONS_ENTRY_TEMPLATE.format(
            definition=definition
        ))

    formatted_entry = DICTIONARY_GENERIC_ENTRY_TEMPLATE.format(
        entry_id=str(i),
        word=entry,
        definitions="".join(definition_lis),
        inflection_entries="".join(inflected_entries_iforms)
    )
    all_entries.append(formatted_entry)


dictionary_content = DICTIONARY_BODY_TEMPLATE.format(dict_body="<hr>".join(all_entries))

with open("PL_EN_dict.html", "w") as myfile:
    myfile.write(dictionary_content)

# Check all types of entries
# abbrev: {"pos": "abbrev", "heads": [{"1": "pl", "2": "contraction", "template_name": "head"}], "word": "ze\u0144", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/z\u025b\u0272/"}], "senses": [{"glosses": ["Contraction of z niego."], "tags": ["abbreviation", "alt-of", "contraction"], "alt_of": ["z niego"], "id": "ze\u0144-abbrev-mj4S8ufG"}, {"glosses": ["Contraction of z niej."], "tags": ["abbreviation", "alt-of", "contraction"], "alt_of": ["z niej"], "id": "ze\u0144-abbrev-MhzoEWR7"}]}
# adj: {"pos": "adj", "heads": [{"1": "-", "adv": "-", "template_name": "pl-adj"}], "word": "czerwony jak burak", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/t\u0361\u0282\u025br\u02c8v\u0254.n\u0268 jak \u02c8bu.rak/"}, {"audio": "Pl-czerwony jak burak.ogg", "text": "Audio"}], "senses": [{"categories": ["Polish similes"], "tags": ["not-comparable", "simile"], "glosses": ["flushed; red-faced"], "id": "czerwony_jak_burak-adj"}]}
# conj: {"pos": "conj", "heads": [{"1": "pl", "2": "conjunction", "template_name": "head"}], "word": "za\u015b", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/za\u0255/"}, {"audio": "Pl-za\u015b.ogg", "text": "Audio"}], "senses": [{"synonyms": [{"word": "natomiast"}], "glosses": ["whereas, while, however"], "id": "za\u015b-conj-JWa1WRJu"}, {"synonyms": [{"word": "znowu"}], "categories": ["Upper Silesia Polish"], "tags": ["Upper Silesia"], "glosses": ["again"], "id": "za\u015b-conj-Y5hJ9rNo"}, {"synonyms": [{"word": "potem"}, {"word": "p\u00f3\u017aniej"}], "categories": ["Pozna\u0144 Polish"], "tags": ["Pozna\u0144"], "glosses": ["after, afterwards"], "id": "za\u015b-conj-08IKTHKz"}]}
# det: {"pos": "det", "heads": [{"1": "pl", "2": "determiner form", "template_name": "head"}], "word": "kilkoma", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/k\u02b2il\u02c8k\u0254.ma/"}], "senses": [{"glosses": ["instrumental of kilka"], "tags": ["form-of", "instrumental"], "form_of": ["kilka"], "id": "kilkoma-det"}]}
# infix: {"pos": "infix", "heads": [{"1": "pl", "2": "infix", "template_name": "head"}], "word": "-nie-", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/\u0272\u025b/"}], "senses": [{"glosses": ["Used to form a negative verb."], "categories": ["Polish infixes"], "id": "-nie--infix"}]}
# intj: {"pos": "intj", "heads": [{"1": "pl", "2": "interjection", "template_name": "head"}], "categories": ["Missing Welsh plurals", "Polish onomatopoeias"], "word": "pac", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/pat\u0361s/"}], "senses": [{"synonyms": [{"word": "b\u0119c"}], "categories": ["Cieszyn Silesia Polish"], "tags": ["Cieszyn Silesia"], "glosses": ["plunk, thud, flump (sound)"], "id": "pac-intj"}]}
# name: {"pos": "name", "heads": [{"1": "f", "template_name": "pl-proper noun"}], "inflection": [{"1": "Fenicja ", "2": "Fenicji ", "3": "Fenicji ", "4": "Fenicj\u0119 ", "5": "Fenicj\u0105 ", "6": "Fenicji ", "7": "Fenicjo ", "template_name": "pl-decl-noun-sing"}], "word": "Fenicja", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/f\u025b\u02c8\u0272it\u0361s.ja/"}, {"audio": "Pl-Fenicja.ogg", "text": "Audio"}], "senses": [{"tags": ["feminine"], "glosses": ["Phoenicia"], "derived": [{"word": "Fenicjanin m"}, {"word": "Fenicjanka f"}, {"word": "adjective: fenicki"}], "id": "Fenicja-name"}]}
# noun: {"pos": "noun", "heads": [{"1": "pl", "2": "noun", "g": "n", "head": "[[pismo]] [[klinowy|klinowe]]", "template_name": "head"}], "inflection": [{"1": "n", "2": "adj-n", "tantum": "s", "template_name": "pl-decl-phrase"}], "word": "pismo klinowe", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/\u02c8p\u02b2is.m\u0254 kl\u02b2i\u02c8n\u0254.v\u025b/"}], "senses": [{"tags": ["neuter"], "glosses": ["cuneiform, cuneiform script"], "categories": ["Polish singularia tantum", "Writing systems"], "id": "pismo_klinowe-noun"}]}
# noun2: {"pos": "noun", "heads": [{"1": "pl", "2": "noun form", "g": "f", "template_name": "head"}], "categories": ["Missing Welsh plurals", "Murids", "Sounds"], "word": "pac", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/pat\u0361s/"}], "senses": [{"tags": ["feminine", "form-of", "genitive", "plural"], "glosses": ["genitive plural of paca"], "form_of": ["paca"], "id": "pac-noun"}]}
# num: {"pos": "num", "heads": [{"1": "pl", "2": "numeral", "template_name": "head"}], "inflection": [{"1": "dwoj", "2": "e", "template_name": "pl-decl-numeral-coll"}], "word": "dwoje", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/\u02c8dv\u0254.j\u025b/"}, {"audio": "Pl-dwoje.ogg", "text": "Audio"}], "senses": [{"tags": ["collectively"], "glosses": ["two"], "related": [{"word": "dwoje", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "troje", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "czworo", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "pi\u0119cioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "sze\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "siedmioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "o\u015bmioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "dziewi\u0119cioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "dziesi\u0119cioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "jedena\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "dwana\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "trzyna\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "czterna\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "pi\u0119tna\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "szesna\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "siedemna\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "osiemna\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "dziewi\u0119tna\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}, {"word": "dwadzie\u015bcioro", "tags": ["collective numbers from two to twenty", "collectively"], "translation": "collective numbers from two to twenty"}], "categories": ["Polish numerals", "Two"], "id": "dwoje-num"}]}
# particle: {"pos": "particle", "heads": [{"1": "pl", "2": "particle", "template_name": "head"}], "categories": ["Polish particles"], "word": "oby", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/\u02c8\u0254.b\u0268/"}], "senses": [{"synonyms": [{"word": "bodaj"}, {"word": "niech"}, {"word": "niechaj"}], "glosses": ["hopefully, if only, let, may"], "id": "oby-particle"}]}
# phrase: {"pos": "phrase", "heads": [{"1": "pl", "2": "phrase", "head": "([[czy]]) [[mo\u017cesz]] [[mi]] [[pom\u00f3c]]?", "template_name": "head"}], "word": "mo\u017cesz mi pom\u00f3c", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/\u02c8m\u0254.\u0290\u025b\u0282 m\u02b2i \u02c8p\u0254.mut\u0361s/"}], "senses": [{"tags": ["informal"], "glosses": ["can you help me?"], "related": [{"word": "mo\u017ce mi pan pom\u00f3c?", "tags": ["formal", "masculine"], "translation": "formal, to male"}, {"word": "mo\u017ce mi pani pom\u00f3c?", "tags": ["formal", "feminine"], "translation": "formal, to female"}], "categories": ["Polish phrasebook"], "id": "mo\u017cesz_mi_pom\u00f3c-phrase"}]}
# prexif: {"pos": "prefix", "heads": [{"1": "pl", "2": "prefix", "template_name": "head"}], "word": "prze-", "lang": "Polish", "lang_code": "pl", "senses": [{"glosses": ["Intensifier prefix; over-"], "tags": ["morpheme"], "id": "prze--prefix-hV-ud.Pj"}, {"glosses": ["re- (again)"], "id": "prze--prefix-6EqOUsxb"}]}
# prep: {"pos": "prep", "heads": [{"1": "pl", "2": "preposition", "3": "+ genitive", "template_name": "head"}], "categories": ["Polish prepositions"], "word": "miast", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/m\u02b2ast/"}], "senses": [{"synonyms": [{"word": "zamiast"}], "tags": ["archaic", "with-genitive"], "glosses": ["instead of"], "id": "miast-prep"}]}
# prep_phrase: {"pos": "prep_phrase", "heads": [{"1": "pl", "2": "prepositional phrase", "head": "[[z]] [[grosze|groszami]]", "template_name": "head"}], "word": "z groszami", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/z\u0261r\u0254\u02c8\u0282a.m\u02b2i/"}], "senses": [{"glosses": ["Used other than figuratively or idiomatically: see z,\u200e grosze."], "id": "z_groszami-prep_phrase-cwFN0epU"}, {"tags": ["colloquial", "humorous"], "glosses": ["plus a small amount; plus epsilon"], "id": "z_groszami-prep_phrase-hMNcFuKU"}]}
# pron: {"pos": "pron", "heads": [{"1": "pl", "2": "pronoun", "g": "m", "template_name": "head"}], "inflection": [{"1": "\u00f3w", "2": "owa", "3": "owo", "4": "owi", "5": "owe", "6": "owego", "7": "owej", "8": "owych", "9": "owemu", "10": "owym", "11": "ow\u0105", "12": "owym", "13": "owymi", "template_name": "pl-decl-adj"}], "word": "\u00f3w", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/uf/"}, {"audio": "Pl-\u00f3w.ogg", "text": "Audio"}], "senses": [{"tags": ["literary", "masculine"], "glosses": ["that, the aforementioned"], "categories": ["Polish pronouns"], "id": "\u00f3w-pron"}]}
# proverb: {"pos": "proverb", "heads": [{"1": "pl", "2": "proverb", "head": "[[nadgorliwo\u015b\u0107]] [[by\u0107|jest]] [[gorszy|gorsza]] [[od]] [[faszyzm]]u", "template_name": "head"}], "categories": ["Polish proverbs"], "word": "nadgorliwo\u015b\u0107 jest gorsza od faszyzmu", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/nad.\u0261\u0254r\u02c8l\u02b2i.v\u0254\u0255t\u0361\u0255 j\u025bst \u02c8\u0261\u0254r.\u0282a \u0254t fa\u02c8\u0282\u0268z.mu/"}], "senses": [{"glosses": ["Doing too much is worse than doing just enough; one should be careful not to overdo things."], "id": "nadgorliwo\u015b\u0107_jest_gorsza_od_faszyzmu-proverb-QVowzxib"}, {"glosses": ["Busybodies and overcommiters cause far more problems than slackers."], "id": "nadgorliwo\u015b\u0107_jest_gorsza_od_faszyzmu-proverb-nO5xcGBp"}]}
# suffix: {"pos": "suffix", "heads": [{"1": "pl", "2": "suffix", "g": "f", "template_name": "head"}], "inflection": [{"1": "-an", "2": "k", "template_name": "pl-decl-noun-f"}], "word": "-anka", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/\u02c8an.ka/"}], "senses": [{"tags": ["feminine", "morpheme", "obsolete"], "glosses": ["Attached to surnames, sometimes to other nouns, to form feminine (proper) nouns meaning: daughter of"], "id": "-anka-suffix-8obUS1FA"}, {"tags": ["feminine"], "glosses": ["Purely structural suffix, forms feminine nouns"], "id": "-anka-suffix-EolYpQDl"}]}
# verb: {"pos": "verb", "heads": [{"1": "pl", "2": "verb form", "g": "f", "template_name": "head"}], "categories": ["Mythological creatures"], "word": "wi\u0142a", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/\u02c8v\u02b2i.wa/"}], "senses": [{"tags": ["feminine", "form-of", "past", "singular", "third-person"], "glosses": ["third-person singular feminine past of wi\u0107"], "form_of": ["wi\u0107"], "id": "wi\u0142a-verb"}]}
# verb2: {"pos": "verb", "heads": [{"a": "impf", "template_name": "pl-verb"}], "inflection": [{"1": "boja", "template_name": "pl-conj-ai-am,asz"}], "word": "boja\u0107", "lang": "Polish", "lang_code": "pl", "sounds": [{"ipa": "/\u02c8b\u0254.jat\u0361\u0255/"}], "senses": [{"tags": ["archaic", "dialectal", "imperfect", "reflexive"], "glosses": ["to fear, to be afraid"], "synonyms": [{"word": "ba\u0107", "sense": "to fear"}], "id": "boja\u0107-verb"}]}

# Only keep noun, verb, adj
# Separate between entries where senses->{form_of} and not (one per senses entry with form_of)
# Start creating basic entries for not form_of, move to form_of later
# Exclude pos types we can't handle
# Noun: get pos, word (entry), for each senses->glosses[] create a definition including tags
# Verb: get pos, word (entry), for each senses->glosses[] create a definition including tags
# form_of -> use tags excluding form_of for inflection type, use form_of for linking

# Plan on how to handle more complex entry variants (diminutives, alternative meanings, derived words)
# Plan how to handle more complex grammar (listing verb aspects?)
# Plan how to add context to each entry
# Plan how to add grammatical category to each meaning (inflgrp="{part_of_speech}")


# P3/E2: Establish internal links for diminutive/augmentatives/derived
# P3/E3: Add 
# P2/E2: Add links between perfective and imperfective verbs
# P2/E3: Start adding grammar categories for each head word
# P2/E2: Start removing incorrect head words
# P1/E1: Add derived forms from http://sgjp.pl


# http://sgjp.pl scraping
# Manual survey: 279978 lexemes
# Url structure: http://sgjp.pl/edycja/ajax/get-entry/?lexeme_id=13589 (lexeme exists)
# Url structure: http://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=13589&variant=1 (lexeme contents)
# 1. Fetch list of head words from dictionary, scrape in order until
# you find all of them. Build offline mapping of page id to lexeme. Use AutoThrottling extension
# to avoid crashing the site.
# 2. For each head word, go to the appropriate lexeme detail page if it exists (build list of the ones
# you didn't find - can be useful to exclude bad head words).
# 3. Convert string response into HtmlResponse (provide encoding). Fetch required table data and word
# class.
# 4. Start updating dictionary of derived forms based on results (headword: {derived_word: [gloss]})


# Only go for head words that have a single word
# Exclude: wok, nwok, neg, depr, pun, ign, split on :
# If it has "ign", flag it as it's probably a bad head word