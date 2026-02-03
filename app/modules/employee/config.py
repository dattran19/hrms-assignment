# Allowlist: only these can ever be returned
ALLOWED_COLUMNS = {
    "first_name",
    "last_name",
    "display_name",
    "email_addr",
    "phone",
    "status",
    "dept_descr",
    "location_descr",
    "jobcode_descr",
    "position_descr",
    "company_descr",
    "empl_status",
}

# Demo per-org columns (pretend stored in DB/file)
ORG_COLUMNS = {
    1: [
        "first_name",
        "last_name",
        "display_name",
        "email_addr",
        "phone",
        "dept_descr",
        "location_descr",
        "position_descr",
        "company_descr",
        "empl_status",
    ],
    2: [
        "display_name",
        "email_addr",
        "phone",
        "dept_descr",
        "position_descr",
        "empl_status",
    ],
}

DEFAULT_COLUMNS = [
    "display_name",
    "email_addr",
    "phone",
    "empl_status",
    "dept_descr",
    "location_descr",
    "position_descr",
]


def get_columns_for_org(org_id: int):
    return ORG_COLUMNS.get(org_id, DEFAULT_COLUMNS)
