package models;

import java.util.Objects;

public class Particle implements Obstacle {

    private int id;
    private double posX;
    private double posY;
    private double velX;
    private double velY;
    private double radius;
    private double mass;

    public Particle(int id, double posX, double posY, double velX, double velY, double radius, double mass) {
        this.id = id;
        this.posX = posX;
        this.posY = posY;
        this.velX = velX;
        this.velY = velY;
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
        return distance < this.radius + other.radius;
    }

    public void move(double tc) {
        double newX = this.getPosX() + this.getVelX() * tc;
        double newY = this.getPosY() + this.getVelY() * tc;
        this.setPosX(newX);
        this.setPosY(newY);
    }

    @Override
    public Particle applyCollision(final Particle p) {
        // Calcular deltaR (diferencia de posiciones) y deltaV (diferencia de velocidades)
        double deltaRx = p.getPosX() - this.getPosX();
        double deltaRy = p.getPosY() - this.getPosY();
        double deltaVx = p.getVelX() - this.getVelX();
        double deltaVy = p.getVelY() - this.getVelY();

        // Calcular el valor de sigma (distancia entre centros)
        double sigma = this.getRadius() + p.getRadius();

        // Calcular deltaV · deltaR
        double deltaVDeltaR = deltaVx * deltaRx + deltaVy * deltaRy;

        // Calcular el valor de J (el impulso en la colisión)
        double J = (2 * this.getMass() * p.getMass() * deltaVDeltaR) / (sigma * (this.getMass() + p.getMass()));

        // Calcular Jx y Jy
        double Jx = (J * deltaRx) / sigma;
        double Jy = (J * deltaRy) / sigma;

        // Actualizar las velocidades de la partícula (p)
        double newVxP = p.getVelX() - Jx / p.getMass();
        double newVyP = p.getVelY() - Jy / p.getMass();

        Particle newParticle = new Particle(p.getId(), p.getPosX(), p.getPosY(), newVxP, newVyP, p.getRadius(), p.getMass());

        return newParticle;
    }

    @Override
    public double timeToCollide(Particle particle) {
        /* Tiempo en colisionar la particula 'particle' con esta instancia. */

        // Calculamos las diferencias de posición (deltaR) y velocidad (deltaV)
        Pair<Double, Double> deltaR = new Pair<>(this.getPosX() - particle.getPosX(), this.getPosY() - particle.getPosY());
        Pair<Double, Double> deltaV = new Pair<>(this.getVelX() - particle.getVelX(), this.getVelY() - particle.getVelY());

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
                ", posX=" + posX +
                ", posY=" + posY +
                ", velX=" + velX +
                ", velY=" + velY +
                ", radius=" + radius +
                ", mass=" + mass +
                '}';
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

    public double getVelX() {
        return velX;
    }

    public void setVelX(double velX) {
        this.velX = velX;
    }

    public double getVelY() {
        return velY;
    }

    public void setVelY(double velY) {
        this.velY = velY;
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
