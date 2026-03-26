from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import html

from config.setting import Setting

metaredirect_router = APIRouter(prefix="/pages", tags=["Pages"])
setting = Setting()
@metaredirect_router.get("/drop_anonymous/{username}", response_class=HTMLResponse)
async def drop_anonymous(request: Request, username: str):

    user_display = html.escape(username)

    title = f"Send {user_display} an Anonymous Message 👀"
    description = (
        f"Send {user_display} a message anonymously. "
        f"They won’t know it’s you 😉."
    )

    redirect_url = f"{setting.sitename}/send_message/{user_display}"

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Open Graph -->
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="https://res.cloudinary.com/dcrpmvykk/image/upload/v1774479465/unnamed_6_wnwcm6.png" />
    <meta property="og:url" content="{setting.sitename}/pages/drop_anonymous/{user_display}" />
    <meta property="og:type" content="website" />

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="https://res.cloudinary.com/dcrpmvykk/image/upload/v1774479465/unnamed_6_wnwcm6.png" />

    <!-- Instant redirect -->
    <script>
        window.location.replace("{redirect_url}");
    </script>

    <noscript>
        <meta http-equiv="refresh" content="0;url={redirect_url}" />
    </noscript>
</head>
<body></body>
</html>
""")