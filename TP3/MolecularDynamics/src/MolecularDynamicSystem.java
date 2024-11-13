import models.*;
import models.particles.Particle;
import models.particles.Position;
import models.particles.StaticParticle;
import models.particles.Velocity;
import models.walls.*;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.*;
import java.util.List;


public class MolecularDynamicSystem {

    private final double l;

    private final double velocity;
    private final double radius;
    private final double mass;
    private final double staticRadius;
    private final double staticMass;
    private final int n;

    // Horizontal, Vertical
    private final Map<WallType, Wall> walls = new HashMap<>();
    private final Map<Double, Double> wallsPressure = new HashMap<>();
    private final Map<Double, Double> staticParticlePressure = new HashMap<>();

    private final State initial;

    public MolecularDynamicSystem(int n, double l, double velocity, double mass, double radius, double staticRadius, double staticMass) {
        this.l = l;
        this.velocity = velocity;
        this.radius = radius;
        this.mass = mass;
        this.staticRadius = staticRadius;
        this.staticMass = staticMass;
        this.n = n;

        createWalls(l);
        initial = testParticlesInitial();
    }

    private void createWalls(double L) {
        walls.put(WallType.BOTTOM, new BottomWall(WallType.BOTTOM, L));
        walls.put(WallType.RIGHT, new RightWall(WallType.RIGHT, L));
        walls.put(WallType.TOP, new TopWall(WallType.TOP, L));
        walls.put(WallType.LEFT, new LeftWall(WallType.LEFT, L));
    }

    private State testWallInitial() {
        Set<Particle> particleSet = new HashSet<>();

        Particle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, staticMass);
        particleSet.add(staticParticle);

        // Choca contra la pared derecha => Luego izquierda => Luego derecha => ...
        Particle p1 = new Particle(1, new Position(0.095, 0.01), new Velocity(1, 0), radius, mass);
        particleSet.add(p1);

        return new State(0, walls, particleSet);
    }
    
    private State testWallInclinadoInitial() {
        Set<Particle> particleSet = new HashSet<>();

        Particle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, staticMass);
        particleSet.add(staticParticle);

        // Choca contra la pared derecha => Luego izquierda => Luego derecha => ...
        Particle p1 = new Particle(1, new Position(0.095, 0.01), new Velocity(1, -0.001), radius, mass);
        particleSet.add(p1);

        return new State(0, walls, particleSet);
    }

    private State testStaticInitial() {
        Set<Particle> particleSet = new HashSet<>();

        Particle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, mass);
        particleSet.add(staticParticle);

        // Choca contra particula estatica => Luego izquierda => Luego particula estatica => ...
        Particle p1 = new Particle(1, new Position(0.01, l/2.0), new Velocity(1, 0), radius, mass);
        particleSet.add(p1);

        return new State(0, walls, particleSet);
    }

    private State testParticlesInitial() {
        Set<Particle> particleSet = new HashSet<>();

        // Movemos la partícula estática arriba para que no interfiera
        Particle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, mass);
        particleSet.add(staticParticle);

        // Posicionamos las partículas móviles en el mismo eje Y, separadas horizontalmente
        // p1 moviéndose hacia la derecha
        Particle p1 = new Particle(1, new Position(radius, radius+radius/2.0), new Velocity(1, 0), radius, mass);
        particleSet.add(p1);

        // p2 moviéndose hacia la izquierda
        Particle p2 = new Particle(2, new Position(l-3*radius, radius+radius/2.0), new Velocity(-1, 0), radius, mass);
        particleSet.add(p2);

        return new State(0, walls, particleSet);
    }

    private State initialState() {
        Random random = new Random();
        Set<Particle> particleSet = new HashSet<>();

        Particle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, mass);
        particleSet.add(staticParticle);

        while (particleSet.size() < n) {
            // Posición x aleatoria dentro del área L x L
            double x = radius + random.nextDouble() * (l - 2 * radius);
            double y = radius + random.nextDouble() * (l - 2 * radius);

            double angle = random.nextDouble() * (2 * Math.PI);
            double vx = Math.cos(angle) * velocity;
            double vy = Math.sin(angle) * velocity;

            Particle newParticle = new Particle(particleSet.size(), new Position(x, y), new Velocity(vx, vy), radius, mass);

            boolean match = false;
            for (Particle particle : particleSet) {
                match = newParticle.isInside(particle);
                if (match)
                    break;
            }
            if (!match)
                particleSet.add(newParticle);
        }
        return new State(0, walls, particleSet);
    }

    public void fixedSolution(int runSeconds) {
        String directory = String.format(Locale.US, "fixed_solution");

        Path staticPath = getFilePath(directory, "static.csv");
        saveStatic(staticPath);

        Path filepath = getFilePath(directory, "particles.csv");

        Iterator<State> iterator = new MolecularDynamicWithFixObstacle(velocity, mass, radius, staticRadius, initial);
        runSolution(iterator, filepath, runSeconds);
    }

    private void runSolution(Iterator<State> iterator, Path filepath, int runSeconds) {
        LinkedList<State> statesToSave = new LinkedList<>();

        int stateCounter = 0;
        int saveFrequency = 1; // Guarda cada 100 estados
        int maxStatesToSave = 100; // Máximo número de estados a guardar antes de escribir en archivo

        long startTime = System.nanoTime();
        long endTime = startTime + (runSeconds * 1_000_000_000L); // Convertir segundos a nanosegundos

        while (System.nanoTime() < endTime) {
            State currentState = iterator.next();
            stateCounter++;

            if (stateCounter % saveFrequency == 0) {
                statesToSave.add(currentState);
            }

            if (statesToSave.size() >= maxStatesToSave) {
                save(statesToSave, filepath);
                statesToSave.clear();
            }
        }

        // Si quedan estados por guardar después de salir del bucle
        if (!statesToSave.isEmpty()) {
            save(statesToSave, filepath);
            statesToSave.clear();
        }
    }

    private void saveStatic(Path filePath) {
        boolean fileExists = Files.exists(filePath);

        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE)) {
            if (!fileExists) {
                // Parámetros generales
                writer.write(this.walls.get(WallType.RIGHT).getL() + "\n");
                writer.write("" + n + "\n");

                // Parámetros individuales
                writer.write("idx,mass,radius\n");
            }

            List<Particle> particles = initial.getParticles().stream().toList();
            for (Particle p : particles) {
                writer.write(String.format(Locale.US, "%d,%.4f,%.4f\n", p.getId(), p.getMass(), p.getRadius()));
            }
        } catch (IOException e) {
            System.out.println("Error al escribir un estado: " + e.getMessage());
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

            if (Files.deleteIfExists(filePath))
                System.out.println("Archivo borrado: " + filePath);

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
                writer.write("time,id,x,y,vx,vy\n"); // Encabezados de CSV
            }
            for (State state : states)
                for (Particle p : state.getParticles())
                    if (p.getId() == 1 || true)
                        writer.write(String.format(Locale.ENGLISH, "%.6f,%d,%.6f,%.6f,%.6f,%.6f\n", state.getTime(), p.getId(), p.getPosition().getX(), p.getPosition().getY(), p.getVelocity().getX(), p.getVelocity().getY()));
        } catch (IOException e) {
            System.out.println("Error al escribir un estado: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private List<List<Double>> getMomentums(double deltaTime, Map<Double, Double> momentumsByTime) {
        // Encontrar el tiempo máximo para determinar el tamaño de la lista
        double maxTime = Collections.max(momentumsByTime.keySet());

        // Crear una lista donde cada índice será un múltiplo de deltaT
        int size = (int) Math.ceil(maxTime / deltaTime);
        List<List<Double>> momentums = new ArrayList<>();

        // Inicializar cada índice con una nueva lista vacía
        for (int i = 0; i < size; i++) {
            momentums.add(new ArrayList<>());
        }

        // Iterar sobre el mapa combinado y agregar los valores a la lista correspondiente
        for (Map.Entry<Double, Double> entry : momentumsByTime.entrySet()) {
            double collisionTime = entry.getKey();
            double momentum = entry.getValue();

            // Encontrar el índice correspondiente en la lista
            int index = (int) Math.floor(collisionTime / deltaTime);

            // Sumar el valor del momento al índice correspondiente
            List<Double> frame = momentums.get(index);
            frame.add(momentum);
        }
        return momentums;
    }

    public Map<Double, Double> calculatePressureForWalls(double deltaTime) {
        Map<Double, Double> pressureByTime = new TreeMap<>();
        List<List<Double>> momentums = this.getMomentums(deltaTime, this.wallsPressure);


        for (int i = 0; i < momentums.size(); i++) {
            double sumMomentum = 0;
            for (Double momentum : momentums.get(i)) {
                sumMomentum += momentum;
            }

            double pressure = sumMomentum / (momentums.get(i).size() * deltaTime * l);
            pressureByTime.put(deltaTime*i, pressure);
        }
        return pressureByTime;
    }

    public Map<Double, Double> calculatePressureForStatic(double deltaTime) {
        Map<Double, Double> pressureByTime = new TreeMap<>();
        List<List<Double>> momentums = this.getMomentums(deltaTime, this.staticParticlePressure);


        for (int i = 0; i < momentums.size(); i++) {
            double sumMomentum = 0;
            for (Double momentum : momentums.get(i)) {
                sumMomentum += momentum;
            }
            double contactArea = 2 * Math.PI * staticRadius;

            double pressure = sumMomentum / (momentums.get(i).size() * deltaTime * contactArea);
            pressureByTime.put(deltaTime*i, pressure);
        }
        return pressureByTime;
    }

}
