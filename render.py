def titleize(string):
    return string.lower().replace(" ", "_")


def individual_data(person, prefix=""):
    if not person:
        return {}
    dates = (
        (person.birth or None)
        if not person.death
        else f"{person.birth or ''}-{person.death}"
    )
    return {
        f"{prefix}dates": dates,
        f"{prefix}id": person.node_id,
        f"{prefix}name": person.name,
        f"{prefix}dates_html": f"<FONT POINT-SIZE='10.0'>{dates}</FONT>"
        if dates
        else "",
    }


def render_individual(person, embedded=False):
    data = individual_data(person)
    inner = """
      <TABLE BORDER='0'>
        <TR><TD ALIGN='left' port='primary'>{dates_html}</TD></TR>
        <TR><TD BORDER='1' PORT='main'>{name}</TD></TR>
      </TABLE>""".format(
        **data
    )
    return inner if embedded else f"<{inner}>"


spacers = {
    "married": "__",
    "divorced": "___<FONT POINT-SIZE='10.0'>div.</FONT>___",
    "other": "_ _ _",
}


def render_partnership(person, primary_partnership, secondary_partnership=None):

    data = {
        **individual_data(person),
        **individual_data(primary_partnership.spouse, "primary_"),
        "primary_partner_spacer": spacers.get(
            primary_partnership.status, spacers["other"]
        ),
    }
    if secondary_partnership:
        data.update(**individual_data(secondary_partnership.spouse, "secondary_"))
        data["secondary_partner_spacer"] = spacers.get(
            secondary_partnership.status, spacers["other"]
        )
        content = """
            <TABLE BORDER='0' CELLBORDER='0'>
                <TR>
                    <TD ALIGN='left'>{secondary_dates_html}</TD>
                    <TD></TD>
                    <TD ALIGN='left'>{dates_html}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
                    <TD></TD>
                    <TD ALIGN='left'>{primary_dates_html}</TD>
                </TR>
                <TR>
                    <TD PORT='secondary' BORDER='1'>{secondary_name}</TD>
                    <TD PORT='secondary_joiner'>{secondary_partner_spacer}</TD>
                    <TD BORDER='1' PORT='main'>{name}</TD>
                    <TD PORT='primary_joiner'>{primary_partner_spacer}</TD>
                    <TD BORDER='1' PORT='primary'>{primary_name}</TD>
                </TR>
            </TABLE>
        """.format(
            **data,
            primary_joiner=primary_partnership.spouse.node_id,
            secondary_joiner=secondary_partnership.spouse.node_id,
        )
    elif primary_partnership.spouse:
        try:
            content = """
                <TABLE BORDER='0' CELLBORDER='0'>
                    <TR>
                        <TD ALIGN='left'>{dates_html}</TD>
                        <TD></TD>
                        <TD ALIGN='left'>{primary_dates_html}</TD>
                    </TR>
                    <TR>
                        <TD BORDER='1' PORT='main'>{name}</TD>
                        <TD PORT='primary_joiner'>{primary_partner_spacer}</TD>
                        <TD BORDER='1' PORT='primary'>{primary_name}</TD>
                    </TR>
                </TABLE>
            """.format(
                **data, primary_joiner=primary_partnership.spouse.node_id
            )
        except:
            print(data)
            raise
    else:
        content = render_individual(person, embedded=True)
    return f"<{content}>"


class PartnershipRender:
    TYPES = ["primary", "secondary"]

    def __init__(
        self,
        attached_id,
        children=None,
        spouse=None,
        collapse_children=True,
        partnership_type="primary",
        status="married",
    ):
        self.attached_id = attached_id
        self.children = children or []
        self.collapse_children = collapse_children
        self.partnership_type = partnership_type
        self.spouse = PersonRender(**spouse, is_main=False) if spouse else None
        self.status = status

    def __str__(self):
        return f"PartnershipRender(spouse={self.spouse_name}, children={len(self.children)}, collapse={self.collapse_children})"

    @property
    def spouse_name(self):
        return self.spouse and self.spouse.node_id

    @property
    def node_id(self):
        return self.spouse_name or self.attached_id

    @property
    def joiner_id(self):
        return (
            f"{self.attached_id}:{self.partnership_type}_joiner"
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
            [
                f"<TR><TD>{render_individual(p, embedded=True)}</TD></TR>"
                for p in people_the_children
            ]
        )

        return f"<<TABLE border='1' cellborder='0'>{row_the_children}</TABLE>>"

    def attach(self, dot):
        if not self.spouse:
            # If nobody as spouse, just use the original person
            return self.attached_id

        spouse_id = self.spouse.attach(dot)
        dot.node(self.node_id, "", shape="insulator")
        dot.edge(self.attached_id, self.node_id, dir="none")
        dot.edge(self.node_id, spouse_id, dir="none")

    def attach_collapsed_children(self, dot):
        children_id = f"{self.node_id}_children"
        dot.node(children_id, self.render_children())
        dot.edge(self.joiner_id, children_id)


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
        partnership_options = PartnershipRender.TYPES[:]
        self.partnerships = [
            PartnershipRender(
                self.node_id, **p, partnership_type=partnership_options.pop()
            )
            for p in partnerships or []
        ]

    @property
    def downward_link_id(self):
        return f"{self.node_id}:s"

    @property
    def upward_link_id(self):
        return f"{self.node_id}:main:ne"

    @property
    def node_id(self):
        return titleize(self.name)

    @property
    def person_count(self):
        return 1 + len(self.partnerships)

    def attach(self, dot):
        if self.parent:
            dot.edge(self.parent, self.upward_link_id)

        if self.below:
            dot.edge(self.below, self.upward_link_id, style="invis")

        with dot.subgraph(
            name=f"{self.node_id}_wrapper",
        ) as subgraph:
            subgraph.attr(rank="same")
            # if self.sibling:
            #     dot.edge(
            #         self.sibling,
            #         self.link_id,
            #         rank="same",
            #         style="dotted",
            #         constraint="false",
            #         dir="none",
            #     )
            me = render_individual(self)
            if len(self.partnerships) == 0:
                subgraph.node(self.node_id, me)
            elif len(self.partnerships) == 1:
                subgraph.node(
                    self.node_id, render_partnership(self, self.partnerships[0])
                )
            elif len(self.partnerships) == 2:
                subgraph.node(
                    self.node_id,
                    render_partnership(
                        self, self.partnerships[1], self.partnerships[0]
                    ),
                )

            return self.node_id
