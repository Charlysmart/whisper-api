from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import html

from config.setting import Setting

metaredirect_router = APIRouter(prefix="/pages", tags=["Pages"])
setting = Setting()

@metaredirect_router.get("/drop_anonymous/{username}", response_class=HTMLResponse)
async def drop_anonymous(request: Request, username: str):

    user_agent = request.headers.get("user-agent", "").lower()

    is_bot = any(bot in user_agent for bot in [
        "whatsapp", "facebookexternalhit", "twitterbot", 
        "linkedinbot", "slackbot", "discordbot"
    ])

    user_display = html.escape(username)

    title = f"Send {user_display} an Anonymous Message 👀"
    description = (
        f"Send {user_display} a message anonymously. "
        f"They won’t know it’s you 😉."
    )

    # 🟢 BOT → return preview (NO redirect)
    if is_bot:
        return f"""
        <html>
        <head>
            <meta property="og:title" content="{title}" />
            <meta property="og:description" content="{description}" />
            <meta property="og:image" content="https://res.cloudinary.com/dcrpmvykk/image/upload/v1774479465/unnamed_6_wnwcm6.png" />
            <meta property="og:url" content="{setting.sitename}/pages/drop_anonymous/{user_display}" />
            <meta property="og:image:width" content="1200" />
            <meta property="og:image:height" content="630" />
            <meta property="og:image:type" content="image/png" />
            <meta property="og:type" content="website" />

            <!-- Twitter -->
            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:title" content="{title}" />
            <meta name="twitter:description" content="{description}" />
            <meta name="twitter:image" content="https://res.cloudinary.com/dcrpmvykk/image/upload/v1774479465/unnamed_6_wnwcm6.png" />
        </head>
        </html>
        """

    # 🔵 REAL USER → instant invisible redirect
    return RedirectResponse(
        url=f"{setting.sitename}/send_message/{user_display}",
        status_code=302  # or 307
    )