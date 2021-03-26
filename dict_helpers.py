from collections import namedtuple
import functools
import morfeusz2
import json
from tqdm import tqdm

# CONSTANTS
CORPUS_FILENAME = "kaikki.org-dictionary-Polish.json"
DICTIONARY_HTML_FILENAME = "PL_EN_dict.html"
LOCALE_NAME = "pl_PL.utf8"

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
    return sorted(lemmas, key=lambda x: functools.cmp_to_key(locale.strcoll)(x.headword))


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
    def __init__(self, headword, morph_cat, meanings, raw_corpus_entry):
        super(Lemma, self).__init__()
        self.headword = headword
        self.morph_cat = morph_cat
        self.meanings = meanings
        self.raw_corpus_entry = raw_corpus_entry
        self.inflected_forms = []

    DICTIONARY_GENERIC_ENTRY_TEMPLATE = """
    <idx:entry name="Polish" scriptable="yes" spell="yes">
    <idx:short><a id="{entry_id}"></a>
    <idx:orth><b>{word}</b>
    {inflection_entries}
    </idx:orth>
    <div><i>{morph}</i></div>
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

    MORFEUSZ_OBJ = morfeusz2.Morfeusz(expand_tags=True)

    @property
    def definitions(self):
        definitions = []
        for meaning in self.meanings:
            definition = meaning.get(CORPUS_DEFINITION_STR, [])
            # TODO: check what exactly appears here
            if not definition:
                continue
            form_of = meaning.get(CORPUS_INFLECTED_FORM_STR, "")
            definitions.append(
                {
                    "definition": definition[0],
                    "derived": bool(form_of),
                    "derived_from": form_of
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
                derived_words_check.add(generated_word.generated_form)
                derived_words.append(
                    {"derived_form": generated_word.generated_form, "tags": generated_word.tags}
                )

        return derived_words

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

    def generate_lemma_html_entry(self, dictionary_id):
        return self.DICTIONARY_GENERIC_ENTRY_TEMPLATE.format(
            entry_id=str(dictionary_id),
            word=self.headword,
            morph=self.morph_cat.capitalize(),
            definitions="".join(self.generate_definitions_html_list()),
            inflection_entries="".join(self.generate_derived_html_iforms())
        )

    def __str__(self):
        return "{} - {} - {}".format(
            self.headword,
            self.morph_cat,
            self.definitions
        )


def extract_head_words(corpus_data):
    """
    Casts corpus data into Lemma objects
    """
    all_lemmas = []
    for entry in corpus_data:
        morph_cat = entry[CORPUS_MORPH_CAT_STR]

        # Bad morphological category, throw out
        if morph_cat in WIKTIONARY_HEAD_WORD_TYPES_TO_IGNORE:
            continue

        # For some reason the entry has no valid meanings, throw out
        # TODO: check these
        meanings = entry.get(CORPUS_MEANINGS_STR, [])
        if not meanings:
            continue

        word = entry[CORPUS_HEADWORD_STR]

        lemma = Lemma(word, morph_cat, meanings, entry)

        if not lemma.is_only_derived_form:
            # Dictionary breaks if we don't exclude these, which
            # should anyway be replaced by Morfeusz
            all_lemmas.append(lemma)

    return all_lemmas


def create_html_dictionary():
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
    lemmas = tqdm(extract_head_words(corpus_data), desc="Extracting head words...")
    sorted_lemmas = sort_lemmas(lemmas)
    all_html_lemmas = []
    for i, lemma in tqdm(enumerate(sorted_lemmas, start=1), desc="Generating HTML entries..."):
        lemma_html = lemma.generate_lemma_html_entry(str(i))
        # We get a few duplicates here?
        all_html_lemmas.append(lemma_html)
    return DICTIONARY_BODY_TEMPLATE.format(dict_body="<hr>".join(all_html_lemmas))

# should have 1236231 lines
def write_html_dictionary():
    html_dict = create_html_dictionary()
    with open(DICTIONARY_HTML_FILENAME, "w", encoding="utf-8") as myfile:
        myfile.write(html_dict)
