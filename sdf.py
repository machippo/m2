import turtle,random
t = turtle.Pen()
t.shape('turtle')

iterations = 1
radius = 30
d = 100

while iterations<4:
    r,g,b = [random.random() for _ in range(3)]
    t.color(r,g,b)

    t.begin_fill()
    t.circle(radius)
    t.end_fill()

    if iterations != 3:
        t.fd(d)

    iterations += 1
    radius += 20
    d += 50
    
    
