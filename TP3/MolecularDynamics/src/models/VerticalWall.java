package models;

public class VerticalWall extends Wall {


    public VerticalWall(double l) {
        super(l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocityX() == 0) {
            return Double.POSITIVE_INFINITY; // Nunca colisionará si la velocidad en X es 0
        } else if (particle.getVelocityX() > 0) {
            // Colisión con la pared derecha
            return (this.getL() - particle.getRadius() - particle.getPosX()) / particle.getVelocityX();
        }
        // Colisión con la pared izquierda
        return (particle.getRadius() - particle.getPosX()) / particle.getVelocityX();
    }

    public void incrementMomentum(Particle particle) {
        double newMomentum = this.momentum.get(index) + 2 * particle.getMass() * Math.abs(particle.getVelocityY());
        this.momentum.set(index, newMomentum);
    }

    @Override
    public Particle applyCollision(Particle p) {
        this.incrementMomentum(p);
        return new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelocity(), Math.PI - p.getAngle(), p.getRadius(), p.getMass());
    }



}
