from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import html

metaredirect_router = APIRouter(prefix="/pages", tags=["Pages"])

@metaredirect_router.get("/drop_anonymous/{username}", response_class=HTMLResponse)
@metaredirect_router.get("/drop_anonymous", response_class=HTMLResponse)
async def drop_anonymous(username: str = "me"):

    user_display = html.escape(username)

    title = f"Send {user_display} an Anonymous Message 👀"
    description = (
        f"Send {user_display} a message anonymously. "
        f"They won’t know it’s you 😉. You can even get a reply."
    )

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <title>{title}</title>

        <!-- Open Graph -->
        <meta property="og:title" content="{title}" />
        <meta property="og:description" content="{description}" />
        <meta property="og:image" content="https://res.cloudinary.com/dcrpmvykk/image/upload/v1774090729/unnamed_mg0stn.png" />
        <meta property="og:url" content="https://whisperbin.shop/pages/drop_anonymous/{user_display}" />
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="WhisperBin" />

        <!-- Twitter -->
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{title}" />
        <meta name="twitter:description" content="{description}" />
        <meta name="twitter:image" content="https://res.cloudinary.com/dcrpmvykk/image/upload/v1774090729/unnamed_mg0stn.png" />

        <!-- Smooth redirect (no visible page) -->
        <meta http-equiv="refresh" content="0; url=https://whisperbin.shop/send_message/{user_display}" />

    </head>
    </html>
    """