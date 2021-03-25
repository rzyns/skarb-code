from collections import defaultdict, namedtuple
import morfeusz2
import json
import subprocess

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
with open("kaikki.org-dictionary-Polish.json", encoding="utf-8") as myfile:
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

ret_obj = subprocess.run(
    [
        "./kindlegen",
        "./PL_EN_dict.opf",
        "-c2",
        "-verbose",
        "-dont_append_source"
    ]
)

if ret_obj.returncode not in (0, 1):
    raise Exception("Failed to properly generate the dictionary")
