package models;

import java.util.ArrayList;
import java.util.List;

public abstract class Wall implements Obstacle {

    protected int index;
    protected List<Double> collisions;

    private double L;

    public Wall(double l) {
        L = l;
        collisions = new ArrayList<>();
        index = 0;
        collisions.add(0.0);
    }

    public void newInterval() {
        this.index += 1;
        this.collisions.add(0.0);
    }

    public List<Double> getCollisions() {
        return collisions;
    }

    public double getL() {
        return L;
    }
}
