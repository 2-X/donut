import re

def fix_filepath(filepath):
    """ add double-quotes around each directory or filename containing spaces """
    # split into directory names
    filepath = re.split(r"[\/\\]", filepath)

    # add double-quotes to items with spaces in them
    filepath = list(map(lambda x: f'"{x}"' if " " in x else x, filepath))

    # join back with forward slashes
    filepath = "/".join(filepath)

    return filepath

def test_fix_filepath():
    assert (fix_filepath("c:\\Users\\My Username\\Documents\\Coding Projects/ nu-crushes-autopost\\download_utils.py") ==
    'c:/Users/"My Username"/Documents/"Coding Projects"/" nu-crushes-autopost"/download_utils.py')
