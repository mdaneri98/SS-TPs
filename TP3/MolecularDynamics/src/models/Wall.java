package models;

import java.util.ArrayList;
import java.util.List;

public abstract class Wall implements Obstacle {

    protected int index;

    private double L;

    public Wall(double l) {
        L = l;
    }

    public abstract double getMomentum(Particle particle);

    public double getL() {
        return L;
    }
}
