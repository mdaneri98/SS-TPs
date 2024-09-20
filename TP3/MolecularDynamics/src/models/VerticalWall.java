package models;

public class VerticalWall extends Wall {


    public VerticalWall(double l) {
        super(l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelX() == 0) {
            return Double.POSITIVE_INFINITY; // Nunca colisionará si la velocidad en X es 0
        } else if (particle.getVelX() > 0) {
            // Colisión con la pared derecha
            return (this.getL() - particle.getRadius() - particle.getPosX()) / particle.getVelX();
        }
        // Colisión con la pared izquierda
        return (particle.getRadius() - particle.getPosX()) / particle.getVelX();
    }

    public double getMomentum(Particle particle) {
        return 2 * particle.getMass() * Math.abs(particle.getVelX());
    }

    @Override
    public Particle applyCollision(Particle p) {
        return new Particle(p.getId(), p.getPosX(), p.getPosY(),- p.getVelX(), p.getVelY(), p.getRadius(), p.getMass());
    }

    @Override
    public String toString() {
        return "VerticalWall";
    }

}
