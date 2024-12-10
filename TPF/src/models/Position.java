package models;

public class Position {
    private double posX;
    private double posY;
    private static final double EPSILON = 0.0001;

    public Position(double posX, double posY) {
        this.posX = posX;
        this.posY = posY;
    }

    public double distanceTo(Position other) {
        double deltaX = this.posX - other.getX();
        double deltaY = this.posY - other.getY();
        return Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    }

    public boolean isCloseTo(Position other) {
        return distanceTo(other) <= EPSILON;
    }

    @Override
    public String toString() {
    	return String.format("{%.2f, %.2f}", posX, posY);
    }
    
    public double getX() {
        return posX;
    }

    public void setX(double posX) {
        this.posX = posX;
    }

    public double getY() {
        return posY;
    }

    public void setY(double posY) {
        this.posY = posY;
    }

}