package models;

import com.sun.source.tree.Tree;

import java.util.*;

public class State {


    private double time;
    private int L;


    private Map<WallType, Wall> walls;
    private Set<Particle> particleSet;

    // <Tiempo de choque, Particulas>
    private TreeSet<Collision> collisionQueue;

    public State(double time, Map<WallType, Wall> walls, Set<Particle> particleSet) {
        this.time = time;
        this.walls = walls;
        this.particleSet = particleSet;

        collisionQueue = new TreeSet<>();

        updateCollisionsTimes();
    }

    public Set<Particle> getParticles() {
        return particleSet;
    }


    public void updateCollisionsTimes() {
        Set<Obstacle> visited = new HashSet<>();
        for (Particle current : particleSet) {
            if (visited.contains(current) || current.getId() == 0)
                continue;

            Pair<Wall, Double> timeUntilCollisionWithWall = timeUntilCollisionWithWall(current);
            List<Double> timeUntilCollisionWithParticle = new ArrayList<>();
            for (Particle other : particleSet) {
                if (current.equals(other) || visited.contains(other))
                    continue;

                double tc = current.timeToCollide(other);
                if (tc > 0 && tc < Double.POSITIVE_INFINITY)
                    timeUntilCollisionWithParticle.add(tc);
            }

            if (timeUntilCollisionWithParticle.isEmpty()){
                collisionQueue.add(new Collision(timeUntilCollisionWithWall.getRight(),current, timeUntilCollisionWithWall.getLeft()));
                visited.add(current);
                continue;
            }
            double min = Collections.min(timeUntilCollisionWithParticle);
            if (min < timeUntilCollisionWithWall.getRight()) {
                //collisionQueue.add(new Collision(min,current, particleSet.stream().filter(p -> current.timeToCollide(p) == min).findFirst().get()));
                Particle collideWith = null;
                for (Particle p : particleSet) {
                    if (current.timeToCollide(p) == min) {
                        collideWith = p;
                    }
                }
                collisionQueue.add(new Collision(min, current, collideWith));
            } else if (timeUntilCollisionWithWall.getRight() > 0) {
                collisionQueue.add(new Collision(timeUntilCollisionWithWall.getRight(),current, timeUntilCollisionWithWall.getLeft()));
            }
            visited.add(current);
        }
    }

    /*
        p1 ---> |


     */

    private Pair<Wall, Double> timeUntilCollisionWithWall(Particle p) {
        Wall horizontalWall = this.walls.get(WallType.HORIZONTAL);
        Wall verticalWall = this.walls.get(WallType.VERTICAL);

        double timeToHorizontalWall = horizontalWall.timeToCollide(p);
        double timeToVerticalWall = verticalWall.timeToCollide(p);

        // Comparar los tiempos de colisión y devolver el menor
        Map<Wall, Double> timeToWallMap = new HashMap<>();
        timeToWallMap.put(horizontalWall, timeToHorizontalWall);
        timeToWallMap.put(verticalWall, timeToVerticalWall);

        // Encontrar el mínimo tiempo
        Wall collidingWall = timeToWallMap.entrySet()
                .stream()
                .min(Comparator.comparing(Map.Entry::getValue))
                .get()
                .getKey();

        double minTime = timeToWallMap.get(collidingWall);

        return new Pair<>(collidingWall, minTime);
    }

    public TreeSet<Collision> getCollisionList() {
        return collisionQueue;
    }

    public Set<Particle> getParticleSet() {
        return particleSet;
    }

    public double getTime() {
        return time;
    }
}
