package models;

public class Field implements Target {

	private final int width;
	private final int height;
	private final Position target;
	
	public Field(int width, int height, Position target) {
		this.width = width;
		this.height = height;
		this.target = target;
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
