package models;

import com.sun.source.tree.Tree;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.*;

public class State {


    private double time;
    private int L;


    private Map<WallType, Wall> walls;
    private Set<Particle> particleSet;

    // <Tiempo de choque, Particulas>
    private List<Collision> collisionList;

    public State(double time, Map<WallType, Wall> walls, Set<Particle> particleSet) {
        this.time = time;
        this.walls = walls;
        this.particleSet = particleSet;

        collisionList = new LinkedList<>();

        updateCollisionsTimes();
    }

    public State(double time, Map<WallType, Wall> walls, Set<Particle> particleSet, List<Collision> collisionList, Set<Particle> collidedParticles) {
        this.time = time;
        this.walls = walls;
        this.particleSet = particleSet;

        this.collisionList = collisionList;

        updateCollisionsTimesWith(collidedParticles);
    }

    public Set<Particle> getParticles() {
        return particleSet;
    }


    private void updateCollisionsTimesWith(Set<Particle> particles) {
        Iterator<Collision> collisionIterator = collisionList.iterator();
        while (collisionIterator.hasNext()) {
            Collision collision = collisionIterator.next();
            for (Particle p : particles) {
                if (collision.getParticle().equals(p)) {
                    // Eliminar la colisión de forma segura
                    collisionIterator.remove();
                    break; // Salir del bucle si se eliminó la colisión
                }
            }
        }

        for (Particle current : particles) {
            Pair<Wall, Double> timeUntilCollisionWithWall = timeUntilCollisionWithWall(current);
            List<Double> timeUntilCollisionWithParticle = new ArrayList<>();
            for (Particle other : particleSet) {
                if (current.equals(other))
                    continue;

                double tc = current.timeToCollide(other);
                if (tc > 0 && tc < Double.POSITIVE_INFINITY)
                    timeUntilCollisionWithParticle.add(tc);
            }

            if (timeUntilCollisionWithParticle.isEmpty()){
                collisionList.add(new Collision(timeUntilCollisionWithWall.getRight(),current, timeUntilCollisionWithWall.getLeft()));
                continue;
            }
            double min = Collections.min(timeUntilCollisionWithParticle);
            if (min < timeUntilCollisionWithWall.getRight()) {
                //collisionList.add(new Collision(min,current, particleSet.stream().filter(p -> current.timeToCollide(p) == min).findFirst().get()));
                Particle collideWith = null;
                for (Particle p : particleSet) {
                    if (current.timeToCollide(p) == min) {
                        collideWith = p;
                    }
                }
                collisionList.add(new Collision(min, current, collideWith));
            } else if (timeUntilCollisionWithWall.getRight() > 0) {
                collisionList.add(new Collision(timeUntilCollisionWithWall.getRight(),current, timeUntilCollisionWithWall.getLeft()));
            }
        }
    }

    private void updateCollisionsTimes() {
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
                collisionList.add(new Collision(timeUntilCollisionWithWall.getRight(),current, timeUntilCollisionWithWall.getLeft()));
                visited.add(current);
                continue;
            }
            double min = Collections.min(timeUntilCollisionWithParticle);
            if (min < timeUntilCollisionWithWall.getRight()) {
                //collisionList.add(new Collision(min,current, particleSet.stream().filter(p -> current.timeToCollide(p) == min).findFirst().get()));
                Particle collideWith = null;
                for (Particle p : particleSet) {
                    if (current.timeToCollide(p) == min) {
                        collideWith = p;
                    }
                }
                collisionList.add(new Collision(min, current, collideWith));
            } else if (timeUntilCollisionWithWall.getRight() > 0) {
                collisionList.add(new Collision(timeUntilCollisionWithWall.getRight(),current, timeUntilCollisionWithWall.getLeft()));
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

    public List<Collision> getCollisionList() {
        return collisionList;
    }

    public Set<Particle> getParticleSet() {
        return particleSet;
    }

    public double getTime() {
        return time;
    }
}
