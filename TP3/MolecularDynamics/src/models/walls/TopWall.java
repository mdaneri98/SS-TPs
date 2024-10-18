package models.walls;

import models.particles.Particle;
import models.particles.StaticParticle;
import models.particles.Velocity;

public class TopWall extends Wall {

    public TopWall(WallType type, double l) {
        super(type, l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocity().getY() <= 0) {
            return Double.POSITIVE_INFINITY; // Nunca colisionará si la velocidad en X es 0
        } else if (particle.getVelocity().getY() > 0) {
            // Colisión con la pared derecha
            return (this.getL() - particle.getRadius() - particle.getPosition().getY()) / particle.getVelocity().getY();
        }
        // Colisión con la pared izquierda
        return (particle.getRadius() - particle.getPosition().getX()) / particle.getVelocity().getY();
    }


    public double getMomentum(Particle particle) {
        return 2 * particle.getMass() *  Math.abs(particle.getVelocity().getY());
    }

    @Override
    public String toString() {
        return "TopWall";
    }


}
