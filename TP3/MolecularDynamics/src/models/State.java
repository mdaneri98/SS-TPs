package models;

import models.particles.Particle;
import models.particles.StaticParticle;
import models.walls.Wall;
import models.walls.WallType;

import java.util.*;

public class State {


    private double time;
    private int L;

    private Map<WallType, Wall> walls;
    private Set<Particle> particleSet;

    private StaticParticle staticParticle;
    
    // <Tiempo de choque, Particulas>
    private Set<FutureCollision> collisionSet;

    public State(double time, Map<WallType, Wall> walls, Set<Particle> particleSet, StaticParticle staticParticle) {
        this.time = time;
        this.walls = walls;
        this.particleSet = particleSet;
        this.staticParticle = staticParticle;

        collisionSet = new TreeSet<>();

        updateCollisionsTimes();
    }

    private void updateCollisionsTimesWith(Set<Particle> particles) {

    }

    private void updateCollisionsTimes() {
        collisionSet.clear(); // Limpiamos la lista antes de actualizarla
        for (Particle current : particleSet) {
            Pair<Double, Wall> wallCollision = timeUntilCollisionWithWall(current);
            double timeUntilWallCollision = wallCollision.getLeft();
            Wall collisionWall = wallCollision.getRight();

            Pair<Double, Particle> particleCollision = findNextParticleCollision(current);

            if (particleCollision == null || (timeUntilWallCollision > 0 && timeUntilWallCollision < particleCollision.getLeft())) {
                // La colisión con la pared ocurre primero (o no hay colisión con partícula)
                collisionSet.add(new FutureCollision(timeUntilWallCollision, current, collisionWall));
            } else {
                // La colisión con otra partícula ocurre primero
                collisionSet.add(new FutureCollision(particleCollision.getLeft(), current, particleCollision.getRight()));
            }
        }
    }

    private Pair<Double, Particle> findNextParticleCollision(Particle current) {
        Pair<Double, Particle> nextCollision = null;
        
        for (Particle other : particleSet) {
            if (current.equals(other))
                continue;

            // Si current == static => tc < 0
            double tc = current.timeToCollide(other);

            if (tc > 0 && tc < Double.POSITIVE_INFINITY) {
                if (nextCollision == null || tc < nextCollision.getLeft()) {
                    nextCollision = new Pair<>(tc, other);
                }
            }
        }
        
        return nextCollision;
    }

    private Pair<Double, Wall> timeUntilCollisionWithWall(Particle p) {
        double t1 = walls.get(WallType.BOTTOM).timeToCollide(p);
        double t2 = walls.get(WallType.RIGHT).timeToCollide(p);
        double t3 = walls.get(WallType.TOP).timeToCollide(p);
        double t4 = walls.get(WallType.LEFT).timeToCollide(p);

        // Mapear tiempos de colisión a las paredes correspondientes
        Map<Wall, Double> timeToWallMap = new HashMap<>();
        timeToWallMap.put(walls.get(WallType.BOTTOM), t1);
        timeToWallMap.put(walls.get(WallType.RIGHT), t2);
        timeToWallMap.put(walls.get(WallType.TOP), t3);
        timeToWallMap.put(walls.get(WallType.LEFT), t4);

        // Encontrar la pared con el menor tiempo de colisión
        Map.Entry<Wall, Double> minEntry = timeToWallMap.entrySet()
                .stream()
                .min(Comparator.comparing(Map.Entry::getValue))
                .get();  // Puedes manejar la excepción en caso de que el mapa esté vacío

        Wall collidingWall = minEntry.getKey();
        double minTime = minEntry.getValue();

        return new Pair<>(minTime, collidingWall);  // Devolver <minTime, collidingWall>
    }

    public Set<FutureCollision> getCollisionSet() {
        return collisionSet;
    }

    public Set<Particle> getParticles() {
        return particleSet;
    }

    public Map<WallType, Wall> getWalls() {
        return walls;
    }

    public double getTime() {
        return time;
    }
    
    public StaticParticle getStaticParticle() {
    	return staticParticle;
    }
    
}
