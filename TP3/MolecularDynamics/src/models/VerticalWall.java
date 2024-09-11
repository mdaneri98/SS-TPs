package models;

public class VerticalWall extends Wall {


    public VerticalWall(double l) {
        super(l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocityY() == 0) {
            return Double.POSITIVE_INFINITY;
        } else if (particle.getVelocityY() > 0) {
            return (this.getL() - particle.getRadius() - particle.getPosY()) / particle.getVelocityY();
        }
        return (0 - particle.getPosY() - particle.getRadius()) / particle.getVelocityY();
    }

    public void incrementMomentum(Particle particle) {
        double newMomentum = this.momentum.get(index) + 2 * particle.getMass() * Math.abs(particle.getVelocityY());
        this.momentum.set(index, newMomentum);
    }

    @Override
    public Particle applyCollision(Particle p) {
        this.incrementMomentum(p);
        return new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelocity(), - p.getAngle(), p.getRadius(), p.getMass());
    }



}
