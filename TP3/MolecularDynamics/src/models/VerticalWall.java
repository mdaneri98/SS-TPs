package models;

public class VerticalWall extends Wall {


    public VerticalWall(int l) {
        super(l);
    }

    @Override
    public double timeToCollide(Particle particle) {
        if (particle.getVelocityY() == 0) {
            return Double.POSITIVE_INFINITY;
        } else if (particle.getVelocityY() > 0) {
            return (this.getL() - particle.getRadius() - particle.getPosY()) / particle.getVelocityY();
        }
        return (0 + particle.getRadius() - particle.getPosY()) / particle.getVelocityY();
    }

    @Override
    public void update(Particle p) {
        if (p.getPosY() == 0 || p.getPosY() == this.getL()) {
            p.setAngle(-p.getAngle());
        }
    }

}
