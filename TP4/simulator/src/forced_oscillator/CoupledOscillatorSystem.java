package forced_oscillator;


import damped_harmonic_oscillator.BeemanSolution;
import forced_oscillator.models.Particle;
import forced_oscillator.models.State;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Locale;

public class CoupledOscillatorSystem {

    // --- Parámetros ---
    private final int n;
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;
    private final double amplitud;

    // --- Cond. iniciales ---
    private final double distance;

    private final List<State> states;

    public CoupledOscillatorSystem(int n, double k, double mass, double maxTime, double distance, double amplitud) {
        this.n = n;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.distance = distance;
        this.amplitud = amplitud;

        this.states = new LinkedList<>();
        states.add(initialize());

    }

    private State initialize() {
        List<Particle> particles = new LinkedList<>();
        for (int i = 0; i < n + 1; i++) {
            particles.add(new Particle(i, 0, getInitialVelocity(), this.mass));
        }
        return new State(0, particles);
    }

    private double getInitialVelocity() {
        return 0;
    }

    public void verletSolution(double wf) {
        String directory = String.format(Locale.US, "verlet_%.6f", wf);

        Path staticPath = getFilePath(directory, "static.csv");
        saveStatic(staticPath, wf);

        Iterator<State> solutionable = new CoupledVerletSolution(k, mass, maxTime, amplitud, wf, initialize());

        Path filepath = getFilePath(directory, "particle.csv");
        while (solutionable.hasNext()) {
            State currentState = solutionable.next();
            currentState.save(filepath);
        }
    }

    private void saveStatic(Path filePath, double wf) {
        boolean fileExists = Files.exists(filePath);

        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE)) {
            if (!fileExists) {
                writer.write("n, k, mass, distance, amplitud, w0, wf\n"); // Encabezados de CSV
            }
            writer.write(String.format(Locale.ENGLISH, "%d, %.6f,%.6f,%.6f,%.6f, %.6f, %.6f\n", n, k, mass, distance, amplitud, Math.sqrt(k/mass), wf));
        } catch (IOException e) {
            System.out.println("Error al escribir un estado: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private Path getFilePath(String directory, String filename) {
        try {
            String projectPath = Paths.get("").toAbsolutePath().toString();
            Path directoryPath = Paths.get(projectPath, "python", "outputs", "multiple", directory);
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
