from config.setting import Setting
from mailersend import MailerSendClient, EmailBuilder

MAILERSEND_API_KEY = Setting().mailersendapi
ms = MailerSendClient(MAILERSEND_API_KEY)


def send_email(email, username, code):
    template_id = "pq3enl6e77r42vwr"

    email_data = (
        EmailBuilder()
        .from_email("no-reply@whisperbin.shop", "Whisperbin")
        .to_many([
            {
                "email": email,
                "name": username
            }
        ])
        .subject("Your verification code")
        .template(template_id)
        .personalize_many([
            {
                "email": email,
                "data": {
                    "verification_code": code,
                    "website_url": "https://whisperbin.vercel.app",
                    "username": username
                }
            }
        ])
        .build()
    )

    try:
        response = ms.emails.send(email_data)
        return True
    except Exception as e:
        return False