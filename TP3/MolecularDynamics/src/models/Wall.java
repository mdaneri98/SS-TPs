package models;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public abstract class Wall implements Obstacle {

    private double L;

    public Wall(double l) {
        L = l;
    }

    public abstract double getMomentum(Particle particle);

    public double getL() {
        return L;
    }
}
