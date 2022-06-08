import graphviz

from data import load_data
from render import PersonRender

people_count = 0


def add_person(dot, person):
    global people_count
    try:
        person = PersonRender(**person)
    except:
        print("failed on", person)
        raise
    person.attach(dot)
    people_count += person.person_count

    for partnership in person.partnerships:
        if partnership.can_collapse_children:
            try:
                partnership.attach_collapsed_children(dot)
            except:
                print("failed on", partnership)
                raise
        else:
            for child in partnership.children:
                child_id = add_person(dot, child)
                dot.edge(f"{partnership.joiner_id}:s", child_id, tailclip="false")

    return person.upward_link_id


def build_graph(data):
    dot = graphviz.Digraph(
        "structs",
        node_attr={"shape": "plaintext"},
        comment="Brody Family Tree",
    )
    dot.attr(nodesep="0.02")
    dot.graph_attr["dpi"] = "300"

    for person in data:
        add_person(dot, person)

    return dot


def main():
    data = load_data()
    graph = build_graph(data)
    graph.render("export", view=True, format="pdf")
    graph.render("image", format="png")
    print(f"There are {people_count} people")


if __name__ == "__main__":
    main()
