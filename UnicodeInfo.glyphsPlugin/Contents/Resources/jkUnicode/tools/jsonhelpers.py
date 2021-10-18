import codecs
import json
import os

json_path = os.path.join(
    os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "json"
)


def json_to_file(path, file_name, obj, human_readable=True):
    with codecs.open(
        os.path.join(path, "%s.json" % file_name), "w", "utf-8"
    ) as f:
        if human_readable:
            indent = 4
        else:
            indent = None
        json.dump(obj, f, ensure_ascii=False, indent=indent, sort_keys=True)


def dict_from_file(path, file_name):
    with codecs.open(
        os.path.join(path, "%s.json" % file_name), "r", "utf-8"
    ) as f:
        return json.load(f)


def clean_json_dir(path):
    # Clean up the directory which contains the separate json files to avoid
    # orphaned files
    for name in os.listdir(path):
        if not name[0] == "." and name.lower().endswith(".json"):
            try:
                os.remove(os.path.join(path, name))
            except:
                print(
                    "WARNING: Could not remove file before regenerating it:",
                    os.path.join(path, name),
                )
