from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import html

app = FastAPI()

@app.get("/send_anonymous/{username}", response_class=HTMLResponse)
@app.get("/send_anonymous", response_class=HTMLResponse)  # 👈 handles no username
async def send_message(username: str = "me"):
    
    user_display = html.escape(username)

    title = f"Send {user_display} an Anonymous Message 👀"
    description = (
        f"Send {user_display} a message anonymously. "
        f"They won’t know it’s you 😉. You might even get a reply!"
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
        <meta property="og:image" content="https://whisperbin.shop/preview.png" />
        <meta property="og:url" content="https://whisperbin.shop/send/{user_display}" />
        <meta property="og:type" content="website" />
        <meta http-equiv="refresh" content="0; url=/https://whisperbin.shop/send_messages/{user_display}" />
        <meta property="og:site_name" content="WhisperBin" />

        <!-- Twitter -->
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{title}" />
        <meta name="twitter:description" content="{description}" />
        <meta name="twitter:image" content="https://whisperbin.shop/preview.png" />

    </html>
    """