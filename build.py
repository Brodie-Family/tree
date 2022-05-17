import graphviz

from data import load_data
from render import PersonRender

people_count = 0


def add_person(dot, person):
    global people_count
    person = PersonRender(**person)
    person.attach(dot)
    people_count += person.person_count
    if person.can_collapse_children:
        person.attach_collapsed_children(dot)
    else:
        for child in person.children:
            child_id = add_person(dot, child)
            dot.edge(person.downward_link_id, child_id)

    return person.upward_link_id


def build_graph(data):
    dot = graphviz.Digraph(
        "structs",
        node_attr={"shape": "plaintext"},
        comment="Brody Family Tree",
    )

    for person in data:
        add_person(dot, person)

    return dot


def main():
    data = load_data()
    graph = build_graph(data)
    graph.render("doctest-output/tree.gv", view=True)
    print(f"There are {people_count} people")


if __name__ == "__main__":
    main()
