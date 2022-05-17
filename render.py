def titleize(string):
    return string.lower().replace(" ", "_")


class PersonRender:
    def __init__(
        self,
        name,
        birth=None,
        children=None,
        death=None,
        is_main=True,
        nee=None,
        note=None,
        parent=None,
        spouse=None,
        status=None,
    ):
        self.name = name

        self.birth = birth
        self.children = children or []
        self.death = death
        self.is_main = is_main
        self.note = note
        self.parent = parent
        self.spouse = PersonRender(**spouse, is_main=False) if spouse else None
        self.status = status

    @property
    def can_collapse_children(self):
        return self.children and not any(c.get("children") for c in self.children)

    @property
    def downward_link_id(self):
        return (
            f"{self.node_id}_marries_{self.spouse.node_id}"
            if self.spouse
            else self.node_id
        )

    @property
    def is_divorced(self):
        return self.status == "divorced"

    @property
    def node_id(self):
        return titleize(self.name)

    @property
    def person_count(self):
        return (
            1
            + ((self.spouse and 1) or 0)
            + ((self.can_collapse_children and len(self.children)) or 0)
        )

    def attach(self, dot):
        if self.parent:
            dot.edge(self.parent, self.downward_link_id)

        if self.spouse:
            dot.node(self.downward_link_id, self.render_marriage())

        else:
            dot.node(self.downward_link_id, f"<{self.render_individual()}>")

    def attach_collapsed_children(self, dot):
        children_id = f"{self.downward_link_id}_children"
        dot.node(children_id, self.render_children())
        dot.edge(self.downward_link_id, children_id)

    def render_marriage(self):
        return f"<<TABLE border='0'><TR><TD>{self.render_individual()}</TD><TD>{self.spouse.render_individual()}</TD></TR></TABLE>>"

    def render_individual(self):
        dates = (
            (self.birth or "") if not self.death else f"{self.birth or ''}-{self.death}"
        )

        dates_format = (
            f"<TR><TD><FONT POINT-SIZE='10.0'>{dates}</FONT></TD></TR>" if dates else ""
        )
        divorce_format = "(d)" if self.is_divorced else ""
        port_format = "PORT='MAIN'" if self.is_main else ""
        return f"<TABLE border='0'><TR><TD {port_format}>{self.name} {divorce_format}</TD></TR>{dates_format}</TABLE>"

    def render_children(self):
        people_the_children = [PersonRender(**child) for child in self.children]
        row_the_children = "\n".join(
            [f"<TR><TD>{p.render_individual()}</TD></TR>" for p in people_the_children]
        )

        return f"<<TABLE border='0'>{row_the_children}</TABLE>>"
