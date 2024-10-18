package models;

import models.particles.Particle;

public interface Obstacle {

    double timeToCollide(Particle particle);

}
