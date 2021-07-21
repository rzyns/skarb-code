from collections import defaultdict, namedtuple
import functools
import morfeusz2
import json
from tqdm import tqdm
import subprocess

# CONSTANTS
CORPUS_FILENAME = "kaikki.org-dictionary-Polish.json"
MACHINE_TRANSLATED_CORPUS_FILENAME = "machine_translated_corpus.json"
DICTIONARY_HTML_FILENAME = "PL_EN_dict{}.html"
LOCALE_NAME = "pl_PL.utf8"
STATS_FILENAME = "dictionary_stats_{}.json"
DISCARDED_ENTRIES_FILENAME = "discarded_entries_{}.json"
DISCARDED_INVALID_POS_VARNAME = "excluded_pos"
DISCARDED_DERIVED_VARNAME = "entry_is_only_derived"
CORPUS_MORPH_CAT_VERB_STR = "verb"
VERBS_TAG_MAPPING = {
    "perfective": "pf",
    "imperfective": "impf",
    "frequentative": "fq",
    "transitive": "trans",
    "intransitive": "intrans",
}

WIKTIONARY_HEAD_WORD_TYPES_TO_IGNORE = [
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

CORPUS_INFLECTED_FORM_STR = "form_of"
CORPUS_MORPH_CAT_STR = "pos"
CORPUS_HEADWORD_STR = "word"
CORPUS_MEANINGS_STR = "senses"
CORPUS_DEFINITION_STR = "glosses"


SGJP_MORPH_CATEGORY_MAPPING = {
    "rz.": "noun",
    "cz.": "verb",
    "przym.": "adj"
}
MACHINE_TRANSLATED_MESSAGE = "<div><i>Translation generated with Google Cloud Translate API</i></div>"
SAFE_DICT_CHUNK = 25000


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def sort_headwords(word_list):
    """
    Make sure a list of words is put in proper ascending
    alphabetical order based on specified locale
    """
    import locale
    locale.setlocale(locale.LC_COLLATE, LOCALE_NAME)
    return sorted(word_list, key=functools.cmp_to_key(locale.strcoll))


def sort_lemmas(lemmas):
    """
    An ugly way of ensuring sorting of Lemma objects according to locale
    """
    import locale
    locale.setlocale(locale.LC_COLLATE, LOCALE_NAME)
    return sorted(lemmas, key=lambda lemma: functools.cmp_to_key(locale.strcoll)(lemma.headword))


def load_corpus():
    """
    Loads the Kaikki Wiktionary extract into JSON object
    """
    corpus_data = []
    with open(CORPUS_FILENAME, encoding="utf-8") as myfile:
        for line in tqdm(myfile.readlines(), desc="Loading corpus..."):
            json_version = json.loads(line)
            corpus_data.append(json_version)
    return corpus_data


class Lemma(object):
    """Class encapsulating all required data for a dictionary entry"""
    def __init__(self, headword, morph_cat, meanings, dictionary_id, raw_corpus_entry, machine_translated=""):
        super(Lemma, self).__init__()
        self.headword = headword
        self.morph_cat = morph_cat
        self.meanings = meanings
        self.raw_corpus_entry = raw_corpus_entry
        self.dictionary_id = dictionary_id
        self.inflected_forms = []
        self.machine_translated = machine_translated

    DICTIONARY_GENERIC_ENTRY_TEMPLATE = """
    <idx:entry name="Polish" scriptable="yes" spell="yes">
    <idx:short><a id="{entry_id}"></a>
    <idx:orth><b>{word}</b>
    {inflection_entries}
    </idx:orth>
    <div><i>{morph}</i></div>
    <div><ol>{definitions}</ol></div>
    {verb_aspect}
    {machine_translated}
    </idx:short>
    </idx:entry>
    """

    DICTIONARY_ENTRY_INFLECTION_TEMPLATE = """
    <idx:iform name="{inflection_type}" value="{word}"/></idx:iform>
    """

    DICTIONARY_DEFINITIONS_ENTRY_TEMPLATE = """
    <li>{definition}</li>
    """

    DICTIONARY_VERB_ASPECT_ENTRY_TEMPLATE = """
    <div>{aspect_tag} form: <a href="{other_id}">{other_aspect_headword}</a></div>
    """

    MORFEUSZ_OBJ = morfeusz2.Morfeusz(expand_tags=True, praet='composite')

    @property
    def definitions(self):
        definitions = []
        for meaning in self.meanings:
            definition = meaning.get(CORPUS_DEFINITION_STR, [])
            # TODO: check what exactly appears here
            if not definition:
                continue
            form_of = meaning.get(CORPUS_INFLECTED_FORM_STR, [])
            definitions.append(
                {
                    "definition": definition[0],
                    "derived": bool(form_of),
                    "derived_from": (form_of[0] if form_of else form_of)
                }
            )
        return definitions

    @property
    def is_only_derived_form(self):
        return all([definition["derived"] for definition in self.definitions])

    def generate_derived_forms(self):
        derived_words_check = set()
        derived_words = []

        if len(self.headword.split(" ")) > 1:
            # Only lemmas made by a single word for now
            return []

        GeneratedEntry = namedtuple(
            "GeneratedEntry", ["generated_form", "base_form", "tags", "frequency", "qualifiers"]
        )

        generated = self.MORFEUSZ_OBJ.generate(self.headword)
        generated_named = [GeneratedEntry(*element) for element in generated]

        for generated_word in generated_named:
            keep = True
            split_tags = generated_word.tags.split(":")

            for tag in split_tags:
                # Skip anything that Morfeusz doesn't recognise - we can reuse it later to refine
                # the head words
                if tag == MORFEUSZ_UNKNOWN_WORD_TAG:
                    keep = False
                    continue
                # Skip tags for abbreviation, non-accepted forms, etc.
                if tag in MORFEUSZ_TAGS_TO_IGNORE:
                    keep = False
                    continue

            # Skip certain qualifiers that don't lead to useful derived forms
            for qualif in MORFEUSZ_BAD_QUALIFS:
                if qualif in generated_word.qualifiers:
                    keep = False
                    continue

            # Add anything that made it to this point to the inflected entries,
            # making sure only unique values are added as Morfeusz has a tendency to
            # generate tons of duplicates
            if generated_word.generated_form not in derived_words_check and keep:
                # There seems to be something non-deterministic or environment- or version-dependent
                # in the way in which these 'm' tags are produced so getting rid of them
                tags_to_keep = [tag for tag in split_tags if tag not in ("m1", "m2", "m3")]
                tags_to_keep_formatted = ":".join(tags_to_keep)
                derived_words_check.add(generated_word.generated_form)
                derived_words.append(
                    {"derived_form": generated_word.generated_form, "tags": tags_to_keep_formatted}
                )

        return sorted(derived_words, key=lambda x: x["derived_form"])

    def generate_derived_html_iforms(self):
        derived_iforms = []
        derived_forms = self.generate_derived_forms()
        if derived_forms:
            derived_iforms.append("<idx:infl>")
            derived_iforms.extend([
                self.DICTIONARY_ENTRY_INFLECTION_TEMPLATE.format(
                    word=derived_form["derived_form"],
                    inflection_type=derived_form["tags"]
                ) for derived_form in derived_forms
            ])
            derived_iforms.append("</idx:infl>")
        return derived_iforms

    def generate_definitions_html_list(self):
        definitions_html_list = []
        for definition in self.definitions:
            definitions_html_list.append(
                self.DICTIONARY_DEFINITIONS_ENTRY_TEMPLATE.format(definition=definition["definition"])
            )
        return definitions_html_list

    def find_alternative_aspect_data(self):
        if self.morph_cat == CORPUS_MORPH_CAT_VERB_STR:
            other_aspect = self.raw_corpus_entry.get("forms", [])
            if other_aspect:
                form = other_aspect[0].get("form")
                tag = other_aspect[0].get("tags", [])
                if form and tag:
                    tag = tag[0]
                    return form, tag
        return "", ""

    def find_alternative_aspect(self, lemma_verb_dict={}):
        alternative_aspect_id = ""
        form, tag = self.find_alternative_aspect_data()
        if form and tag:
            alternative_aspect_lemma = lemma_verb_dict.get(form)
            if alternative_aspect_lemma:
                alternative_aspect_id = alternative_aspect_lemma.dictionary_id
        return form, tag, alternative_aspect_id

    def generate_lemma_html_entry(self, lemma_verb_dict={}):
        verb_aspect_str = ""
        form, tag, alternative_aspect_id = self.find_alternative_aspect()
        if form and tag:
            verb_aspect_str = self.DICTIONARY_VERB_ASPECT_ENTRY_TEMPLATE.format(
                aspect_tag=tag,
                other_id=alternative_aspect_id,
                other_aspect_headword=form,
            )

        return self.DICTIONARY_GENERIC_ENTRY_TEMPLATE.format(
            entry_id=self.dictionary_id,
            word=self.headword,
            morph=self.morph_cat.capitalize(),
            definitions="".join(self.generate_definitions_html_list()),
            inflection_entries="".join(self.generate_derived_html_iforms()),
            verb_aspect=verb_aspect_str,
            machine_translated=self.machine_translated
        )

    def __unicode__(self):
        return "{} - {} - {}".format(
            self.headword,
            self.morph_cat,
            self.definitions
        )


def extract_corpus_entry_data(corpus_entry):
    morph_cat = corpus_entry[CORPUS_MORPH_CAT_STR]
    meanings = corpus_entry.get(CORPUS_MEANINGS_STR, [])
    word = corpus_entry[CORPUS_HEADWORD_STR]
    return morph_cat, meanings, word


def check_lemma_is_invalid(lemma):
    if lemma.morph_cat in WIKTIONARY_HEAD_WORD_TYPES_TO_IGNORE:
        return DISCARDED_INVALID_POS_VARNAME
    # TODO: check if you can recover 'diminutive' words
    if lemma.is_only_derived_form:
        return DISCARDED_DERIVED_VARNAME
    return None


def build_verb_lemma_dictionary(lemma_list):
    """
    This is used to find and generate entries for linked perfective/imperfective/iterative forms.
    Note that there are multiple verbs in the dictionary that have more than one entry with the
    same headword, so this'll always be a best guess.
    """
    verb_lemma_dict = {}
    for lemma in lemma_list:
        if lemma.morph_cat == CORPUS_MORPH_CAT_VERB_STR:
            verb_lemma_dict[lemma.headword] = lemma
    return verb_lemma_dict


def build_lemma_from_corpus_entry(corpus_entry, dictionary_id=0):
    morph_cat, meanings, headword = extract_corpus_entry_data(corpus_entry)
    return Lemma(
        headword=headword,
        morph_cat=morph_cat,
        meanings=meanings,
        raw_corpus_entry=corpus_entry,
        dictionary_id=str(dictionary_id)
    )


def extract_head_words(corpus_data):
    """
    Casts corpus data into Lemma objects, keeps track of discarded objects
    """
    discarded = {
        DISCARDED_INVALID_POS_VARNAME: [],
        DISCARDED_DERIVED_VARNAME: [],
        DISCARDED_INVALID_POS_VARNAME + "_count": 0,
        DISCARDED_DERIVED_VARNAME + "_count": 0,
    }
    all_lemmas = []
    for i, entry in tqdm(enumerate(corpus_data), desc="Extracting head words..."):

        lemma = build_lemma_from_corpus_entry(entry)

        check = check_lemma_is_invalid(lemma)
        if check:
            discarded[check].append(entry)
            discarded[check + "_count"] += 1
            continue

        all_lemmas.append(lemma)

    return all_lemmas, discarded


def add_machine_translated_lemmas(machine_translated_corpus, base_lemmas):
    """
    Adds machine-translated corpus from SGJP/GCP Translate API, prioritises base lemmas
    """
    existing_lemmas_headwords = set([lemma.headword for lemma in base_lemmas])
    duplicate = 0
    no_trans = 0
    for item in tqdm(machine_translated_corpus):
        # Discard duplicates, Wiktionary entries will generally be of better quality
        if item["entry"] in existing_lemmas_headwords:
            duplicate += 1
            continue
        # Discard cases where the translation doesn't add anything
        if item["entry"].lower() == item.get("translation", "").lower():
            no_trans += 1
            continue
        lemma = Lemma(
            headword=item["entry"],
            morph_cat=SGJP_MORPH_CATEGORY_MAPPING.get(item["abbr_pos"], ""),
            meanings=[{CORPUS_DEFINITION_STR: [item.get("translation", [])]}],
            machine_translated=MACHINE_TRANSLATED_MESSAGE,
            raw_corpus_entry={},
            dictionary_id=0
        )
        base_lemmas.append(lemma)
    print("Duplicate: {}, no translation: {}".format(str(duplicate), str(no_trans)))
    return base_lemmas


def create_html_dictionary(create_with_stats=False, write=True):
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
    corpus_data = load_corpus()
    lemmas, discarded_entries = extract_head_words(corpus_data)
    machine_translated_corpus = read_machine_translated_corpus()
    lemmas = add_machine_translated_lemmas(machine_translated_corpus, lemmas)
    sorted_lemmas = sort_lemmas(lemmas)
    for i, lemma in enumerate(sorted_lemmas, start=1):
        setattr(lemma, 'dictionary_id', str(i))
    lemma_verb_dict = build_verb_lemma_dictionary(sorted_lemmas)
    split_lemma_chunks = chunks(sorted_lemmas, SAFE_DICT_CHUNK)
    for i, chunk in enumerate(split_lemma_chunks, start=1):
        all_html_lemmas = []
        str_index = str(i)
        for lemma in tqdm(chunk, desc="Generating HTML entries for chunk {}...".format(str_index)):
            lemma_html = lemma.generate_lemma_html_entry(lemma_verb_dict)
            all_html_lemmas.append(lemma_html)
        dict_contents = DICTIONARY_BODY_TEMPLATE.format(
            dict_body="<hr>".join(all_html_lemmas)
        )
        if write:
            write_html_dictionary_chunk(dict_contents, str_index)
    if create_with_stats:
        write_dict_stats(sorted_lemmas, discarded_entries, dict_contents.count("\n"))
    return sorted_lemmas, lemma_verb_dict


def write_dict_stats(sorted_lemmas, discarded_entries, html_dict_len):
    lemmas_per_letter = defaultdict(int)
    for lemma in sorted_lemmas:
        headword_initial = lemma.headword[0]
        lemmas_per_letter[headword_initial] += 1
    stats_dict = {
        "lemmas_count": len(sorted_lemmas),
        "lemmas_per_letter": dict(lemmas_per_letter),
        "dict_lines": html_dict_len,
        "discarded_entries_counts": {
            key: value for key, value in discarded_entries.items() if key.endswith("count")
        },
    }
    with open(STATS_FILENAME.format(fetch_current_git_hash()), "w", encoding="utf-8") as myfile:
        myfile.write(json.dumps(stats_dict))
    with open(DISCARDED_ENTRIES_FILENAME.format(fetch_current_git_hash()), "w", encoding="utf-8") as myfile:
        myfile.write(json.dumps(discarded_entries))


def fetch_current_git_hash():
    return subprocess.check_output(["git", "describe", "--always"]).strip().decode()


def write_html_dictionary(create_with_stats=False):
    create_html_dictionary(create_with_stats, True)


def write_html_dictionary_chunk(html_dict, chunk_no):
    with open(DICTIONARY_HTML_FILENAME.format(chunk_no), "w", encoding="utf-8") as myfile:
        myfile.write(html_dict)


def read_machine_translated_corpus():
    with open(MACHINE_TRANSLATED_CORPUS_FILENAME, "r", encoding="utf-8") as myfile:
        corpus = json.loads(myfile.read())
    return corpus
