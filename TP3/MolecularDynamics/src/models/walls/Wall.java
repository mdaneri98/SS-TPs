package models.walls;

import models.Obstacle;
import models.particles.Particle;

public abstract class Wall implements Obstacle {

    private final WallType type;
    private final double L;

    public Wall(WallType type, double l) {
        this.type = type;
        L = l;
    }

    public WallType getType() {
        return type;
    }

    public abstract double getMomentum(Particle particle);

    public double getL() {
        return L;
    }
}
