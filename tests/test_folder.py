def test_folder_route(client, auth):
    # Simulate a login
    response = auth.login()
    with client:
        response = client.get("/vault/Passing Folder")
        assert response.status_code == 200
        assert b"Fake Name" in response.data
        assert b"Fake Username" in response.data
        assert b"asdf1234" in response.data
        assert b"www.google.com" in response.data
        assert b"note" in response.data
