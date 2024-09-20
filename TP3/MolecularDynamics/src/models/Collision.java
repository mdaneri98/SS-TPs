package models;

import java.util.Comparator;
import java.util.Objects;

public class Collision implements Comparable<Collision> {

    private double tc;
    private Particle particle;
    private Obstacle obstacle;

    public Collision(double tc, Particle particle, Obstacle obstacle) {
        this.tc = tc;
        this.particle = particle;
        this.obstacle = obstacle;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true; // Son el mismo objeto
        if (obj == null || getClass() != obj.getClass()) return false; // Verifica la clase

        Collision that = (Collision) obj; // Casteo seguro

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
        return String.format("En:%f",tc);
    }

    @Override
    public int compareTo(Collision o) {
        return Double.compare(this.getTc(), o.getTc());
    }
}
