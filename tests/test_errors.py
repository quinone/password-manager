def test_404_error(client):
    response = client.get("/page-does-not-exist")
    assert response.status_code == 404
    assert b"404 Page Not Found" in response.data


# def test_500_error(client, monkeypatch):
#    pass
