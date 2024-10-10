package damped_harmonic_oscillator.models;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Comparator;
import java.util.Locale;
import java.util.Objects;

public class State implements Comparator<State> {

    private final double time;
    private final Particle particle;

    public State(double time, Particle particle) {
        this.time = time;
        this.particle = particle;
    }




    // Getters & Setters

    public double getTime() {
        return time;
    }

    public Particle getParticle() {
        return particle;
    }

    @Override
    public int hashCode() {
        return Objects.hash(time, particle);
    }

    @Override
    public String toString() {
        return "State{" +
                "time=" + time +
                ", particle=" + particle +
                '}';
    }

    @Override
    public int compare(State o1, State o2) {
        return Double.compare(o1.time, o2.time);
    }

}
