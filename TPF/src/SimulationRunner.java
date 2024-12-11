import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Locale;
import java.util.Random;
import java.util.Set;
import java.util.Vector;

import models.*;

public class SimulationRunner {


    private final int N;
    private final double p;
    private final Field field;
    private final double maxVelocity;
    private final double tau;
    private final double minRadius;
    private final double maxRadius;
    private final int ct;
    private String outputDirectory = "recital";

    private final static int SECONDS_LIMIT = 600;

    private State initial;

    public SimulationRunner(int N, double p, double maxVelocity, double tau, double minRadius, double maxRadius, int ct) {
        this.N = N;
        this.p = p;
        this.field = Field.getInstance();
        this.maxVelocity = maxVelocity;
        this.tau = tau;
        this.minRadius = minRadius;
        this.maxRadius = maxRadius;
        this.ct = ct;

        this.initial = initialState();
    }

    public State initialState() {
        Random random = new Random();
        Set<Particle> particles = new HashSet<>();

        while (particles.size() < N) {
            // Posición x aleatoria dentro del área L x L
            double x = maxRadius + random.nextDouble() * (field.getWidth() - 2 * maxRadius);
            double y = maxRadius + random.nextDouble() * (field.getHeight() - 2 * maxRadius);
            int doorNumber = random.nextInt(2);
            double ctVariation = ct * (1 + (random.nextDouble() * 0.2 - 0.1));

            Particle blue = new Particle(particles.size(), new Position(x, y), new Target(doorNumber, ct + ctVariation), new Velocity(new Vector<Double>(List.of(0.0, 0.0)), maxVelocity), maxVelocity, minRadius, maxRadius, maxRadius, tau);

            boolean match = false;
            for (Particle particle : particles) {
                match = blue.isInsidePersonalSpace(particle);
                if (match)
                    break;
            }
            if (!match)
                particles.add(blue);
        }

        return new State(0.0, particles);
    }

    public State orderedState() {
        Random random = new Random();
        Set<Particle> particles = new HashSet<>();

        // Calculamos el espacio entre partículas (diámetro máximo)
        double spacing = 2 * maxRadius;

        // Calculamos cuántas partículas caben en cada dimensión
        int particlesPerRow = (int) ((field.getWidth() - 2*maxRadius) / spacing);
        int particlesPerColumn = (int) ((field.getHeight() - 2*maxRadius) / spacing);

        // Calculamos el offset inicial para centrar la grilla
        double startX = maxRadius;
        double startY = maxRadius;

        int particleCount = 0;

        for (int i = 0; i < particlesPerRow && particleCount < N; i++) {
            double x = startX + (i * spacing);

            for (int j = 0; j < particlesPerColumn && particleCount < N; j++) {
                double y = startY + (j * spacing);

                int doorNumber = random.nextInt(3);

                // Añadir un valor aleatorio entre 0 y N segundos
                //int randomSeconds = random.nextInt(0);
                int secondsMustTry = ct;//(int) (4 * Field.getInstance().getWidth() / maxVelocity);

                Particle blue = new Particle(
                        particleCount + 1,
                        new Position(x, y),
                        new Target(doorNumber, secondsMustTry),
                        new Velocity(new Vector<Double>(List.of(0.0, 0.0)), maxVelocity),
                        maxVelocity,
                        minRadius,
                        maxRadius,
                        maxRadius,
                        tau
                );

                particles.add(blue);
                particleCount++;
            }
        }

        return new State(0.0, particles);
    }


    public void run() {
        // Modificar el método run para usar el outputDirectory
        Path staticPath = getFilePath(outputDirectory, "static.txt");
        saveStatic(staticPath);

        Path doorsPath = getFilePath(outputDirectory, "doors.csv");
        saveDoors(doorsPath);

        Path filepath = getFilePath(outputDirectory, "dynamic.txt");

        ConcertSystem tms = new ConcertSystem(p, field, maxVelocity, tau, minRadius, maxRadius, this.initial);
        runSolution(tms, filepath);
    }

    private void runSolution(Iterator<State> iterator, Path filepath) {
        LinkedList<State> statesToSave = new LinkedList<>();
        State initialState = this.initial;
        statesToSave.add(initialState);  // Guardamos el estado inicial

        int stateCounter = 0;
        int saveFrequency = 50;
        int maxStatesToSave = 100;

        State lastState = initialState;  // Guardamos referencia al último estado

        while (iterator.hasNext()) {
            State currentState = iterator.next();
            stateCounter++;
            lastState = currentState;  // Actualizamos el último estado

            if (currentState.getTime() > SECONDS_LIMIT) {
                break;
            }

            if (stateCounter % saveFrequency == 0) {
                statesToSave.add(currentState);
            }

            if (statesToSave.size() >= maxStatesToSave) {
                save(statesToSave, filepath);
                statesToSave.clear();
                // Después de limpiar, volvemos a agregar el último estado guardado
                // para mantener continuidad en el archivo
                statesToSave.add(currentState);
            }
        }

        // Si el último estado no fue guardado por la frecuencia, lo agregamos
        if (lastState != initialState &&
                (statesToSave.isEmpty() || !statesToSave.getLast().equals(lastState))) {
            statesToSave.add(lastState);
        }

        // Guardamos los estados restantes (incluyendo el último si corresponde)
        if (!statesToSave.isEmpty()) {
            save(statesToSave, filepath);
            statesToSave.clear();
        }
    }

    private void saveDoors(Path filePath) {
        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE)) {
            writer.write("initial_x,initial_y,end_x,end_y\n");
            for (Door door : Field.getInstance().getDoors()) {
                writer.write(String.format(Locale.US, "%.6f, %.6f, %.6f,%.6f\n", door.getInitial().getX(), door.getInitial().getY(), door.getEnd().getX(), door.getEnd().getY()));
            }
        } catch (IOException e) {
            System.out.println("Error al escribir la información de las puertas: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void saveStatic(Path filePath) {
        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE)) {
            // Parámetros generales
            writer.write(String.format(Locale.US,
                    "maxVelocity: %.6f"
                            + "\n"
                            + "tau: %.6f"
                            + "\n"
                            + "rMin: %.6f"
                            + "\n"
                            + "rMax: %.6f"
                            + "\n"
                            + "width: %d"
                            + "\n"
                            + "height: %d"
                            + "\n",
                    maxVelocity, tau, minRadius, maxRadius, field.getWidth(), field.getHeight()));
        } catch (IOException e) {
            System.out.println("Error al escribir la información estática: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private Path getFilePath(String directory, String filename) {
        try {
            String projectPath = Paths.get("").toAbsolutePath().toString();
            Path directoryPath = Paths.get(projectPath, "python", "outputs", directory);
            Path filePath = directoryPath.resolve(filename);

            // Crea los directorios si no existen
            Files.createDirectories(directoryPath);

            return filePath;
        } catch (IOException e) {
            System.out.println("Error al crear data files: " + e.getMessage());
            e.printStackTrace();
        }
        return null;
    }

    // Save method
    public void save(List<State> states, Path filePath) {
        boolean fileExists = Files.exists(filePath);

        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            // Escribir encabezados solo si el archivo no existe
            if (!fileExists) {
                // Nothing
            }
            for (State state : states) {
                //System.out.println("Time: " + state.getTime());
                writer.write(String.format(Locale.US, "%.6f\n", state.getTime()));

                for (Particle blue : state.getParticles()) {
                    double velX = blue.getVelocity().getDirection().getFirst() * blue.getVelocity().getMod();
                    double velY = blue.getVelocity().getDirection().getLast() * blue.getVelocity().getMod();
                    writer.write(String.format(Locale.US, "%d,%.6f,%.6f,%.6f,%.6f,%.6f,%d\n", blue.getId(), blue.getPosition().getX(), blue.getPosition().getY(), velX, velY, blue.getActualRadius(), blue.getTarget().getDoor().getNumber()));
                }
            }
        } catch (IOException e) {
            System.out.println("Error al escribir un estado: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void setOutputDirectory(String directory) {
        this.outputDirectory = directory;
    }

}
