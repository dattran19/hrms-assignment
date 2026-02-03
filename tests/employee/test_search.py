import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.employee.config import ALLOWED_COLUMNS, ORG_COLUMNS

BASE = "/api/v1"


@pytest.fixture
def client():
    from app.db.pool import close_pool, init_pool

    # Initialize DB pool (TestClient doesn't trigger startup events)
    init_pool()

    yield TestClient(app)

    # Cleanup
    close_pool()


def _assert_item_keys_valid(item: dict):
    # always present
    assert "employee_id" in item

    # only allow employee_id + allowed columns
    extra = set(item.keys()) - ({"employee_id"} | ALLOWED_COLUMNS)
    assert extra == set(), f"Unexpected keys leaked: {extra}"


def test_invalid_api_key_returns_401(client):
    r = client.get(f"{BASE}/orgs/1/employees/search?q=a", headers={"X-API-Key": "nope"})
    assert r.status_code == 401


def test_org_isolation_forbidden_cross_org(client):
    # dev-key-1 is org 1, should not access org 2
    r = client.get(
        f"{BASE}/orgs/2/employees/search?q=a", headers={"X-API-Key": "dev-key-1"}
    )
    assert r.status_code == 403


def test_search_response_shape_and_allowlist(client):
    r = client.get(
        f"{BASE}/orgs/1/employees/search?q=a&limit=5",
        headers={"X-API-Key": "dev-key-1"},
    )
    assert r.status_code == 200
    data = r.json()

    assert "items" in data
    assert "next_cursor" in data
    assert "limit" in data

    for item in data["items"]:
        _assert_item_keys_valid(item)


def test_dynamic_columns_org1_vs_org2(client):
    # Org 1 has more columns configured than org 2
    r1 = client.get(
        f"{BASE}/orgs/1/employees/search?q=a&limit=1",
        headers={"X-API-Key": "dev-key-1"},
    )
    assert r1.status_code == 200
    items1 = r1.json()["items"]
    assert len(items1) >= 0  # don’t assume data, but if present verify shape

    if items1:
        item1 = items1[0]
        # Should not return columns not in org config (even if allowed globally)
        org1_cols = set(ORG_COLUMNS[1])
        returned_cols = set(item1.keys()) - {"employee_id"}
        assert returned_cols.issubset(org1_cols)

    r2 = client.get(
        f"{BASE}/orgs/2/employees/search?q=a&limit=1",
        headers={"X-API-Key": "dev-key-2"},
    )
    assert r2.status_code == 200
    items2 = r2.json()["items"]

    if items2:
        item2 = items2[0]
        org2_cols = set(ORG_COLUMNS[2])
        returned_cols = set(item2.keys()) - {"employee_id"}
        assert returned_cols.issubset(org2_cols)

        # A very clear dynamic-column proof: org2 should NOT have first/last name
        assert "first_name" not in item2
        assert "last_name" not in item2


def test_keyset_pagination_no_duplicates(client):
    # Page 1 (no q) - more reliable than FTS
    r1 = client.get(
        f"{BASE}/orgs/1/employees/search?limit=2", headers={"X-API-Key": "dev-key-1"}
    )
    assert r1.status_code == 200
    d1 = r1.json()
    items1 = d1["items"]
    assert len(items1) == 2
    assert d1["next_cursor"] is not None

    ids1 = {it["employee_id"] for it in items1}
    cursor = d1["next_cursor"]

    # Page 2 using cursor
    r2 = client.get(
        f"{BASE}/orgs/1/employees/search",
        headers={"X-API-Key": "dev-key-1"},
        params={
            "limit": 2,
            "cursor_updated_at": cursor["updated_at"],
            "cursor_employee_id": cursor["employee_id"],
        },
    )
    assert r2.status_code == 200
    d2 = r2.json()
    ids2 = {it["employee_id"] for it in d2["items"]}

    # No duplicates between pages
    assert ids1.isdisjoint(ids2)
