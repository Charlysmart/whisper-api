import requests

from config.setting import Setting

SENDIAPI = Setting().sendiapi
class SendEmail:
    def __init__(self):
        pass 
    def send_verification_email(self, email, username, code):
        template_id = "5e7fe193-9051-47c9-977c-b44f6c81c96b"
        try:
            response = requests.post(
                "https://app.usesendi.com/api/emails",
                headers={
                    "Authorization" : f"Bearer {SENDIAPI}",
                    "Content-Type" : "application/json"
                },
                json={
                    "subject": "Verify your WhisperBin account",
                    "from": "WhisperBin <noreply@whisperbin.shop>",
                    "to" : [email],
                    "template_id" : template_id,
                    "template_variables" : {
                        "verification_code": code,
                        "website_url": "https://whisperbin.vercel.app",
                        "username": username
                    }
                }
            )
            if response.status_code == 200:
                return True
            else:
                print(response.text)
                return False
        except Exception as e:
            print("Error: ", e)
            return False
    
