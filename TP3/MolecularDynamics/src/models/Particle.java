package models;

import java.util.Objects;

public class Particle implements Obstacle {

    private int id;
    private double posX;
    private double posY;
    private double velocity;
    private double angle;
    private double radius;
    private double mass;

    public Particle(int id, double posX, double posY, double velocity, double angle, double radius, double mass) {
        this.id = id;
        this.posX = posX;
        this.posY = posY;
        this.velocity = velocity;
        this.angle = angle;
        this.radius = radius;
        this.mass = mass;
    }

    public boolean collide(Particle other) {
        // Calcular la distancia entre los centros de las partículas
        double distance = Math.sqrt(Math.pow(other.posX - this.posX, 2) + Math.pow(other.posY - this.posY, 2));

        return distance <= this.radius + other.radius;
    }

    public boolean isInside(Particle other) {
        // Calcular la distancia entre los centros de las partículas
        double distance = Math.sqrt(Math.pow(other.posX - this.posX, 2) + Math.pow(other.posY - this.posY, 2));

        // Verificar si la partícula actual está completamente dentro de la otra
        return distance + this.radius <= other.radius;
    }

    @Override
    public void update(Particle particle) {
        //FIXME: TODO


    }

    @Override
    public double timeToCollide(Particle particle) {
        /* Tiempo en colisionar la particula 'particle' con esta instancia. */
        Pair<Double, Double> deltaR = new Pair<>(this.getPosX() - particle.getPosX(), this.getPosY() - particle.getPosY() );
        Pair<Double, Double> deltaV = new Pair<>(this.getVelocityX() - particle.getVelocityX(), this.getVelocityY() - particle.getVelocityY());
        double deltaR2 = Math.pow(deltaR.getLeft(), 2) + Math.pow(deltaR.getRight(), 2);
        double deltaV2 = Math.pow(deltaV.getLeft(), 2) + Math.pow(deltaV.getRight(), 2);;
        double deltaVDeltaR = deltaV.getLeft() * deltaR.getLeft() + deltaV.getRight() * deltaR.getRight();
        double phi = particle.getRadius() + this.getRadius();
        double d = Math.pow(deltaVDeltaR, 2) - deltaV2 * (deltaR2 - phi * phi);

        if (deltaVDeltaR < 0 || d >= 0)
            return - ((deltaVDeltaR + Math.sqrt(d)) / (deltaV2));
        return Double.POSITIVE_INFINITY;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Particle particle = (Particle) o;
        return id == particle.id;
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    public double getVelocityX() {
        return this.velocity * Math.cos(this.getAngle());
    }

    public double getVelocityY() {
        return this.velocity * Math.sin(this.getAngle());
    }

    // Getters and Setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public double getPosX() {
        return posX;
    }

    public void setPosX(double posX) {
        this.posX = posX;
    }

    public double getPosY() {
        return posY;
    }

    public void setPosY(double posY) {
        this.posY = posY;
    }

    public double getVelocity() {
        return velocity;
    }

    public void setVelocity(double velocity) {
        this.velocity = velocity;
    }

    public double getAngle() {
        return angle;
    }

    public void setAngle(double angle) {
        this.angle = (angle + 2*Math.PI) % (2 * Math.PI);
    }

    public double getRadius() {
        return radius;
    }

    public void setRadius(double radius) {
        this.radius = radius;
    }

    public double getMass() {
        return mass;
    }

    public void setMass(double mass) {
        this.mass = mass;
    }

}
