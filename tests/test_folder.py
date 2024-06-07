from app.db import get_folder_id_from_database

def test_folder_route(client, auth):
    # Simulate a login
    response = auth.login()
    with client:
        folder_name = "Passing Folder"  # Replace with the actual folder name
        with client.application.app_context():  # Ensure we are within the application context
            folder_id = get_folder_id_from_database(folder_name)  # Retrieve folder_id

        # response = client.get("/vault/FOLDER_ID/Passing Folder")
        response = client.get(f"/vault/{folder_id}/{folder_name}")
        print(response)
        assert response.status_code == 200
        assert b"Fake Name" in response.data
        assert b"Fake Username" in response.data
        assert b"asdf1234" in response.data
        assert b"www.google.com" in response.data
        assert b"note" in response.data
