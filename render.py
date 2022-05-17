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
    def person_count(self):
        return 2 if self.spouse else 1

    @property
    def node_id(self):
        return titleize(self.name)

    @property
    def downward_link_id(self):
        return (
            f"{self.node_id}_marries_{self.spouse.node_id}"
            if self.spouse
            else self.node_id
        )

    def attach(self, dot):
        if self.parent:
            dot.edge(self.parent, self.downward_link_id)

        if self.spouse:
            dot.node(self.downward_link_id, self.render_marriage())

        else:
            dot.node(self.downward_link_id, f"<{self.render_individual()}>")

    def render_marriage(self):
        return f"<<TABLE border='0'><TR><TD>{self.render_individual()}</TD><TD>{self.spouse.render_individual()}</TD></TR></TABLE>>"

    @property
    def is_divorced(self):
        return self.status == "divorced"

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
