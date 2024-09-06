package models;

public class HorizontalWall extends Wall {

    public HorizontalWall(int l) {
        super(l);
    }

    @Override
    public void update(Particle p) {
        if (p.getPosX() == 0 || p.getPosX() == this.getL()){
            p.setAngle(Math.PI - p.getAngle());
        }
    }

}
