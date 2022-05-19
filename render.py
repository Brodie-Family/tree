def titleize(string):
    return string.lower().replace(" ", "_")


class PartnershipRender:
    def __init__(
        self,
        attached_id,
        children=None,
        spouse=None,
        collapse_children=True,
        status=None,
    ):
        self.attached_id = attached_id
        self.children = children or []
        self.collapse_children = collapse_children
        self.spouse = PersonRender(**spouse, is_main=False) if spouse else None
        self.status = status

    def __str__(self):
        return f"PartnershipRender(spouse={self.spouse_name}, children={len(self.children)}, collapse={self.collapse_children})"

    @property
    def spouse_name(self):
        return self.spouse and self.spouse.node_id

    @property
    def node_id(self):
        return (
            f"{self.attached_id}_partners_{self.spouse_name}"
            if self.spouse
            else self.attached_id
        )

    @property
    def can_collapse_children(self):
        return (
            self.children
            and self.collapse_children
            and not any(c.get("partnerships") for c in self.children)
        )

    @property
    def is_divorced(self):
        return self.status == "divorced"

    def render_children(self):
        people_the_children = [PersonRender(**child) for child in self.children]
        row_the_children = "\n".join(
            [f"<TR><TD>{p.render_individual()}</TD></TR>" for p in people_the_children]
        )

        return f"<<TABLE border='0'>{row_the_children}</TABLE>>"

    def attach(self, dot):
        if not self.spouse:
            # If nobody as spouse, just use the original person
            return self.attached_id

        spouse_id = self.spouse.attach(dot)
        dot.node(self.node_id, "", shape="insulator")
        dot.edge(self.attached_id, self.node_id, dir="none")
        dot.edge(self.node_id, spouse_id, dir="none")


class PersonRender:
    def __init__(
        self,
        name,
        below=None,
        birth=None,
        death=None,
        is_main=True,
        nee=None,
        note=None,
        parent=None,
        partnerships=None,
        sibling=None,
    ):
        self.name = name

        self.below = below
        self.birth = birth
        self.death = death
        self.is_main = is_main
        self.note = note
        self.parent = parent
        self.sibling = sibling
        self.partnerships = [
            PartnershipRender(self.node_id, **p) for p in partnerships or []
        ]

    # @property
    # def link_id(self):
    #     return (
    #         # f"{self.node_id}_marries_{self.spouse.node_id}"
    #         f"{self.node_id}_married"
    #         if self.partnerships
    #         else self.node_id
    #     )
    #
    @property
    def downward_link_id(self):
        return f"{self.node_id}:s"

    @property
    def upward_link_id(self):
        return f"{self.node_id}:n"

    @property
    def node_id(self):
        return titleize(self.name)

    @property
    def person_count(self):
        return (
            1
            + len(self.partnerships)
            # + ((self.can_collapse_children and len(self.children)) or 0)
        )

    def attach(self, dot):
        with dot.subgraph(
            name=f"{self.node_id}_wrapper",
            # node_attr={"rank": "same"},
        ) as subgraph:
            subgraph.attr(rank="same")
            if self.parent:
                subgraph.edge(self.parent, self.upward_link_id)

            if self.below:
                subgraph.edge(self.below, self.upward_link_id, style="invis")

            # if self.sibling:
            #     dot.edge(
            #         self.sibling,
            #         self.link_id,
            #         rank="same",
            #         style="dotted",
            #         constraint="false",
            #         dir="none",
            #     )
            me = self.render_individual()
            if len(self.partnerships) == 0:
                subgraph.node(self.node_id, me)
            elif len(self.partnerships) == 1:
                self.partnerships[0].attach(subgraph)
                subgraph.node(self.node_id, me)
            elif len(self.partnerships) == 2:
                print(self.node_id, "has two partners")
                subgraph.node(self.node_id, me)
                self.partnerships[0].attach(subgraph)
                self.partnerships[1].attach(subgraph)

            return self.node_id

    def attach_collapsed_children(self, dot):
        children_id = f"{self.link_id}_children"
        # dot.node(children_id, self.render_children())
        # dot.edge(self.link_id, children_id)

    def render_individual(self):
        dates = (
            (self.birth or "") if not self.death else f"{self.birth or ''}-{self.death}"
        )

        dates_format = (
            f"<TR><TD><FONT POINT-SIZE='10.0'>{dates}</FONT></TD></TR>" if dates else ""
        )
        port_format = "PORT='main'" if self.is_main else "PORT='spouse'"
        return f"<<TABLE CELLBORDER='0'><TR><TD {port_format}>{self.name}</TD></TR>{dates_format}</TABLE>>"
