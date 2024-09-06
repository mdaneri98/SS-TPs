package models;

public abstract class Wall implements Obstacle {

    private int L;

    public Wall(int l) {
        L = l;
    }

    public int getL() {
        return L;
    }
}
