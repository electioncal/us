from PIL import Image, ImageDraw, ImageFont

import math

font28 = ImageFont.truetype('site/static/fonts/Roboto_Slab/static/RobotoSlab-Light.ttf', 28, layout_engine=ImageFont.LAYOUT_RAQM)
font20 = font28.font_variant(size=20)
font18 = font28.font_variant(size=18)
font40 = font28.font_variant(size=40)
font30 = font28.font_variant(size=30)
font40r = ImageFont.truetype('site/static/fonts/Roboto_Slab/static/RobotoSlab-Regular.ttf', 40, layout_engine=ImageFont.LAYOUT_RAQM)
font44r = font40r.font_variant(size=44)
font28r = font40r.font_variant(size=28)
font18r = font40r.font_variant(size=18)
font30b = ImageFont.truetype('site/static/fonts/Roboto_Slab/static/RobotoSlab-Bold.ttf', 30, layout_engine=ImageFont.LAYOUT_RAQM)

twitter_template = Image.open("templates/twitter-1024x512.png")

def draw_centered(draw, centerx, y, text, **kwargs):
    size = draw.textsize(text, font=kwargs.get("font", None))
    draw.text((centerx - size[0] // 2, y), text, **kwargs)

def render_twitter_image(fn, state=None, county=None, reminder=None, main_date="", secondary_date="", explanation=""):
    height = twitter_template.height
    centerx = twitter_template.width // 2
    img = twitter_template.copy()
    d = ImageDraw.Draw(img)
    if county:
        state = county + ", " + state
    if state:
        d.text((60, 53), " ".join(state.upper()), fill="#ffffff", font=font28r)
    if reminder:
        draw_centered(d, centerx, 138, reminder, fill="#ffffff", font=font30)
    if main_date:
        if main_date in ("Today", "Tomorrow"):
            main_date = main_date.upper()
        draw_centered(d, centerx, 200, main_date, fill="#ffffff", font=font44r)
    if secondary_date:
        draw_centered(d, centerx, 255, secondary_date, fill="#ffffff", font=font28)
    if explanation:
        draw_centered(d, centerx, height - 170, explanation, fill="#ffffff", font=font20)

    img.save(fn)

if __name__ == "__main__":
    render_twitter_image("test.png",
        state="Alabama",
        reminder="Mail voter registration by:",
        main_date="Today",
        secondary_date="(June 28th)",
        explanation="Voter registration must be received by July 6th.")
