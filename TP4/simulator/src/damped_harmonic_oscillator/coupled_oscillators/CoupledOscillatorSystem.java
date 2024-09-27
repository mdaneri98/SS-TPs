package damped_harmonic_oscillator.coupled_oscillators;


import damped_harmonic_oscillator.coupled_oscillators.models.Particle;
import damped_harmonic_oscillator.coupled_oscillators.models.State;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

public class CoupledOscillatorSystem {

    // --- Parámetros ---
    private final int n;
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;

    // --- Cond. iniciales ---
    private final double initialDistance;
    private final double amplitud;

    private final List<State> states;

    public CoupledOscillatorSystem(int n, double b, double k, double mass, double maxTime, double initialDistance, double amplitud) {
        this.n = n;
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.amplitud = amplitud;
        this.initialDistance = initialDistance;

        this.states = new LinkedList<>();
        states.add(initialize());

    }

    private State initialize() {
        List<Particle> particles = new LinkedList<>();
        for (int i = 0; i < n; i++) {
            particles.add(new Particle(i, initialDistance * i, getInitialVelocity(), this.mass));
        }
        return new State(0, particles);
    }

    private double getInitialVelocity() {
        return -amplitud * b / (2 * mass);
    }


    public void analiticSolution(double timestep) {
        Iterator<State> solutionable = new CoupledAnaliticSolution(b, k, mass, maxTime, timestep, initialDistance, amplitud, states.get(0));

        Path filepath = getFilePath("coupled_analitic", "particle.csv");
        while (solutionable.hasNext()) {
            State currentState = solutionable.next();
            currentState.save(filepath);
        }
    }

    public void gearPredictorCorrectorOrder5Solution() {

    }

    private Path getFilePath(String directory, String filename) {
        try {
            String projectPath = Paths.get("").toAbsolutePath().toString();
            Path directoryPath = Paths.get(projectPath, "python", "outputs", directory);
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
