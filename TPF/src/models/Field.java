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
		double doorsLength = 1;

		List<Door> doors = new ArrayList<>();

		// Puerta derecha superior
		Position rightUpperInitial = new Position(width, height * 0.75 - doorsLength/2.0);
		Position rightUpperEnd = new Position(width, height * 0.75 + doorsLength/2.0);
		doors.add(new Door(0, rightUpperInitial, rightUpperEnd));

		// Puerta derecha central (original)
		Position rightInitial = new Position(width, height/2.0 - doorsLength/2.0);
		Position rightEnd = new Position(width, height/2.0 + doorsLength/2.0);
		doors.add(new Door(1, rightInitial, rightEnd));

		// Puerta derecha inferior
		Position rightLowerInitial = new Position(width, height * 0.25 - doorsLength/2.0);
		Position rightLowerEnd = new Position(width, height * 0.25 + doorsLength/2.0);
		doors.add(new Door(2, rightLowerInitial, rightLowerEnd));

		// Puerta superior
		Position upperInitial = new Position(0.7 * width - doorsLength/2.0, height);
		Position upperEnd = new Position(0.7 * width + doorsLength/2.0, height);
		doors.add(new Door(3, upperInitial, upperEnd));

		// Puerta inferior
		Position bottomInitial = new Position(0.7 * width - doorsLength/2.0, 0);
		Position bottomEnd = new Position(0.7 * width + doorsLength/2.0, 0);
		doors.add(new Door(4, bottomInitial, bottomEnd));

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
