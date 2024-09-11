package models;

import java.util.Set;

public class HorizontalWall extends Wall {

    public HorizontalWall(double l) {
        super(l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocityX() == 0) {
            return Double.POSITIVE_INFINITY;
        } else if (particle.getVelocityX() > 0) {
            return (this.getL() - particle.getRadius() - particle.getPosX()) / particle.getVelocityX();
        }
        return (0 - particle.getRadius() - particle.getPosX()) / particle.getVelocityX();
    }

    public void incrementMomentum(Particle particle) {
        double newMomentum = this.momentum.get(index) + 2 * particle.getMass() *  Math.abs(particle.getVelocityX());
        this.momentum.set(index, newMomentum);
    }

    @Override
    public Particle applyCollision(final Particle p) {
        this.incrementMomentum(p);
        return new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelocity(), Math.PI - p.getAngle(), p.getRadius(), p.getMass());
    }


}
