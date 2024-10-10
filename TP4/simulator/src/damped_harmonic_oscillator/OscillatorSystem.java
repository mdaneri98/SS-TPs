package damped_harmonic_oscillator;

import damped_harmonic_oscillator.models.Particle;
import damped_harmonic_oscillator.models.State;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.*;

public class OscillatorSystem {

    // --- Parámetros ---
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;

    // --- Cond. iniciales ---
    private final double initialPosition;
    private final double initialAmplitud;

    private final double eps = 1e-1;

    public OscillatorSystem(double b, double k, double mass, double maxTime, double initialPosition) {
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.initialPosition = initialPosition;
        this.initialAmplitud = initialPosition;
    }

    private State initialize(double initialPosition, double initialVelocity) {
        return new State(0, new Particle(0, initialPosition, initialVelocity, this.mass));
    }

    private double getInitialVelocity() {
        //FIXME: Chequearlo.
        return -this.initialAmplitud * b / (2 * mass);
    }

    public void analiticSolution(double timestep, double t2) {
        Iterator<State> solutionable = new AnaliticSolution(b, k, mass, maxTime, timestep, initialAmplitud, initialize(initialPosition, getInitialVelocity()));

        String directory = String.format(Locale.US,"analitic_%.6f", timestep);
        Path filepath = getFilePath(directory, "particle.csv");

        LinkedList<State> statesToSave = new LinkedList<>();
        while (solutionable.hasNext()) {
            State currentState = solutionable.next();
            if (currentState.getTime() / t2 - Math.round(currentState.getTime()) / t2 < eps)
                statesToSave.add(currentState);

            if (statesToSave.size() >= 50) {
                save(statesToSave, filepath);
                statesToSave = new LinkedList<>();
            }
        }
    }

    public void verletSolution(double timestep, double t2) {
        Iterator<State> solutionable = new VerletSolution(b, k, maxTime, timestep, initialize(initialPosition, getInitialVelocity()));

        String directory = String.format(Locale.US,"verlet_%.6f", timestep);
        Path filepath = getFilePath(directory, "particle.csv");

        LinkedList<State> statesToSave = new LinkedList<>();
        while (solutionable.hasNext()) {
            State currentState = solutionable.next();
            if (currentState.getTime() / t2 - Math.round(currentState.getTime()) / t2 < eps)
                statesToSave.add(currentState);

            if (statesToSave.size() >= 50) {
                save(statesToSave, filepath);
                statesToSave = new LinkedList<>();
            }
        }
    }

    public void beemanSolution(double timestep, double t2) {
        Iterator<State> solutionable = new BeemanSolution(b, k, maxTime, timestep, initialize(initialPosition, getInitialVelocity()));

        String directory = String.format(Locale.US, "beeman_%.6f", timestep);
        Path filepath = getFilePath(directory, "particle.csv");

        LinkedList<State> statesToSave = new LinkedList<>();
        while (solutionable.hasNext()) {
            State currentState = solutionable.next();
            if (currentState.getTime() / t2 - Math.round(currentState.getTime()) / t2 < eps)
                statesToSave.add(currentState);

            if (statesToSave.size() >= 50) {
                save(statesToSave, filepath);
                statesToSave = new LinkedList<>();
            }
        }
    }

    public void gearPredictorCorrectorOrder5Solution(double timestep, double t2) {
       Iterator<State> solutionable = new GearPredictorCorrector5Solution(b, k, mass, maxTime, timestep, initialAmplitud, initialize(initialPosition, getInitialVelocity()));

        String directory = String.format(Locale.US, "gear_%.6f", timestep);
        Path filepath = getFilePath(directory, "particle.csv");
        LinkedList<State> statesToSave = new LinkedList<>();
        while (solutionable.hasNext()) {
            State currentState = solutionable.next();
            if (currentState.getTime() / t2 - Math.round(currentState.getTime()) / t2 < eps)
                statesToSave.add(currentState);

            if (statesToSave.size() >= 50) {
                save(statesToSave, filepath);
                statesToSave = new LinkedList<>();
            }
        }
    }

    // Save method
    public void save(List<State> states, Path filePath) {
        boolean fileExists = Files.exists(filePath);

        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            // Escribir encabezados solo si el archivo no existe
            if (!fileExists) {
                writer.write("time,id,position,velocity,mass\n"); // Encabezados de CSV
            }
            for (State state : states) {
                writer.write(String.format(Locale.ENGLISH, "%.6f,%d,%.6f,%.6f,%.6f\n", state.getTime(), state.getParticle().getId(), state.getParticle().getPosition(), state.getParticle().getVelocity(), state.getParticle().getMass()));
            }
        } catch (IOException e) {
            System.out.println("Error al escribir un estado: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private Path getFilePath(String directory, String filename) {
        try {
            String projectPath = Paths.get("").toAbsolutePath().toString();
            Path directoryPath = Paths.get(projectPath, "python", "outputs", "individuals", directory);
            Path filePath = directoryPath.resolve(filename);

            // Crea los directorios si no existen
            Files.createDirectories(directoryPath);

            if (Files.deleteIfExists(filePath))
                System.out.println("Archivo borrado: " + filePath);

            return filePath;
        } catch (IOException e) {
            System.out.println("Error al crear data files: " + e.getMessage());
            e.printStackTrace();
        }
        return null;
    }


}
