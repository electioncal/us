from PIL import Image, ImageDraw, ImageFont

import math

twitter_template = Image.open("templates/twitter-1024x512.png")
instagram_template = Image.open("templates/instagram-1080x1080.png")

font_cache = {
    "light": {
        28: ImageFont.truetype('site/static/fonts/Roboto_Slab/static/RobotoSlab-Light.ttf', 28, layout_engine=ImageFont.LAYOUT_RAQM)
    },
    "regular": {
        40: ImageFont.truetype('site/static/fonts/Roboto_Slab/static/RobotoSlab-Regular.ttf', 40, layout_engine=ImageFont.LAYOUT_RAQM)
    },
    "bold": {
        30: ImageFont.truetype('site/static/fonts/Roboto_Slab/static/RobotoSlab-Bold.ttf', 30, layout_engine=ImageFont.LAYOUT_RAQM)
    }
}
def font(weight, size):
    if size not in font_cache[weight]:
        start_size = next(iter(font_cache[weight].values()))
        font_cache[weight][size] = start_size.font_variant(size=size)
    return font_cache[weight][size]

sites = {
    "twitter": {
        "template": twitter_template,
        "location_pos": (60, 53),
        "location_size": 28,
        "reminder_y": 138,
        "reminder_size": 30,
        "main_date_y": 200,
        "main_date_size": 44,
        "secondary_y": 255,
        "secondary_size": 28,
        "explanation_-y": 170,
        "explanation_size": 20
    },
    "instagram": {
        "template": instagram_template,
        "location_pos": (93, 86),
        "location_size": 44,
        "reminder_y": 320,
        "reminder_size": 54,
        "main_date_y": 435,
        "main_date_size": 88,
        "secondary_y": 545,
        "secondary_size": 52,
        "explanation_-y": 370,
        "explanation_size": 37
    }
}

def draw_centered(draw, centerx, y, text, **kwargs):
    size = draw.textsize(text, font=kwargs.get("font", None))
    draw.text((centerx - size[0] // 2, y), text, **kwargs)

def render_image(fn, site, state=None, county=None, reminder=None, main_date="", secondary_date="", explanation=""):
    site = sites[site]
    template = site["template"]
    height = template.height
    centerx = template.width // 2
    img = template.copy()
    d = ImageDraw.Draw(img)
    if county:
        state = county + ", " + state
    if state:
        d.text(site["location_pos"], " ".join(state.upper()), fill="#ffffff", font=font("regular", site["location_size"]))
    if reminder:
        draw_centered(d, centerx, site["reminder_y"], reminder, fill="#ffffff", font=font("light", site["reminder_size"]))
    if main_date:
        if main_date in ("Today", "Tomorrow"):
            main_date = main_date.upper()
        draw_centered(d, centerx, site["main_date_y"], main_date, fill="#ffffff", font=font("regular", site["main_date_size"]))
    if secondary_date:
        draw_centered(d, centerx, site["secondary_y"], secondary_date, fill="#ffffff", font=font("light", site["secondary_size"]))
    if explanation:
        draw_centered(d, centerx, height - site["explanation_-y"], explanation, fill="#ffffff", font=font("light", site["explanation_size"]))

    img.save(fn)

if __name__ == "__main__":
    render_image("test.png", "instagram",
        state="Alabama",
        reminder="Mail voter registration by:",
        main_date="Today",
        secondary_date="(June 28th)",
        explanation="Voter registration must be received by July 6th.")
