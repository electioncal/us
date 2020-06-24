import cairocffi as cairo
import pangocffi as pango
import pangocairocffi as pangocairo

width = 1080
height = 540

s = cairo.SVGSurface("test.svg", width, height)

c = cairo.Context(s)

# Fill background
c.move_to(0, 0)
c.line_to(0, height)
c.line_to(width, height)
c.line_to(width, 0)
c.line_to(0, 0)

c.set_source_rgb(0.1, 0.1, 0.1)
c.fill()

# test text
c.move_to(0, 10)

#context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

layout = pangocairo.create_layout(c)
layout.set_width(pango.units_from_double(width))
layout.set_alignment(pango.Alignment.CENTER)
layout.set_spacing(12)
layout.set_markup("<span font=\"sans-serif 32\">Madison County, Kentucky</span>")

c.set_source_rgb(1, 1, 1)
pangocairo.show_layout(c, layout)

c.move_to(0, 150)
layout.set_markup("<span font=\"sans-serif 52\" foreground=\"#eeeeee\">Vote in person by</span>\n"
                  "<span font=\"sans-serif 60\">Today!</span>\n"
                  "<span font=\"sans-serif 48\" foreground=\"#CCCCCC\">(June 23rd)</span>\n")
pangocairo.show_layout(c, layout)


s.write_to_png("test.png")
s.finish()
