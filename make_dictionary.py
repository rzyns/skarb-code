import subprocess
from dict_helpers import write_html_dictionary

write_html_dictionary()

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
