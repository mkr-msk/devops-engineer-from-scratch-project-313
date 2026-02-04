import json


def test_ping_endpoint(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.data == b"pong"


def test_get_empty_links_list(client):
    response = client.get("/api/links")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_create_link(client):
    response = client.post(
        "/api/links",
        data=json.dumps(
            {
                "original_url": "https://example.com/very-long-url",
                "short_name": "example",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert "id" in data
    assert data["original_url"] == "https://example.com/very-long-url"
    assert data["short_name"] == "example"
    assert data["short_url"] == "http://testserver/r/example"
    assert "created_at" in data


def test_create_link_with_invalid_url(client):
    response = client.post(
        "/api/links",
        data=json.dumps({"original_url": "not-a-valid-url", "short_name": "test"}),
        content_type="application/json",
    )

    assert response.status_code == 422
    data = response.get_json()
    assert "detail" in data


def test_create_link_with_invalid_short_name(client):
    response = client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com", "short_name": "invalid/name"}
        ),
        content_type="application/json",
    )

    assert response.status_code == 422
    data = response.get_json()
    assert "detail" in data


def test_create_duplicate_short_name(client):
    client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com/first", "short_name": "duplicate"}
        ),
        content_type="application/json",
    )
    # duplicate
    response = client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com/second", "short_name": "duplicate"}
        ),
        content_type="application/json",
    )
    assert response.status_code == 409
    data = response.get_json()
    assert "detail" in data


def test_get_link_by_id(client):
    create_response = client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com/test", "short_name": "test"}
        ),
        content_type="application/json",
    )

    created_link = create_response.get_json()
    link_id = created_link["id"]
    response = client.get(f"/api/links/{link_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == link_id
    assert data["short_name"] == "test"
    assert data["original_url"] == "https://example.com/test"


def test_get_nonexistent_link(client):
    response = client.get("/api/links/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert "detail" in data


def test_update_link(client):
    create_response = client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com/old", "short_name": "oldname"}
        ),
        content_type="application/json",
    )
    created_link = create_response.get_json()
    link_id = created_link["id"]
    # update
    response = client.put(
        f"/api/links/{link_id}",
        data=json.dumps(
            {"original_url": "https://example.com/new", "short_name": "newname"}
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == link_id
    assert data["original_url"] == "https://example.com/new"
    assert data["short_name"] == "newname"
    assert data["short_url"] == "http://testserver/r/newname"


def test_update_link_partial(client):
    create_response = client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com/original", "short_name": "partial"}
        ),
        content_type="application/json",
    )
    created_link = create_response.get_json()
    link_id = created_link["id"]
    # update
    response = client.put(
        f"/api/links/{link_id}",
        data=json.dumps({"original_url": "https://example.com/updated"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["original_url"] == "https://example.com/updated"
    assert data["short_name"] == "partial"


def test_update_nonexistent_link(client):
    response = client.put(
        "/api/links/99999",
        data=json.dumps({"original_url": "https://example.com"}),
        content_type="application/json",
    )

    assert response.status_code == 404


def test_update_link_duplicate_short_name(client):
    client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com/first", "short_name": "first"}
        ),
        content_type="application/json",
    )
    create_response = client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com/second", "short_name": "second"}
        ),
        content_type="application/json",
    )
    second_id = create_response.get_json()["id"]
    response = client.put(
        f"/api/links/{second_id}",
        data=json.dumps({"short_name": "first"}),
        content_type="application/json",
    )

    assert response.status_code == 409


def test_delete_link(client):
    create_response = client.post(
        "/api/links",
        data=json.dumps(
            {"original_url": "https://example.com/delete", "short_name": "delete"}
        ),
        content_type="application/json",
    )

    link_id = create_response.get_json()["id"]
    response = client.delete(f"/api/links/{link_id}")
    assert response.status_code == 204
    assert response.data == b""
    get_response = client.get(f"/api/links/{link_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_link(client):
    response = client.delete("/api/links/99999")
    assert response.status_code == 404


def test_redirect_to_original_url(client):
    client.post(
        "/api/links",
        data=json.dumps(
            {
                "original_url": "https://example.com/destination",
                "short_name": "redirect",
            }
        ),
        content_type="application/json",
    )

    response = client.get("/r/redirect", follow_redirects=False)
    assert response.status_code == 301
    assert response.location == "https://example.com/destination"


def test_redirect_nonexistent_short_name(client):
    response = client.get("/r/nonexistent")
    assert response.status_code == 404
    data = response.get_json()
    assert "detail" in data


def test_pagination_first_page(client):
    for i in range(15):
        client.post(
            "/api/links",
            data=json.dumps(
                {"original_url": f"https://example.com/{i}", "short_name": f"link{i}"}
            ),
            content_type="application/json",
        )

    response = client.get("/api/links?range=[0,9]")
    assert response.status_code == 200
    assert "Content-Range" in response.headers
    assert response.headers["Content-Range"] == "links 1-10/15"
    data = response.get_json()
    assert len(data) == 10
    ids = [link["id"] for link in data]
    assert ids == list(range(1, 11))


def test_pagination_middle_page(client):
    for i in range(15):
        client.post(
            "/api/links",
            data=json.dumps(
                {"original_url": f"https://example.com/{i}", "short_name": f"link{i}"}
            ),
            content_type="application/json",
        )

    response = client.get("/api/links?range=[5,9]")
    assert response.status_code == 200
    assert response.headers["Content-Range"] == "links 6-10/15"
    data = response.get_json()
    assert len(data) == 5
    ids = [link["id"] for link in data]
    assert ids == list(range(6, 11))


def test_pagination_last_page_partial(client):
    for i in range(12):
        client.post(
            "/api/links",
            data=json.dumps(
                {"original_url": f"https://example.com/{i}", "short_name": f"link{i}"}
            ),
            content_type="application/json",
        )

    response = client.get("/api/links?range=[10,19]")
    assert response.status_code == 200
    assert response.headers["Content-Range"] == "links 11-12/12"
    data = response.get_json()
    assert len(data) == 2
    ids = [link["id"] for link in data]
    assert ids == [11, 12]


def test_pagination_out_of_range(client):
    for i in range(5):
        client.post(
            "/api/links",
            data=json.dumps(
                {"original_url": f"https://example.com/{i}", "short_name": f"link{i}"}
            ),
            content_type="application/json",
        )

    response = client.get("/api/links?range=[100,109]")
    assert response.status_code == 200
    assert response.headers["Content-Range"] == "links */5"
    data = response.get_json()
    assert len(data) == 0


def test_pagination_invalid_format(client):
    response = client.get("/api/links?range=invalid")
    assert response.status_code == 400
    data = response.get_json()
    assert "detail" in data


def test_pagination_negative_values(client):
    response = client.get("/api/links?range=[-5,9]")
    assert response.status_code == 400
    data = response.get_json()
    assert "detail" in data
    assert "non-negative" in data["detail"].lower()


def test_get_all_links_without_pagination(client):
    for i in range(5):
        client.post(
            "/api/links",
            data=json.dumps(
                {"original_url": f"https://example.com/{i}", "short_name": f"link{i}"}
            ),
            content_type="application/json",
        )

    response = client.get("/api/links")
    assert response.status_code == 200
    assert response.headers["Content-Range"] == "links 1-5/5"
    data = response.get_json()
    assert len(data) == 5
