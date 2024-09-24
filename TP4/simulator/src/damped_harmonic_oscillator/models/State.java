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


    // Save method
    public void save(Path filePath) {
        boolean fileExists = Files.exists(filePath);

        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            // Escribir encabezados solo si el archivo no existe
            if (!fileExists) {
                writer.write("time,id,position,velocity,mass\n"); // Encabezados de CSV
            }
            // Escribir los datos de la partícula
            writer.write(String.format(Locale.ENGLISH, "%.6f,%d,%.6f,%.6f,%.6f\n", time, particle.getId(), particle.getPosition(), particle.getVelocity(), particle.getMass()));
        } catch (IOException e) {
            System.out.println("Error al escribir un estado: " + e.getMessage());
            e.printStackTrace();
        }
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
