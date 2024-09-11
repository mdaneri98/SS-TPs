package models;

import java.util.List;

public interface Obstacle {

    double timeToCollide(Particle particle);
    Particle applyCollision(Particle particle);

}
