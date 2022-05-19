from pathlib import Path

from ruamel.yaml import YAML


def yaml_filepaths():
    # for path in Path("data").glob("*.yaml"):
    for path in Path("data").glob("*ers.yaml"):
        yield path


def yaml_files():
    for path in yaml_filepaths():
        print("Loading", path)
        with open(path, "r", encoding="utf-8") as file_handle:
            yield file_handle


def load_data():
    yaml = YAML(typ="safe")
    roots = []
    for yaml_file in yaml_files():
        roots.extend(yaml.load(yaml_file)["roots"])
    return roots
