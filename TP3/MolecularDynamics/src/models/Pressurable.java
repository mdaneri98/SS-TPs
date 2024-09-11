package models;

import java.util.List;

public interface Pressurable {

    void incrementMomentum(Particle particle);
    List<Double> getMomentum();
    void newInterval();


}
