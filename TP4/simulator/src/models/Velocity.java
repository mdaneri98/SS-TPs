package models;

public class Velocity {
    private double velX;
    private double velY;

    public Velocity(double velX, double velY) {
        this.velX = velX;
        this.velY = velY;
    }

    public double getVelX() {
        return velX;
    }

    public void setVelX(double velX) {
        this.velX = velX;
    }

    public double getVelY() {
        return velY;
    }

    public void setVelY(double velY) {
        this.velY = velY;
    }
}