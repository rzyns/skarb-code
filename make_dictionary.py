import subprocess
import sys
from dict_helpers import write_html_dictionary

create_with_stats = False
make_mobi_dict = False

if len(sys.argv) > 1 and sys.argv[1] == "stats":
    create_with_stats = True


if len(sys.argv) > 2 and sys.argv[2] == "make":
    make_mobi_dict = True


write_html_dictionary(create_with_stats)

if make_mobi_dict:
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
