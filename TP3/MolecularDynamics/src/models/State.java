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


    private void updateCollisionsTimes() {
        for (Particle current : particleSet) {
            Pair<Wall, Double> timeUntilCollisionWithWall = timeUntilCollisionWithWall(current);
            for (Particle other : particleSet) {
                Pair<Double, Double> deltaR = new Pair<>(other.getPosX() - current.getPosX(), other.getPosY() - current.getPosY() );
                Pair<Double, Double> deltaV = new Pair<>(other.getVelocityX() - current.getVelocityX(), other.getVelocityY() - current.getVelocityY());
                double deltaR2 = Math.pow(deltaR.getLeft(), 2) + Math.pow(deltaR.getRight(), 2);
                double deltaV2 = Math.pow(deltaV.getLeft(), 2) + Math.pow(deltaV.getRight(), 2);;
                double deltaVDeltaR = deltaV.getLeft() * deltaR.getLeft() + deltaV.getRight() * deltaR.getRight();
                double phi = current.getRadius() + other.getRadius();
                double d = Math.pow(deltaVDeltaR, 2) - deltaV2 * (deltaR2 - phi * phi);

                if (deltaVDeltaR < 0 || d >= 0) {
                    // Collides
                    double tc = - ((deltaVDeltaR + Math.sqrt(d)) / (deltaV2));
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
    }

    private Pair<Wall, Double> timeUntilCollisionWithWall(Particle p) {
        // Asumimos que walls.get(0) es una pared horizontal y walls.get(1) es una pared vertical
        Wall horizontalWall = this.walls.get(0);
        Wall verticalWall = this.walls.get(1);

        double timeToVerticalWall, timeToHorizontalWall;

        // Componente de la velocidad en los ejes X e Y
        double velocityX = p.getVelocityX();
        double velocityY = p.getVelocityY();

        // Tiempo hasta colisión con las paredes verticales (x = 0 o x = L)
        if (velocityX > 0) {
            // Pared derecha (x = L)
            timeToVerticalWall = (verticalWall.getL() - p.getPosX() - p.getRadius()) / velocityX;
        } else if (velocityX < 0) {
            // Pared izquierda (x = 0)
            timeToVerticalWall = (p.getPosX() - p.getRadius()) / -velocityX;
        } else {
            // No se mueve en la dirección X
            timeToVerticalWall = Double.POSITIVE_INFINITY;
        }

        // Tiempo hasta colisión con las paredes horizontales (y = 0 o y = L)
        if (velocityY > 0) {
            // Pared superior (y = L)
            timeToHorizontalWall = (horizontalWall.getL() - p.getPosY() - p.getRadius()) / velocityY;
        } else if (velocityY < 0) {
            // Pared inferior (y = 0)
            timeToHorizontalWall = (p.getPosY() - p.getRadius()) / -velocityY;
        } else {
            // No se mueve en la dirección Y
            timeToHorizontalWall = Double.POSITIVE_INFINITY;
        }

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
