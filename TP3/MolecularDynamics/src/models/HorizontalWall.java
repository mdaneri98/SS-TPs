package models;

public class HorizontalWall extends Wall {

    public HorizontalWall(int l) {
        super(l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocityX() == 0) {
            return Double.POSITIVE_INFINITY;
        } else if (particle.getVelocityX() > 0) {
            return (this.getL() - particle.getRadius() - particle.getPosX()) / particle.getVelocityX();
        }
        return (0 + particle.getRadius() - particle.getPosX()) / particle.getVelocityX();
    }

    @Override
    public void update(Particle p) {
        if (p.getPosX() == 0 || p.getPosX() == this.getL()){
            p.setAngle(Math.PI - p.getAngle());
        }
    }

}
