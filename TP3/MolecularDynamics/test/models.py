class Particle:

    def __init__(self, id, x, y, vx, vy):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy


class State:
    def __init__(self, time, particles):
        self.time = time
        self.particles = particles
