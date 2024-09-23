package damped_harmonic_oscillator;

import models.Position;
import models.Velocity;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.LinkedList;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

public class OscillatorSystem {

    // --- Parámetros ---
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;

    // --- Cond. iniciales ---
    private final double initialPosition;
    private final double initialAmplitud;


    public OscillatorSystem(double b, double k, double mass, double maxTime, double initialPosition, double initialAmplitud) {
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.initialPosition = initialPosition;
        this.initialAmplitud = initialAmplitud;
    }

    private State initialize(double initialPosition, double initialVelocity) {
        return new State(0, new Particle(0, initialPosition, initialVelocity, this.mass));
    }

    private double getInitialVelocity() {
        //FIXME: Chequearlo.
        return -this.initialAmplitud * b / (2 * mass);
    }

    public void analiticSolution(double timestep) {
        LinkedList<State> stateList = new LinkedList<>();
        stateList.add(initialize(initialPosition, getInitialVelocity()));

        while (stateList.peekLast().getTime() < this.maxTime) {
            State previousState = stateList.peekLast();

            double currentTime = previousState.getTime() + timestep;
            Particle currentParticle = previousState.getParticle().clone();

            double newPos = this.initialAmplitud
                    * Math.pow(Math.E, -(this.b / (2 * this.mass)) * currentTime)
                    * Math.cos(Math.sqrt((this.k / this.mass) - (this.b * this.b / (4 * this.mass * this.mass))) * currentTime);

            currentParticle.setPosition(newPos);

            stateList.add(new State(currentTime, currentParticle));
        }


        // --- Guardamos los estados ---
        Path filepath = getFilePath("analitic", "particle.csv");
        for (int i = 0; i < stateList.size(); i++) {
            stateList.get(i).save(filepath);
        }

    }

    public void gearPredictorCorrectorOrder5Solution() {

    }

    public void verletSolution() {

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
