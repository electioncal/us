from PIL import Image, ImageDraw, ImageFont

import math

width = 1080
height = 565
scale_factor = 4

font30 = ImageFont.truetype('site/static/fonts/Open_Sans/OpenSans-Regular.ttf', 30, layout_engine=ImageFont.LAYOUT_RAQM)
font50 = font30.font_variant(size=50)
font60 = font30.font_variant(size=60)
font30b = ImageFont.truetype('site/static/fonts/Open_Sans/OpenSans-Bold.ttf', 30, layout_engine=ImageFont.LAYOUT_RAQM)

blue = "#1d00b2"
dblue = "#100090"
red = "#dd0000"
dred = "#bb0000"
white = "white"
bg = "#333333"

def draw_star(draw, center, *, radius=50, points=5, fill=None, stroke=None):
    cx, cy = center
    step = math.pi / points
    inr = radius * 2 / 5
    outr = radius
    for point in range(points):
        la = step * (2 * point - 1)
        left = (cx + inr * math.sin(la), cy - inr * math.cos(la))
        ta = step * (2 * point)
        tip = (cx + outr * math.sin(ta), cy - outr * math.cos(ta))
        ra = step * (2 * point + 1)
        right = (cx + inr * math.sin(ra), cy - inr * math.cos(ra))
        if isinstance(fill, list):
            l = len(fill)
            lf = fill[(2 * point) % l]
            rf = fill[(2 * point + 1) % l]
        else:
            lf = fill
            rf = fill
        draw.polygon([center, left, tip], fill=lf, outline=stroke)
        draw.polygon([center, tip, right], fill=rf, outline=stroke)

twitter_template = Image.new('RGB', (width * scale_factor, height * scale_factor), color = bg)

d = ImageDraw.Draw(twitter_template)
one_third = scale_factor * width // 3
d.rectangle([0, 0, one_third, 60 * scale_factor], fill=dblue)
spacing = 160
for y in range(3):
    shift = spacing / 2 * (y % 2)
    for i in range(15):
        draw_star(d, (i * spacing + shift, spacing / 2 * y - 3), radius=(spacing / 3), fill=blue)
# d.rectangle([one_third, 0, scale_factor * width + 1, 50 * scale_factor + 1], fill=red)
for y in range(2):
    if y % 2 == 0:
        f = red
    else:
        f = dred
    y = 30 * scale_factor * y
    d.rectangle([one_third, y, width * scale_factor, y + 30 * scale_factor], fill=f)
d.rectangle([0, 60 * scale_factor, width * scale_factor, height * scale_factor], fill=bg)

def draw_centered(draw, y, text, **kwargs):
    size = draw.textsize(text, font=kwargs.get("font", None))
    draw.text((540 - size[0] // 2, y), text, **kwargs)

colors = ["#444444", "#666666"] * 5
gray_colors = ["#444444", "#666666"] * 5
red_blue_colors = [blue, dblue, blue, dblue, red, dred, red, dred, red, dred]
colors = list(red_blue_colors)
stages = []
corner_radius = 30
star_pos = ((width - corner_radius - 4) * scale_factor, (height - corner_radius - 4) * scale_factor)
for i in range(len(colors)):
    draw_star(d, star_pos, fill=colors)
    stages.append(twitter_template.copy())
    if i < len(colors):
        colors[i] = gray_colors[i]

for i in range(len(colors)):
    draw_star(d, star_pos, fill=colors)
    stages.append(twitter_template.copy())
    if i < len(colors):
        colors[i] = red_blue_colors[i]

draw_star(d, star_pos, fill=colors, radius=corner_radius*scale_factor)

twitter_template = twitter_template.copy()
twitter_template.thumbnail((width, height), reducing_gap=1)
one_third = width // 3

def render_twitter_image(fn, state=None, county=None, reminder=None, main_date="", secondary_date="", explanation=""):
    img = twitter_template.copy()
    d = ImageDraw.Draw(img)
    if county:
        d.text((one_third + 6, 9), county, fill="#eeeeee", font=font30b)
    if state:
        size = d.textsize(state, font=font30b)
        d.text((one_third - 6 - size[0], 9), state, fill="#eeeeee", font=font30b)
    if reminder:
        draw_centered(d, 110, reminder, fill="#eeeeee", font=font50)
    if main_date:
        draw_centered(d, 210, main_date, fill="#ffffff", font=font60)
    if secondary_date:
        draw_centered(d, 310, secondary_date, fill="#eeeeee", font=font50)
    if explanation:
        draw_centered(d, height - 50, explanation, fill="#eeeeee", font=font30)

    img.save(fn)
#img.save("test.gif", save_all=True, append_images=stages, disposal=1, duration=200, loop=0)

if __name__ == "__main__":
    render_twitter_image("test.png", reminder="Check electioncal.us for deadlines by", main_date="June 29th", secondary_date="( Monday )", explanation="Washington, Oregon")
