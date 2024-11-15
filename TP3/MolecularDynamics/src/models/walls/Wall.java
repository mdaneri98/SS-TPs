package models.walls;

import java.util.ArrayList;
import java.util.List;

import models.Obstacle;
import models.particles.Particle;

public abstract class Wall implements Obstacle {

    private final WallType type;
    private final double L;
    
    private final List<Integer> collisionCount;
    private final List<Double> momentumCount;

    public Wall(WallType type, double l) {
        this.type = type;
        L = l;
        
        collisionCount = new ArrayList<>();
        collisionCount.add(0);
        
        momentumCount = new ArrayList<>();
        momentumCount.add(0d);
    }

    public WallType getType() {
        return type;
    }

    public abstract double getMomentum(Particle particle);

    public double getL() {
        return L;
    }
    
    public List<Integer> collisionCount() {
    	return collisionCount;
    }
    
    public List<Double> momentumCount() {
    	return momentumCount;
    }
    
}
