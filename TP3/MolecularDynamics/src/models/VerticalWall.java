package models;

public class VerticalWall extends Wall {


    public VerticalWall(int l) {
        super(l);
    }

    @Override
    public void update(Particle p) {
        if (p.getPosY() == 0 || p.getPosY() == this.getL()) {
            p.setAngle(-p.getAngle());
        }
    }

}
