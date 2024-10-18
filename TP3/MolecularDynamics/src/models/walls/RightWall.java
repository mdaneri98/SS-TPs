package models.walls;

import models.particles.Particle;
import models.particles.StaticParticle;
import models.particles.Velocity;

public class RightWall extends Wall {

    public RightWall(WallType type, double l) {
        super(type, l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocity().getX() <= 0) {
            return Double.POSITIVE_INFINITY;
        } else {
            return (this.getL() - particle.getRadius() - particle.getPosition().getX()) / particle.getVelocity().getX();
        }
    }

    @Override
    public double getMomentum(Particle particle) {
        return 2 * particle.getMass() * Math.abs(particle.getVelocity().getX());
    }

    @Override
    public String toString() {
        return "RightWall";
    }

}