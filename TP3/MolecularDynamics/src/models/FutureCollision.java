package models;

import models.particles.Particle;

import java.util.Objects;

public class FutureCollision implements Comparable<FutureCollision> {

    private double tc;
    private Particle particle;
    private Obstacle obstacle;

    public FutureCollision(double tc, Particle particle, Obstacle obstacle) {
        this.tc = tc;
        this.particle = particle;
        this.obstacle = obstacle;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true; // Son el mismo objeto
        if (obj == null || getClass() != obj.getClass()) return false; // Verifica la clase

        FutureCollision that = (FutureCollision) obj; // Casteo seguro

        // Comparar los campos
        return Double.compare(tc, that.tc) == 0 &&
                Objects.equals(particle, that.particle) &&
                Objects.equals(obstacle, that.obstacle);
    }

    public double getTc() {
        return tc;
    }

    public Particle getParticle() {
        return particle;
    }

    public Obstacle getObstacle() {
        return obstacle;
    }



    @Override public String toString(){
        return String.format("[%f][%s]->[%s]", tc, particle, obstacle);
    }

    @Override
    public int compareTo(FutureCollision o) {
        return Double.compare(this.getTc(), o.getTc());
    }
}
