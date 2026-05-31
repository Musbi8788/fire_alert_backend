VALID_REPORT = {
    "description": "Large fire near the central market, spreading fast.",
    "latitude": 13.4549,
    "longitude": -16.5790,
    "address": "Serrekunda Market",
}


def test_create_report_requires_auth(client):
    response = client.post("/api/reports", json=VALID_REPORT)
    assert response.status_code == 401


def test_list_reports_requires_auth(client):
    response = client.get("/api/reports")
    assert response.status_code == 401


def test_create_and_list_own_reports(client, auth_headers):
    created = client.post("/api/reports", json=VALID_REPORT, headers=auth_headers)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["description"] == VALID_REPORT["description"]
    assert body["status"] == "pending"

    listed = client.get("/api/reports", headers=auth_headers)
    assert listed.status_code == 200
    reports = listed.json()
    assert len(reports) == 1
    assert reports[0]["id"] == body["id"]


def test_create_report_rejects_short_description(client, auth_headers):
    bad = {**VALID_REPORT, "description": "fire"}  # below min_length=10
    response = client.post("/api/reports", json=bad, headers=auth_headers)
    assert response.status_code == 422


def test_non_admin_cannot_access_admin_reports(client, auth_headers):
    response = client.get("/api/admin/reports", headers=auth_headers)
    assert response.status_code == 403


def test_admin_reports_requires_auth(client):
    response = client.get("/api/admin/reports")
    assert response.status_code == 401
