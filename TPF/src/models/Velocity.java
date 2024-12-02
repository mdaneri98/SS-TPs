package models;

import java.util.Vector;

import utils.Utils;

public class Velocity {
    private Vector<Double> direction;
    private double mod;

    public Velocity(Vector direction, double mod) {
    	if (direction.size() != 2) {
    		throw new IllegalArgumentException("Velocity direction has to be 2D.");
    	}
        this.direction = direction;
        this.mod = mod;
    }
    
    public Velocity subtract(Velocity other) {
        Vector<Double> dir = Utils.subtract(this.direction, other.direction);
        double mod = this.mod - other.mod; 
        return new Velocity(dir, mod);
    }
    
    @Override
    public String toString() {
    	return String.format("{%.2f, %.2f}", direction.getFirst()*mod, direction.getLast()*mod);
    }
    
    // ====== GETTERS & SETTERS ======
	public Vector<Double> getDirection() {
		return direction;
	}

	public void setDirection(Vector<Double> direction) {
		this.direction = direction;
	}

	public double getMod() {
		return mod;
	}

	public void setMod(double mod) {
		this.mod = mod;
	}

}