import os
from dotenv import load_dotenv
from docusign_esign import ApiClient

load_dotenv()

def get_api_client():
    api_client = ApiClient()
    auth_server = os.getenv("AUTH_SERVER")
    api_client.set_oauth_host_name(auth_server)
    
    private_key_path = os.getenv("PRIVATE_KEY_FILE")
    with open(private_key_path) as key_file:
        private_key = key_file.read()

    token = api_client.request_jwt_user_token(
        client_id=os.getenv("INTEGRATION_KEY"),
        user_id=os.getenv("USER_ID"),
        oauth_host_name=auth_server,
        private_key_bytes=private_key.encode(),
        expires_in=3600,
        scopes=["signature", "impersonation"]
    )

    api_client.host = "https://na2.docusign.net/restapi"
    api_client.set_default_header("Authorization", f"Bearer {token.access_token}")
    return api_client
