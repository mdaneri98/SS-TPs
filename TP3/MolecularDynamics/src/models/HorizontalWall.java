package models;

import java.util.Set;

public class HorizontalWall extends Wall {

    public HorizontalWall(double l) {
        super(l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocityY() == 0) {
            return Double.POSITIVE_INFINITY; // Nunca colisionará si la velocidad en X es 0
        } else if (particle.getVelocityY() > 0) {
            // Colisión con la pared derecha
            return (this.getL() - particle.getRadius() - particle.getPosY()) / particle.getVelocityY();
        }
        // Colisión con la pared izquierda
        return (particle.getRadius() - particle.getPosY()) / particle.getVelocityY();
    }


    public void incrementMomentum(Particle particle) {
        double newMomentum = this.momentum.get(index) + 2 * particle.getMass() *  Math.abs(particle.getVelocityX());
        this.momentum.set(index, newMomentum);
    }

    @Override
    public Particle applyCollision(final Particle p) {
        this.incrementMomentum(p);
        return new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelocity(), - p.getAngle(), p.getRadius(), p.getMass());
    }


}
