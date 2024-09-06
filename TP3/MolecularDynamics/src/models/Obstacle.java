package models;

public interface Obstacle {

    double timeToCollide(Particle particle);
    void update(Particle particle);

}
