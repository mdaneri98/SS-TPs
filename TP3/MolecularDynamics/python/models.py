class Particle:

    def __init__(self, id, radius, mass, x, y, vx, vy):
        self.id = id
        self.radius = radius
        self.mass = mass
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy


class State:
    def __init__(self, time, particles):
        self.time = time
        self.particles = particles
