package models.walls;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import models.Obstacle;
import models.particles.Particle;

public abstract class Wall implements Obstacle {
    private final WallType type;
    private final double L;

    private final TreeMap<Double, Integer> collisionCount;
    private final TreeMap<Double, Double> momentumCount;

    public Wall(WallType type, double l) {
        this.type = type;
        L = l;

        collisionCount = new TreeMap<>();
        collisionCount.put(0.0, 0);

        momentumCount = new TreeMap<>();
        momentumCount.put(0.0, 0.0);
    }

    public WallType getType() {
        return type;
    }

    public abstract double getMomentum(Particle particle);

    public double getL() {
        return L;
    }

    public TreeMap<Double, Integer> collisionCount() {
        return collisionCount;
    }

    public TreeMap<Double, Double> momentumCount() {
        return momentumCount;
    }
}