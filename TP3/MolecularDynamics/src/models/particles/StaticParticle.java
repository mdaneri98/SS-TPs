package models.particles;

import java.util.*;

public class StaticParticle extends Particle {
    private static TreeMap<Double, Integer> collisionCount = new TreeMap<>();
    private static TreeMap<Double, Double> momentumCount = new TreeMap<>();
    private static TreeMap<Double, Integer> uniqueCollisionCount = new TreeMap<>();
    private static Set<Integer> collidedParticles = new HashSet<>();

    public StaticParticle(int id, Position position, Velocity velocity, double radius, double mass) {
        super(id, position, velocity, radius, mass);
    }

    public static void newIteration() {
        collisionCount = new TreeMap<>();
        collisionCount.put(0d, 0);
        momentumCount = new TreeMap<>();
        momentumCount.put(0d, 0d);
        uniqueCollisionCount = new TreeMap<>();
        uniqueCollisionCount.put(0d, 0);
        collidedParticles = new HashSet<>();
    }

    @Override
    public StaticParticle clone() {
        return new StaticParticle(getId(),
                new Position(getPosition().getX(), getPosition().getY()),
                new Velocity(getVelocity().getX(), getVelocity().getY()),
                getRadius(), getMass());
    }

    public TreeMap<Double, Integer> collisionCount() {
        return collisionCount;
    }

    public TreeMap<Double, Integer> uniqueCollisionCount() {
        return uniqueCollisionCount;
    }

    public TreeMap<Double, Double> momentumCount() {
        return momentumCount;
    }

    public Set<Integer> getCollidedParticles() {
        return collidedParticles;
    }
}