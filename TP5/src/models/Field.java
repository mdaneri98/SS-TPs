package models;

public class Field {

	private final int width;
	private final int height;
	private final Position target;
	
	public Field(int width, int height, Position target) {
		this.width = width;
		this.height = height;
		this.target = target;
	}
	
	public Position getShorterGoal(Particle p) {
		return new Position(0, Math.min(height, Math.max(0, p.getPosition().getY())));
	}
	
	public Position getLeftCenter() {
		return new Position(0, width/2);
	}

	public int getWidth() {
		return width;
	}

	public int getHeight() {
		return height;
	}
	
	public Position getPosition() {
		return target;
	}
	
}
