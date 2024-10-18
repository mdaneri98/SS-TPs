package models.particles;

import models.Obstacle;
import models.Pair;

import java.util.Objects;

public class Particle implements Obstacle {

    private int id;
    private Velocity velocity;
    private Position position;
    private double radius;
    private double mass;

    public Particle(int id, Position position, Velocity velocity, double radius, double mass) {
        this.id = id;
        this.velocity = velocity;
        this.position = position;
        this.radius = radius;
        this.mass = mass;
    }

    public boolean collide(Particle other) {
        // Calcular la distancia entre los centros de las partículas
        double distance = Math.sqrt(Math.pow(other.getPosition().getX() - this.getPosition().getX(), 2) + Math.pow(other.getPosition().getY() - this.getPosition().getY(), 2));

        return distance <= this.radius + other.radius;
    }

    public boolean isInside(Particle other) {
        // Calcular la distancia entre los centros de las partículas
        double distance = Math.sqrt(Math.pow(other.getPosition().getX() - this.getPosition().getX(), 2) + Math.pow(other.getPosition().getY() - this.getPosition().getY(), 2));

        // Verificar si la partícula actual está completamente dentro de la otra
        return distance < this.radius + other.radius;
    }

    public void move(double tc) {
        double newX = this.getPosition().getX() + this.getVelocity().getX() * tc;
        double newY = this.getPosition().getY() + this.getVelocity().getY() * tc;
        this.setPosition(new Position(newX, newY));
    }

    @Override
    public double timeToCollide(Particle particle) {
        /* Tiempo en colisionar la particula 'particle' con esta instancia. */

        // Calculamos las diferencias de posición (deltaR) y velocidad (deltaV)
        Pair<Double, Double> deltaR = new Pair<>(this.getPosition().getX() - particle.getPosition().getX(), this.getPosition().getY() - particle.getPosition().getY());
        Pair<Double, Double> deltaV = new Pair<>(this.getVelocity().getX() - particle.getVelocity().getX(), this.getVelocity().getY() - particle.getVelocity().getY());

        // Magnitudes al cuadrado
        double deltaR2 = Math.pow(deltaR.getLeft(), 2) + Math.pow(deltaR.getRight(), 2); // deltaR^2
        double deltaV2 = Math.pow(deltaV.getLeft(), 2) + Math.pow(deltaV.getRight(), 2); // deltaV^2
        double deltaVDeltaR = deltaV.getLeft() * deltaR.getLeft() + deltaV.getRight() * deltaR.getRight(); // deltaV * deltaR

        // La suma de los radios de ambas partículas
        double phi = particle.getRadius() + this.getRadius();

        // Calculamos el discriminante
        double d = Math.pow(deltaVDeltaR, 2) - deltaV2 * (deltaR2 - (phi * phi));

        // Si el discriminante es negativo, no hay colisión
        if (d < 0) {
            return Double.POSITIVE_INFINITY;
        }

        // Si deltaVDeltaR es negativo, significa que las partículas están acercándose
        if (deltaVDeltaR < 0) {
            // Calculamos el tiempo de colisión
            double time = -(deltaVDeltaR + Math.sqrt(d)) / deltaV2;

            // Si el tiempo es positivo, devolvemos ese valor, de lo contrario no colisionarán en el futuro
            if (time > 0) {
                return time;
            }
        }

        // Si las partículas no colisionan en el futuro, devolvemos infinito
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
    public String toString() {
        return "Particle{" +
                "id=" + id +
                ", x=" + position.getX() +
                ", y=" + position.getY() +
                ", vx=" + velocity.getX() +
                ", vy=" + velocity.getY() +
                ", radius=" + radius +
                ", mass=" + mass +
                '}';
    }

    @Override
    public Particle clone() {
        Velocity newVelocity = new Velocity(this.getVelocity().getX(), this.getVelocity().getY());
        Position newPosition = new Position(this.getPosition().getX(), this.getPosition().getY());
        return new Particle(getId(), position, velocity, getRadius(), getMass());
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    // Getters and Setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public Velocity getVelocity() {
        return velocity;
    }

    public void setVelocity(Velocity velocity) {
        this.velocity = velocity;
    }

    public Position getPosition() {
        return position;
    }

    public void setPosition(Position position) {
        this.position = position;
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
