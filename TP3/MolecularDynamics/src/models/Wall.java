package models;

import java.util.ArrayList;
import java.util.List;

public abstract class Wall implements Obstacle, Pressurable {

    protected int index;
    protected List<Double> momentum;

    private double L;

    public Wall(double l) {
        L = l;
        momentum = new ArrayList<>();
        index = 0;
        momentum.add(0.0);
    }

    public void newInterval() {
        this.index += 1;
        this.momentum.add(0.0);
    }

    public List<Double> getMomentum() {
        return momentum;
    }

    public double getL() {
        return L;
    }
}
