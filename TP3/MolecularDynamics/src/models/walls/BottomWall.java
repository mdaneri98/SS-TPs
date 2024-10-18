package models.walls;

import models.particles.Particle;
import models.particles.StaticParticle;
import models.particles.Velocity;

public class BottomWall extends Wall {

    public BottomWall(WallType type, double l) {
        super(type, l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocity().getY() >= 0) {
            return Double.POSITIVE_INFINITY;
        } else {
            return (particle.getRadius() - particle.getPosition().getY()) / particle.getVelocity().getY();
        }
    }

    @Override
    public double getMomentum(Particle particle) {
        return 2 * particle.getMass() * Math.abs(particle.getVelocity().getY());
    }

    @Override
    public String toString() {
        return "BottomWall";
    }
}
