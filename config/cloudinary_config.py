import cloudinary
from config.setting import Setting

setting = Setting()

cloudinary.config(
    cloud_name="dcrpmvykk",
    api_key=setting.cloudinaryapi,
    api_secret=setting.cloudinarysecret
)