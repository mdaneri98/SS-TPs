package damped_harmonic_oscillator.models;

import java.util.Objects;

public class Particle implements Cloneable {

    private int id;
    private double position;
    private double velocity;
    private double mass;

    public Particle(int id, double position, double velocity, double mass) {
        this.id = id;
        this.position = position;
        this.velocity = velocity;
        this.mass = mass;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Particle particle = (Particle) o;
        return id == particle.id;
    }

    @Override
    public Particle clone() {
        try {
            // Llamamos a super.clone() para hacer una copia superficial (shallow copy)
            Particle clone = (Particle) super.clone();
            return clone;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError("Cloning not supported");
        }
    }

    @Override
    public String toString() {
        return "damped_harmonic_oscillator.models.Particle{" +
                "id=" + id +
                ", position=" + position +
                ", velocity=" + velocity +
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

    public double getMass() {
        return mass;
    }

    public void setMass(double mass) {
        this.mass = mass;
    }

    public double getPosition() {
        return position;
    }

    public void setPosition(double position) {
        this.position = position;
    }

    public double getVelocity() {
        return velocity;
    }

    public void setVelocity(double velocity) {
        this.velocity = velocity;
    }

}
