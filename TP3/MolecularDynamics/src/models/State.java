package models;

import java.util.*;

public class State {


    private int L;


    private List<Wall> walls;
    private Set<Particle> particleSet;

    // <Tiempo de choque, Particulas>
    private TreeMap<Double, Pair<Particle, Obstacle>> collidesByTime;

    public State(List<Wall> walls, Set<Particle> particleSet) {
        this.walls = walls;
        this.particleSet = particleSet;

        collidesByTime = new TreeMap<>();

        updateCollisionsTimes();
    }

    public Set<Particle> getParticles() {
        return particleSet;
    }


    private void updateCollisionsTimes() {
        for (Particle current : particleSet) {
            Pair<Wall, Double> timeUntilCollisionWithWall = timeUntilCollisionWithWall(current);
            for (Particle other : particleSet) {
                double tc = current.timeToCollide(other);
                if (tc > 0) {
                    if (timeUntilCollisionWithWall.getRight() < tc) {
                        collidesByTime.put(timeUntilCollisionWithWall.getRight(), new Pair<>(current, timeUntilCollisionWithWall.getLeft()));
                    } else {
                        collidesByTime.put(tc, new Pair<>(current, other));
                    }
                }
            }
        }
    }

    private Pair<Wall, Double> timeUntilCollisionWithWall(Particle p) {
        // Asumimos que walls.get(0) es una pared horizontal y walls.get(1) es una pared vertical
        Wall horizontalWall = this.walls.get(0);
        Wall verticalWall = this.walls.get(1);

        double timeToVerticalWall = verticalWall.timeToCollide(p);
        double timeToHorizontalWall = horizontalWall.timeToCollide(p);

        // Comparar los tiempos de colisión y devolver el menor
        double minTime = Math.min(timeToVerticalWall, timeToHorizontalWall);

        // Determinar la pared con la que colisionará primero
        Wall collidingWall = (minTime == timeToVerticalWall) ? verticalWall : horizontalWall;

        return new Pair<>(collidingWall, minTime);
    }

    public TreeMap<Double, Pair<Particle, Obstacle>> getCollidesByTime() {
        return collidesByTime;
    }

    public Set<Particle> getParticleSet() {
        return particleSet;
    }
}
