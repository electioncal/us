import cairo

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
c.move_to(10, 10)

c.set_source_rgb(0.9, 0.9, 0.9)
c.show_text("hello world")


s.write_to_png("test.png")
s.finish()
