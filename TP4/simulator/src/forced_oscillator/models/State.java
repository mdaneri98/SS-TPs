package forced_oscillator.models;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

public class State implements Comparator<State> {

    private final double time;
    private final List<Particle> particles;

    public State(double time, List<Particle> particles) {
        this.time = time;
        this.particles = particles;
    }

    // Getters & Setters

    public double getTime() {
        return time;
    }

    public List<Particle> getParticles() {
        return particles;
    }

    @Override
    public int compare(State o1, State o2) {
        return Double.compare(o1.time, o2.time);
    }

}
