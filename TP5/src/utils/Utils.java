package utils;

import java.util.Vector;

import models.Position;

public class Utils {

	public static double angleBetweenVectors2(Vector<Double> v1, Vector<Double> v2) {
		if (v1.size() != 2 || v2.size() != 2)
			throw new IllegalArgumentException("Both vectors must be 2-dimensional.");

		double dotProduct = v1.get(0) * v2.get(0) + v1.get(1) * v2.get(1);
		double magnitudeV1 = Math.sqrt(v1.get(0) * v1.get(0) + v1.get(1) * v1.get(1));
		double magnitudeV2 = Math.sqrt(v2.get(0) * v2.get(0) + v2.get(1) * v2.get(1));

		double cosTheta = dotProduct / (magnitudeV1 * magnitudeV2);
		cosTheta = Math.max(-1.0, Math.min(1.0, cosTheta)); 

		return Math.acos(cosTheta);
	}
	
	public static double angleBetweenVectors(Vector<Double> v1, Vector<Double> v2) {
	    if (v1.size() != 2 || v2.size() != 2)
	        throw new IllegalArgumentException("Both vectors must be 2-dimensional.");

	    double dotProduct = v1.get(0) * v2.get(0) + v1.get(1) * v2.get(1);
	    double magnitudeV1 = Math.sqrt(v1.get(0) * v1.get(0) + v1.get(1) * v1.get(1));
	    double magnitudeV2 = Math.sqrt(v2.get(0) * v2.get(0) + v2.get(1) * v2.get(1));

	    double cosTheta = dotProduct / (magnitudeV1 * magnitudeV2);

	    // Limitar cosTheta entre -1 y 1
	    cosTheta = Math.max(-1.0, Math.min(1.0, cosTheta));

	    return Math.acos(cosTheta);
	}

	
	public static Vector<Double> subtract(Vector<Double> v1, Vector<Double> v2) {
	    if (v1.size() != 2 || v2.size() != 2)
	        throw new IllegalArgumentException("Both vectors must be 2-dimensional.");

	    Vector<Double> result = new Vector<>(2);
	    result.add(v1.get(0) - v2.get(0));
	    result.add(v1.get(1) - v2.get(1));

	    return result;
	}
	
	public static Vector<Double> rotate(Vector<Double> v, double angle) {
	    if (v.size() != 2)
	        throw new IllegalArgumentException("The vector must be 2-dimensional.");

	    double x = v.get(0);
	    double y = v.get(1);

	    // Matriz de rotación aplicada
	    double rotatedX = x * Math.cos(angle) - y * Math.sin(angle);
	    double rotatedY = x * Math.sin(angle) + y * Math.cos(angle);

	    Vector<Double> rotatedVector = new Vector<>(2);
	    rotatedVector.add(rotatedX);
	    rotatedVector.add(rotatedY);

	    return rotatedVector;
	}
	
	public static Vector<Double> normalize(Vector<Double> v) {
	    if (v.size() != 2)
	        throw new IllegalArgumentException("The vector must be 2-dimensional.");

	    double magnitude = Math.sqrt(v.get(0) * v.get(0) + v.get(1) * v.get(1));
	    
	    if (magnitude == 0) {
	        throw new ArithmeticException("Cannot normalize a zero vector.");
	    }

	    Vector<Double> normalizedVector = new Vector<>(2);
	    normalizedVector.add(v.get(0) / magnitude);
	    normalizedVector.add(v.get(1) / magnitude);

	    return normalizedVector;
	}
	
	public static Double magnitude(Vector<Double> v) {
	    if (v.size() != 2)
	        throw new IllegalArgumentException("The vector must be 2-dimensional.");
	    
	    return Math.sqrt(v.get(0) * v.get(0) + v.get(1) * v.get(1));
	}
	
	public static Double distance(Position p1, Position p2) {
	    Vector<Double> diff = new Vector<>(2);
	    diff.add(p2.getX() - p1.getX());
	    diff.add(p2.getY() - p1.getY());
	    return Utils.magnitude(diff);
	}
	
	public static void printVector(Vector<Double> v) {
		System.out.println(String.format("%f %f", v.getFirst(), v.getLast()));
	}
	
}
