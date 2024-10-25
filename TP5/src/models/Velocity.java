package models;

public class Velocity {
    private double[] direction;
    private double mod;

    public Velocity(double[] direction, double mod) {
    	if (direction.length != 2) {
    		throw new IllegalArgumentException("Velocity direction has to be 2D.");
    	}
        this.direction = direction;
        this.mod = mod;
    }

    @Override
    public String toString() {
    	return String.format("{%.2f, %.2f}", direction[0]*mod, direction[1]*mod);
    }
    
    // ====== GETTERS & SETTERS ======
	public double[] getDirection() {
		return direction;
	}

	public void setDirection(double[] direction) {
		this.direction = direction;
	}

	public double getMod() {
		return mod;
	}

	public void setMod(double mod) {
		this.mod = mod;
	}

}