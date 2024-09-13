package models;

import java.util.*;

public class State {


    private double time;
    private int L;


    private Map<WallType, Wall> walls;
    private Set<Particle> particleSet;

    // <Tiempo de choque, Particulas>
    private PriorityQueue<Collision> collisionQueue;

    public State(double time, Map<WallType, Wall> walls, Set<Particle> particleSet) {
        this.time = time;
        this.walls = walls;
        this.particleSet = particleSet;

        collisionQueue = new PriorityQueue<>();

        updateCollisionsTimes();
    }

    public Set<Particle> getParticles() {
        return particleSet;
    }


    private void updateCollisionsTimes() {
        for (Particle current : particleSet) {
            Pair<Wall, Double> timeUntilCollisionWithWall = timeUntilCollisionWithWall(current);
            //Particula a la que colisiona.
            for (Particle other : particleSet) {
                if (current.equals(other))
                    continue;
                double tc = current.timeToCollide(other);
                if (tc > 0) {
                    if (timeUntilCollisionWithWall.getRight() < tc) {
                        collisionQueue.add(new Collision(timeUntilCollisionWithWall.getRight(), current, timeUntilCollisionWithWall.getLeft()));
                    } else {
                        collisionQueue.add(new Collision(tc, current, other));
                    }
                }
            }
        }
    }

    private Pair<Wall, Double> timeUntilCollisionWithWall(Particle p) {
        Wall bottomWall = this.walls.get(WallType.BOTTOM);
        Wall rightWall = this.walls.get(WallType.RIGHT);
        Wall topWall = this.walls.get(WallType.TOP);
        Wall leftWall = this.walls.get(WallType.LEFT);

        double timeToBottomWall = bottomWall.timeToCollide(p);
        double timeToRightWall = rightWall.timeToCollide(p);
        double timeToTopWall = topWall.timeToCollide(p);
        double timeToLeftWall = leftWall.timeToCollide(p);

        // Comparar los tiempos de colisión y devolver el menor
        Map<Wall, Double> timeToWallMap = new HashMap<>();
        timeToWallMap.put(bottomWall, timeToBottomWall);
        timeToWallMap.put(rightWall, timeToRightWall);
        timeToWallMap.put(topWall, timeToTopWall);
        timeToWallMap.put(leftWall, timeToLeftWall);

        // Encontrar el mínimo tiempo
        Wall collidingWall = timeToWallMap.entrySet()
                .stream()
                .min(Comparator.comparing(Map.Entry::getValue))
                .get()
                .getKey();

        double minTime = timeToWallMap.get(collidingWall);

        return new Pair<>(collidingWall, minTime);
    }

    public PriorityQueue<Collision> getCollisionList() {
        return collisionQueue;
    }

    public Set<Particle> getParticleSet() {
        return particleSet;
    }

    public double getTime() {
        return time;
    }
}
