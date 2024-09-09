package models;

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

    @Override
    public Particle applyCollision(final Particle p) {
        /*
        if (p.getPosY() - p.getRadius() <= 0 || p.getPosY() + p.getRadius() >= this.getL()){
             return new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelocity(), Math.PI - p.getAngle(), p.getRadius(), p.getMass());
        }
         */
        return new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelocity(), Math.PI - p.getAngle(), p.getRadius(), p.getMass());
    }

}
