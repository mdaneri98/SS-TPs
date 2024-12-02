package models;

import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

public class Field {

	private static Field field;

	private int width;
	private int height;

	private List<Door> doors;

	private Field(int width, int height, List<Door> doors) {
		this.width = width;
		this.height = height;

		this.doors = doors;
	}

	public static Field getInstance() {
		int width = 30;
		int height = 30;
		double doorsLength = 0.5;

		List<Door> doors = new ArrayList<>();

		// Puerta derecha
		Position rightInitial = new Position(width, height/2.0 - doorsLength/2.0);
		Position rightEnd = new Position(width, height/2.0 + doorsLength/2.0);
		doors.add(new Door(rightInitial, rightEnd));

		// Puerta superior
		Position upperInitial = new Position(0.7 * width - doorsLength/2.0, height);
		Position upperEnd = new Position(0.7 * width + doorsLength/2.0, height);
		doors.add(new Door(upperInitial, upperEnd));

		// Puerta inferior
		Position bottomInitial = new Position(0.7 * width - doorsLength/2.0, 0);
		Position bottomEnd = new Position(0.7 * width + doorsLength/2.0, 0);
		doors.add(new Door(bottomInitial, bottomEnd));

		if (field == null)
			field = new Field(width,height, doors);

		return field;
	}

	public double getDistanceToClosestBoundary(Particle p) {
	    double x = p.getPosition().getX();
	    double y = p.getPosition().getY();
	    
	    // Devolver la menor distancia a una pared relevante
	    return Math.min(width - x, Math.min(y, height - y));
	}

	public int getWidth() {
		return width;
	}

	public int getHeight() {
		return height;
	}

	public List<Door> getDoors() {
		return doors;
	}

}
