package models;

import java.util.Objects;
import java.util.Vector;

public class Particle {

    private int id;
    private Position position;
    private Velocity velocity;
    private double maxVelocity;
    private double minRadius;
    private double maxRadius;
    private double actualRadius;
    
    //private final Position target;

    public Particle(int id, Position position, Velocity velocity, double maxVelocity, double minRadius, double maxRadius, double actualRadius) {
    	this.id = id;
        this.position = position;
        this.velocity = velocity;
        this.maxVelocity = maxVelocity;
        this.minRadius = minRadius;
        this.maxRadius = maxRadius;
        this.actualRadius = actualRadius;
    }

    public boolean isInside(Particle other) {
        // Calcular la distancia entre los centros de las partículas
        double distance = Math.sqrt(Math.pow(other.getPosition().getX() - this.getPosition().getX(), 2) + Math.pow(other.getPosition().getY() - this.getPosition().getY(), 2));

        // Verificar si la partícula actual está completamente dentro de la otra
        return distance < this.actualRadius + other.actualRadius;
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
                ", position=" + position +
                ", velocity=" + velocity +
                ", actualRadius=" + actualRadius +
                '}';
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    public Velocity desired() {
    	if (actualRadius == minRadius)
    		return new Velocity(new double[] {0, 0}, 0);
    	return new Velocity(velocity.getDirection(), this.maxVelocity);
    }

    // Getters and Setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

	public Position getPosition() {
		return position;
	}

	public void setPosition(Position position) {
		this.position = position;
	}

	public Velocity getVelocity() {
		return velocity;
	}

	public void setVelocity(Velocity velocity) {
		this.velocity = velocity;
	}

	public double getMinRadius() {
		return minRadius;
	}

	public void setMinRadius(double minRadius) {
		this.minRadius = minRadius;
	}

	public double getMaxRadius() {
		return maxRadius;
	}

	public void setMaxRadius(double maxRadius) {
		this.maxRadius = maxRadius;
	}

	public double getActualRadius() {
		return actualRadius;
	}

	public void setActualRadius(double actualRadius) {
		this.actualRadius = actualRadius;
	}

}
