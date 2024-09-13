package models;

import java.util.Comparator;

public class Collision implements Comparable<Collision> {

    private double tc;
    private Particle particle;
    private Obstacle obstacle;

    public Collision(double tc, Particle particle, Obstacle obstacle) {
        this.tc = tc;
        this.particle = particle;
        this.obstacle = obstacle;
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
