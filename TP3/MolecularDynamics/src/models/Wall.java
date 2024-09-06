package models;

public abstract class Wall implements Obstacle {

    private double L;

    public Wall(double l) {
        L = l;
    }

    public double getL() {
        return L;
    }
}
