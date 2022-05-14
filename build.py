from pathlib import Path

import graphviz
from ruamel.yaml import YAML

people_count = 0


def titleize(string):
    return string.lower().replace(" ", "_")


def load_data():
    yaml = YAML(typ="safe")
    roots = []
    for path in Path("data").glob("*.yaml"):
        try:
            roots.extend(yaml.load(open(path))["roots"])
        except:
            print("Ran into issue parsing", path)
            raise
    return roots


def node_format(person, main=False):
    dates = person.get("birth")

    if "death" in person:
        dates = f"{person.get('birth')}-{person['death']}"

    dates_format = (
        f"<TR><TD><FONT POINT-SIZE='10.0'>{dates}</FONT></TD></TR>" if dates else ""
    )
    divorce_format = "(d)" if person.get("status") == "divorced" else ""
    port_format = "PORT='MAIN'" if main else ""
    return f"<TABLE border='0'><TR><TD {port_format}>{person['name']} {divorce_format}</TD></TR>{dates_format}</TABLE>"


def add_person(dot, person):
    global people_count
    people_count += 1
    node_id = titleize(person["name"])

    if "spouse" in person:
        people_count += 1
        spouse = person["spouse"]
        spouse_id = titleize(spouse["name"])

        linking_id = f"{node_id}_marries_{spouse_id}"
        node_id = f"{linking_id}:person"
        dot.node(
            linking_id,
            f"<<TABLE border='0'><TR><TD>{node_format(person)}</TD><TD>{node_format(spouse)}</TD></TR></TABLE>>",
        )

    else:
        dot.node(node_id, f"<{node_format(person)}>")
        linking_id = node_id

    if "parent" in person:
        dot.edge(person["parent"], node_id)

    for child in person.get("children", []):
        child_id = add_person(dot, child)
        dot.edge(linking_id, child_id)

    return node_id


def build_graph(data):
    dot = graphviz.Digraph(
        "structs", node_attr={"shape": "record"}, comment="Brody Family Tree"
    )

    for person in data:
        add_person(dot, person)

    return dot


def main():
    data = load_data()
    graph = build_graph(data)
    graph.render("doctest-output/round-table.gv", view=True)
    print(f"There are {people_count} people")


if __name__ == "__main__":
    main()
