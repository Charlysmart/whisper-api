import requests

from config.setting import Setting

setting = Setting()
class SendEmail:
    def __init__(self):
        pass 
    def send_verification_email(self, email: str, username: str, code: str):
        template_id = "5e7fe193-9051-47c9-977c-b44f6c81c96b"
        try:
            response = requests.post(
                "https://app.usesendi.com/api/emails",
                headers={
                    "Authorization" : f"Bearer {setting.sendiapi}",
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
            if response.ok:
                print("Sent:", response.json()["id"])
                return True
            else:
                print("Error:", response.json()["error"])
                return False
        except Exception as e:
            print("Error: ", e)
            return False
    
    
    def send_reset_email(self, email: str, username: str, code: str):
        template_id = "b3af3391-b80f-4a61-a192-33fc601fe64d"
        try:
            response = requests.post(
                "https://app.usesendi.com/api/emails",
                headers={
                    "Authorization" : f"Bearer {setting.sendiapi}",
                    "Content-Type" : "application/json"
                },
                json={
                    "subject": "Reset Password OTP",
                    "from": "WhisperBin <noreply@whisperbin.shop>",
                    "to" : [email],
                    "template_id" : template_id,
                    "template_variables" : {
                        "reset_url": f"{setting.sitename}/reset_password?token={code}",
                        "username": username,
                        "website_url": setting.sitename
                    }
                }
            )
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False