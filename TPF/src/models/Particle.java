package models;

import java.util.Objects;

public class Particle {

    private final int id;
    private final Position position;
    private final Velocity velocity;
    private final double maxVelocity;
    private final double minRadius;
    private final double maxRadius;
    private final double actualRadius;
    private final double tau;
    
    private final Target target;

    public Particle(int id, Position position, Target target, Velocity velocity, double maxVelocity, double minRadius, double maxRadius, double actualRadius, double tau) {
    	this.id = id;
        this.position = position;
        this.target = target;
        this.velocity = velocity;
        this.maxVelocity = maxVelocity;
        this.minRadius = minRadius;
        this.maxRadius = maxRadius;
        this.actualRadius = actualRadius;
        this.tau = tau;
    }

    public double distanceTo(Particle other) {
        double dx = this.getPosition().getX() - other.getPosition().getX();
        double dy = this.getPosition().getY() - other.getPosition().getY();
        return Math.sqrt(dx * dx + dy * dy);
    }

    
    public boolean isInside(Particle other) {
        // Calcular la distancia entre los centros de las partículas
        double distance = Math.sqrt(Math.pow(other.getPosition().getX() - this.getPosition().getX(), 2) + Math.pow(other.getPosition().getY() - this.getPosition().getY(), 2));

        // Verificar si la partícula actual está completamente dentro de la otra
        return distance < this.actualRadius + other.actualRadius;
    }
    
    public boolean isInsidePersonalSpace(Particle other) {
        double distance = this.position.distanceTo(other.getPosition());
        return distance < (this.actualRadius + other.getActualRadius());
    }

    public boolean isInsidePersonalSpace(Field field) {
    	// Según original ACM.
    	double x = Math.max(0, Math.min(this.getPosition().getX(), field.getWidth()));
    	double y = Math.max(0, Math.min(this.getPosition().getY(), field.getHeight()));
    	
        double deltaX = this.getPosition().getX() - x;
        double deltaY = this.getPosition().getY() - y;
    	
        return Math.sqrt(Math.pow(deltaX, 2) + Math.pow(deltaY, 2)) < actualRadius; 
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
    
    // Getters and Setters
    public int getId() {
        return id;
    }
    
    public Target getTarget() {
    	return target;
    }
    
    public double getTau() {
    	return tau;
    }

	public Position getPosition() {
		return position;
	}

	public Velocity getVelocity() {
		return velocity;
	}
	
	public double getMaxVelocity() {
		return maxVelocity;
	}

	public double getMinRadius() {
		return minRadius;
	}

	public double getMaxRadius() {
		return maxRadius;
	}

	public double getActualRadius() {
		return actualRadius;
	}

}
