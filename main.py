import audible, os

Auth_file = "Credentials.txt"

if(os.path.exists(Auth_file)):
    auth = audible.FileAuthenticator(Auth_file)
else:
    auth = audible.LoginAuthenticator(
        input("Username: "),
        input("Password: "),
        locale="it")
    auth.to_file(Auth_file, encryption=False)

client = audible.Client(auth)
asin = "3748018037"

child_asin = client.get(
    path=f"library/{asin}",
            params={
                "response_groups": (
                    "relationships"
                )
            }
        )

license = client.post(
   "content/{child_asin}/licenserequest",
    body={
        "drm_type": "Adrm",
        "consumption_type": "Download",
        "quality":"Extreme"
    }
)
content_url = license['content_license']['content_metadata']['content_url']['offline_url']