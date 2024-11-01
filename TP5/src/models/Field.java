package models;

import java.util.List;
import java.util.Vector;

public class Field {

	private final int width;
	private final int height;
	
	public Field(int width, int height) {
		this.width = width;
		this.height = height;
	}
	
	public Position getShorterGoal(Particle p) {
		return new Position(0, Math.min(height, Math.max(0, p.getPosition().getY())));
	}
	
	public Position getLeftCenter() {
		return new Position(0, width/2);
	}
	
	// Solo tiene en cuenta las paredes horizontales y la derecha.
	public Position getClosestBoundaryPoint(Particle p) {
	    double x = p.getPosition().getX();
	    double y = p.getPosition().getY();
	    
	    // Encontrar la distancia a las paredes relevantes
	    double dRight = width - x;
	    double dTop = y;
	    double dBottom = height - y;
	    
	    // Encontrar la pared más cercana
	    double minDistance = Math.min(dRight, Math.min(dTop, dBottom));
	    
	    // Devolver el punto más cercano en la pared correspondiente
	    if (minDistance == dRight) {
	        return new Position(width, y);  // Punto en la pared derecha
	    } else if (minDistance == dTop) {
	        return new Position(x, 0);      // Punto en la pared superior
	    } else {
	        return new Position(x, height); // Punto en la pared inferior
	    }
	}

	public Vector<Double> getBoundaryNormal(Particle p) {
	    double x = p.getPosition().getX();
	    double y = p.getPosition().getY();
	    
	    // Encontrar la distancia a las paredes relevantes
	    double dRight = width - x;
	    double dTop = y;
	    double dBottom = height - y;
	    
	    // Encontrar la pared más cercana y devolver su normal
	    double minDistance = Math.min(dRight, Math.min(dTop, dBottom));
	    
	    if (minDistance == dRight) {
	        return new Vector<>(List.of(-1.0, 0.0)); // Normal apunta hacia la izquierda
	    } else if (minDistance == dTop) {
	        return new Vector<>(List.of(0.0, 1.0));  // Normal apunta hacia abajo
	    } else {
	        return new Vector<>(List.of(0.0, -1.0)); // Normal apunta hacia arriba
	    }
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
	
}
