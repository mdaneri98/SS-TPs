package models;

public interface Obstacle {

    double timeToCollide(Particle particle);
    Particle applyCollision(Particle particle);

}
