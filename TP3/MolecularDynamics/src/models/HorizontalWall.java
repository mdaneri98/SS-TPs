package models;

import java.util.Set;

public class HorizontalWall extends Wall {

    public HorizontalWall(double l) {
        super(l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelY() == 0) {
            return Double.POSITIVE_INFINITY; // Nunca colisionará si la velocidad en X es 0
        } else if (particle.getVelY() > 0) {
            // Colisión con la pared derecha
            return (this.getL() - particle.getRadius() - particle.getPosY()) / particle.getVelY();
        }
        // Colisión con la pared izquierda
        return (particle.getRadius() - particle.getPosY()) / particle.getVelY();
    }


    public void incrementMomentum(Particle particle) {
        double newMomentum = this.momentum.get(index) + 2 * particle.getMass() *  Math.abs(particle.getVelX());
        this.momentum.set(index, newMomentum);
    }

    @Override
    public Particle applyCollision(final Particle p) {
        this.incrementMomentum(p);
        return new Particle(p.getId(), p.getPosX(), p.getPosY(), -p.getVelX(), p.getVelY(), p.getRadius(), p.getMass());
    }


}
