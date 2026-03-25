from pydantic import EmailStr


def mask_email(email: EmailStr):
    first = email[0]
    indexOf = email.index("@")
    stars = "*" * (indexOf - 1)
    second = email[indexOf:]
    return f"{first}{stars}{second}"