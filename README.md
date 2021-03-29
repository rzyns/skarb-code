# How to generate the dictionary

* Tested on Ubuntu 18.04, Python 3.6
* `wget -qO - http://download.sgjp.pl/apt/sgjp.gpg.key | apt-key add -`
* `apt-add-repository http://download.sgjp.pl/apt/ubuntu`
* `apt update`
* `apt-get -y install morfeusz2`
* Download repo to a local folder
* Install `virtualenvwrapper` (see (here)[https://medium.com/@aaditya.chhabra/virtualenv-with-virtualenvwrapper-on-ubuntu-34850ab9e765])
* `mkvirtualenv -p python3.6 polski-english-dict`
* `pip install -r requirements.txt`
* `python make_dictionary.py stats make`

# Product
* P1/E3: Make sure that the search is on strict spelling to prevent ambiguity (ex: lęk for lek) via
* Exact-match Parameter (https://kdp.amazon.com/en_US/help/topic/G2HXJS944GL88DNV)
* P1/E2: handle wiktionary particle, phrase, prep_phrase, investigate det
* P1/E2: ~~Start adding grammar categories for each head word~~
* P2/E?: ~~Proper lemma sorting~~
* P2/E2: ~~Handle head words with multiple grammar categories or multiple disinct meanings from different etims (f.e.: pies)~~
* P2/E1: See if you can create new headwords from synonyms
* P2/E2: Add links between perfective and imperfective verbs
* P3/E2: Establish internal links for diminutive/augmentatives/derived
* P3/E1: Start looking into other dictionary formats
* P3/E1: plug gaps in english version through a combination of Wikisłównik and
* Google Translate (https://cloud.google.com/translate/pricing)

# Technical
* P1/E1: ~~refactor generator code so that it's testable, write basic tests~~
* P1/E?: ~~Kindlegen needs a timeout to handle cases where the dict is malformed (else it parses
* forever)~~
* P1/E1: write integration test based on at least one page of a text
* P2/E1: ~~put together CI/CD pipeline on GitLab~~
* P2/E1: ~~make Gitlab build dictionary as pipeline artifact~~
* P2/E2: check if you can use new version of Kindlegen (requires switching to a Windows image)
* P3/E1: autodeliver new build to cloud storage, update site

# Sharing
* P2/E1: ~~put together basic website (static site generator, SSL, download via Gitlab)~~
* P2/E2: put together website copy and choose theme
* P2/E1: document how to install the dictionary
* P2/E3: buy appropriate domain
* P3/E1: document how the whole thing is built

# Test
* P1: not highlightable words per page; missing words per page; wrong first choice; unclear definitions
* P3: Are derived head words bad? Do they detract from the experience?

# Known issues

# Headword templates:

```
# headword tag1, tag2
# 	(etymology if present)
# 	1. (category, other tags) meaning
# 	2. (category, other tags) meaning

# (derived 1, derived 2, derived 3)

# Verb Template:

# headword tag1 (expanded-tag, other-aspect)
# 	(etymology if present)
# 	1. (category, other tags) meanin
# 	2. (category, other tags) meaning

# (derived 1, derived 2, derived 3)
```

# Last manual test

* Total words 96
* Not highlightable 0
* Missing 6
* Wrong choice 5
* Unclear 0

# Entry types
```
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
```