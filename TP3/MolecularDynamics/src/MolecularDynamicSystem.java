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
    private final double dt;
    private final int n;
    

    private final Map<WallType, Wall> walls = new HashMap<>();
    private State initial;

    public MolecularDynamicSystem(int n, double l, double dt) {
        this.l = l;
        this.n = n;
        this.dt = dt;
        
        createWalls(l);
    }

    private void createWalls(double L) {
        walls.put(WallType.BOTTOM, new BottomWall(WallType.BOTTOM, L));
        walls.put(WallType.RIGHT, new RightWall(WallType.RIGHT, L));
        walls.put(WallType.TOP, new TopWall(WallType.TOP, L));
        walls.put(WallType.LEFT, new LeftWall(WallType.LEFT, L));
    }

    private State testWallInitial(double velocity, double mass, double radius, double staticRadius, double staticMass) {
        Set<Particle> particleSet = new HashSet<>();

        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, staticMass);
        particleSet.add(staticParticle);

        // Choca contra la pared derecha => Luego izquierda => Luego derecha => ...
        Particle p1 = new Particle(1, new Position(0.095, 0.01), new Velocity(1, 0), radius, mass);
        particleSet.add(p1);

        return new State(0, walls, particleSet, staticParticle);
    }
    
    private State testOblicuoInitial(double velocity, double mass, double radius, double staticRadius, double staticMass) {
    	   Set<Particle> particleSet = new HashSet<>();

    	   // Movemos la partícula estática arriba para no interferir
    	   StaticParticle staticParticle = new StaticParticle(0, 
    	       new Position(l/2.0, l - 2*staticRadius), 
    	       staticRadius, 
    	       staticMass);
    	   particleSet.add(staticParticle);

    	   // Calcular el punto inicial en la diagonal para P1
    	   double p1x = l/4.0;  // A un cuarto del ancho
    	   double p1y = p1x;    // Misma coordenada y para estar en la diagonal

    	   // Calcular el punto inicial en la diagonal para P2
    	   double p2x = 3*l/4.0;  // A tres cuartos del ancho  
    	   double p2y = p2x;      // Misma coordenada y para estar en la diagonal

    	   // P1: moviéndose hacia arriba-derecha sobre la diagonal
    	   Particle p1 = new Particle(1, 
    	       new Position(p1x, p1y),
    	       new Velocity(velocity/Math.sqrt(2), velocity/Math.sqrt(2)),  // 45 grados (v/√2, v/√2)
    	       radius, 
    	       mass);
    	   particleSet.add(p1);

    	   // P2: moviéndose hacia abajo-izquierda sobre la diagonal
    	   Particle p2 = new Particle(2, 
    	       new Position(p2x, p2y),
    	       new Velocity(-velocity/Math.sqrt(2), -velocity/Math.sqrt(2)),  // 225 grados (-v/√2, -v/√2)
    	       radius, 
    	       mass);
    	   particleSet.add(p2);

    	   // P3: moviéndose paralelo a la diagonal pero desplazado
    	   Particle p3 = new Particle(3, 
    	       new Position(l/2.0, l/4.0),  // Desplazado del centro
    	       new Velocity(velocity/Math.sqrt(2), velocity/Math.sqrt(2)),  // Misma dirección que P1
    	       radius, 
    	       mass);
    	   particleSet.add(p3);

    	   return new State(0, walls, particleSet, staticParticle);
    	}
    
    private State testWallInclinadoInitial(double velocity, double mass, double radius, double staticRadius, double staticMass) {
        Set<Particle> particleSet = new HashSet<>();

        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, staticMass);
        particleSet.add(staticParticle);

        // Choca contra la pared derecha => Luego izquierda => Luego derecha => ...
        Particle p1 = new Particle(1, new Position(0.095, 0.01), new Velocity(1, -0.001), radius, mass);
        particleSet.add(p1);

        return new State(0, walls, particleSet, staticParticle);
    }

    private State testStaticInitial(double velocity, double mass, double radius, double staticRadius, double staticMass) {
        Set<Particle> particleSet = new HashSet<>();

        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, mass);
        particleSet.add(staticParticle);

        // Choca contra particula estatica => Luego izquierda => Luego particula estatica => ...
        Particle p1 = new Particle(1, new Position(0.01, l/2.0), new Velocity(1, 0), radius, mass);
        particleSet.add(p1);

        return new State(0, walls, particleSet, staticParticle);
    }

    private State testParticlesInitial(double velocity, double mass, double radius, double staticRadius, double staticMass) {
        Set<Particle> particleSet = new HashSet<>();

        // Movemos la partícula estática arriba para que no interfiera
        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, mass);
        particleSet.add(staticParticle);

        // Posicionamos las partículas móviles en el mismo eje Y, separadas horizontalmente
        // p1 moviéndose hacia la derecha
        Particle p1 = new Particle(1, new Position(radius, radius+radius/2.0), new Velocity(1, 0), radius, mass);
        particleSet.add(p1);

        // p2 moviéndose hacia la izquierda
        Particle p2 = new Particle(2, new Position(l-3*radius, radius+radius/2.0), new Velocity(-1, 0), radius, mass);
        particleSet.add(p2);

        // p2 moviéndose hacia la izquierda
        Particle p3 = new Particle(3, new Position(l/2, radius+radius/2.0), new Velocity(-1, 0), radius, mass);
        particleSet.add(p3);

        return new State(0, walls, particleSet, staticParticle);
    }

    private State initialState(double velocity, double mass, double radius, double staticRadius, double staticMass) {
        Random random = new Random();
        Set<Particle> particleSet = new HashSet<>();

        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), staticRadius, staticMass);
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
        return new State(0, walls, particleSet, staticParticle);
    }

    public void fixedSolution(double velocity, double mass, double radius, double staticRadius, double staticMass, int runSeconds) {
        String directory = String.format(Locale.US, "fixed_solution", String.format("v_%.2f", velocity));

        initial = initialState(velocity, mass, radius, staticRadius, staticMass);
        
        Path staticPath = getFilePath(directory, "static.csv");
        saveStatic(staticPath);

        Path filepath = getFilePath(directory, "particles.csv");
        
        Iterator<State> iterator = new MolecularDynamicWithObstacle(velocity, mass, radius, staticRadius, initial, dt);
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
        
        // Guardar los contadores de colisiones
        saveCollisionCounts("fixed_solution");
        savePressures("fixed_solution");
        
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
    
    private void saveCollisionCounts(String directory) {
        Path countPath = getFilePath(directory, "count.csv");

        try (BufferedWriter writer = Files.newBufferedWriter(countPath, StandardOpenOption.CREATE)) {
            writer.write("time,bottom,right,top,left,static\n");

            // Obtener las listas de contadores
            List<Integer> bottomCounts = walls.get(WallType.BOTTOM).collisionCount();
            List<Integer> rightCounts = walls.get(WallType.RIGHT).collisionCount();
            List<Integer> topCounts = walls.get(WallType.TOP).collisionCount();
            List<Integer> leftCounts = walls.get(WallType.LEFT).collisionCount();
            List<Integer> staticCounts = initial.getStaticParticle().collisionCount();

            // Encontrar el máximo número de intervalos
            int maxIntervals = Math.max(
                Math.max(
                    Math.max(bottomCounts.size(), rightCounts.size()),
                    Math.max(topCounts.size(), leftCounts.size())
                ),
                staticCounts.size()
            );

            // Función auxiliar para obtener el valor o 0 si el índice está fuera de rango
            for (int i = 0; i < maxIntervals; i++) {
                writer.write(String.format(Locale.US, "%.6f,%d,%d,%d,%d,%d\n",
                    dt * i,
                    getValueOrZero(bottomCounts, i, 0),
                    getValueOrZero(rightCounts, i, 0),
                    getValueOrZero(topCounts, i, 0),
                    getValueOrZero(leftCounts, i, 0),
                    getValueOrZero(staticCounts, i, 0)
                ));
            }
        } catch (IOException e) {
            System.out.println("Error al escribir el archivo de contadores: " + e.getMessage());
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
    
    // Método auxiliar para obtener el valor de la lista o 0 si el índice está fuera de rango
    private <T> T getValueOrZero(List<T> list, int index, T defaultValue) {
        return index < list.size() ? list.get(index) : defaultValue;
    }
    
    private void savePressures(String directory) {
        Path pressurePath = getFilePath(directory, "pressure.csv");

        try (BufferedWriter writer = Files.newBufferedWriter(pressurePath, StandardOpenOption.CREATE)) {
            writer.write("time,bottom,right,top,left,static\n");

            // Obtener las listas de momentos
            List<Double> bottomMoments = walls.get(WallType.BOTTOM).momentumCount();
            List<Double> rightMoments = walls.get(WallType.RIGHT).momentumCount();
            List<Double> topMoments = walls.get(WallType.TOP).momentumCount();
            List<Double> leftMoments = walls.get(WallType.LEFT).momentumCount();
            List<Double> staticMoments = initial.getStaticParticle().momentumCount();

            int maxIntervals = Math.max(
                Math.max(
                    Math.max(bottomMoments.size(), rightMoments.size()),
                    Math.max(topMoments.size(), leftMoments.size())
                ),
                staticMoments.size()
            );

            // Calcular presiones para cada intervalo
            for (int i = 0; i < maxIntervals; i++) {
                // Presión = ΔP / (Δt * L) para paredes
                // Presión = ΔP / (Δt * 2πr) para partícula estática
                double bottomPressure = getValueOrZero(bottomMoments, i, 0d) / (dt * l);
                double rightPressure = getValueOrZero(rightMoments, i, 0d) / (dt * l);
                double topPressure = getValueOrZero(topMoments, i, 0d) / (dt * l);
                double leftPressure = getValueOrZero(leftMoments, i, 0d) / (dt * l);
                double staticPressure = getValueOrZero(staticMoments, i, 0d) / (dt * 2 * Math.PI * initial.getStaticParticle().getRadius());

                writer.write(String.format(Locale.US, "%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n",
                    dt * i,
                    bottomPressure,
                    rightPressure,
                    topPressure,
                    leftPressure,
                    staticPressure
                ));
            }
        } catch (IOException e) {
            System.out.println("Error al escribir el archivo de presiones: " + e.getMessage());
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
        List<List<Double>> momentums = null; //this.getMomentums(deltaTime, this.wallsPressure);


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
        List<List<Double>> momentums = null; //this.getMomentums(deltaTime, this.staticParticlePressure);


        for (int i = 0; i < momentums.size(); i++) {
            double sumMomentum = 0;
            for (Double momentum : momentums.get(i)) {
                sumMomentum += momentum;
            }
            double contactArea = 2 * Math.PI * 2;//staticRadius;

            double pressure = sumMomentum / (momentums.get(i).size() * deltaTime * contactArea);
            pressureByTime.put(deltaTime*i, pressure);
        }
        return pressureByTime;
    }

}
