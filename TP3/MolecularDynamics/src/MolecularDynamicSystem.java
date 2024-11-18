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

        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0),new Velocity(0, 0), staticRadius, staticMass);
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
                   new Velocity(0, 0),
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

        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), new Velocity(0, 0), staticRadius, staticMass);
        particleSet.add(staticParticle);

        // Choca contra la pared derecha => Luego izquierda => Luego derecha => ...
        Particle p1 = new Particle(1, new Position(0.095, 0.01), new Velocity(1, -0.001), radius, mass);
        particleSet.add(p1);

        return new State(0, walls, particleSet, staticParticle);
    }

    private State testStaticInitial(double velocity, double mass, double radius, double staticRadius, double staticMass) {
        Set<Particle> particleSet = new HashSet<>();

        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), new Velocity(0, 0), staticRadius, mass);
        particleSet.add(staticParticle);

        // Choca contra particula estatica => Luego izquierda => Luego particula estatica => ...
        Particle p1 = new Particle(1, new Position(0.01, l/2.0), new Velocity(1, 0), radius, mass);
        particleSet.add(p1);

        return new State(0, walls, particleSet, staticParticle);
    }

    private State testParticlesInitial(double velocity, double mass, double radius, double staticRadius, double staticMass) {
        Set<Particle> particleSet = new HashSet<>();

        // Movemos la partícula estática arriba para que no interfiera
        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), new Velocity(0, 0), staticRadius, mass);
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

    private State initialState(double velocity, double mass, double radius, double staticRadius, double staticMass) {
        Random random = new Random();
        Set<Particle> particleSet = new HashSet<>();

        StaticParticle staticParticle = new StaticParticle(0, new Position(l/2.0, l/2.0), new Velocity(0, 0), staticRadius, staticMass);
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

    public void commonSolution(double velocity, double mass, double radius, double staticRadius, double staticMass, int runSeconds) {
        for (int i = 0; i < 10; i++) {
            String directory = String.format(Locale.US, "common_solution/v_%.2f/%d", velocity, i);

            initial = initialState(velocity, mass, radius, staticRadius, staticMass);

            Path staticPath = getFilePath(directory, "static.csv");
            saveStatic(staticPath);

            Path filepath = getFilePath(directory, "particles.csv");

            Iterator<State> iterator = new MolecularDynamicWithObstacle(velocity, mass, radius, staticRadius, initial, dt);
            runSolution(iterator, directory, filepath, runSeconds);
        }
    }

    public void fixedSolution(double velocity, double mass, double radius, double staticRadius, int runSeconds) {
        for (int i = 0; i < 1; i++) {
            String directory = String.format(Locale.US, "fixed_solution/v_%.2f/%d", velocity, i);

            initial = initialState(velocity, mass, radius, staticRadius, Integer.MAX_VALUE);

            Path staticPath = getFilePath(directory, "static.csv");
            saveStatic(staticPath);

            Path filepath = getFilePath(directory, "particles.csv");

            Iterator<State> iterator = new MolecularDynamicWithObstacle(velocity, mass, radius, staticRadius, initial, dt);
            runSolution(iterator, directory, filepath, runSeconds);
        }
    }

    private void runSolution(Iterator<State> iterator, String directory, Path filepath, int runSeconds) {
        LinkedList<State> statesToSave = new LinkedList<>();
        statesToSave.add(initial);

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
        saveCollisionCounts(directory);
        savePressures(directory);
        saveUniqueCollisionCounts(directory);

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

    private void saveCollisionCounts(String directory) {
        Path countPath = getFilePath(directory, "count.csv");

        try (BufferedWriter writer = Files.newBufferedWriter(countPath, StandardOpenOption.CREATE)) {
            writer.write("time,bottom,right,top,left,static\n");

            // Get all time points from all TreeMaps
            Set<Double> allTimes = new TreeSet<>();
            allTimes.addAll(walls.get(WallType.BOTTOM).collisionCount().keySet());
            allTimes.addAll(walls.get(WallType.RIGHT).collisionCount().keySet());
            allTimes.addAll(walls.get(WallType.TOP).collisionCount().keySet());
            allTimes.addAll(walls.get(WallType.LEFT).collisionCount().keySet());
            allTimes.addAll(initial.getStaticParticle().collisionCount().keySet());

            if(allTimes.size() > 2) {
                Iterator<Double> iterator = allTimes.iterator();
                Double max = null;
                Double secondMax = null;
                while (iterator.hasNext()) {
                    Double current = iterator.next();
                    if (max == null || current > max) {
                        secondMax = max;
                        max = current;
                    }
                }
                allTimes.remove(max);
                allTimes.remove(secondMax);
            }

            // Write data for each time point
            for (Double time : allTimes) {
                writer.write(String.format(Locale.US, "%.6f,%d,%d,%d,%d,%d\n",
                        time,
                        getValueOrZero(walls.get(WallType.BOTTOM).collisionCount(), time, 0),
                        getValueOrZero(walls.get(WallType.RIGHT).collisionCount(), time, 0),
                        getValueOrZero(walls.get(WallType.TOP).collisionCount(), time, 0),
                        getValueOrZero(walls.get(WallType.LEFT).collisionCount(), time, 0),
                        getValueOrZero(initial.getStaticParticle().collisionCount(), time, 0)
                ));
            }
        } catch (IOException e) {
            System.out.println("Error al escribir el archivo de contadores: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void saveUniqueCollisionCounts(String directory) {
        Path countPath = getFilePath(directory, "unique_counts.csv");

        try (BufferedWriter writer = Files.newBufferedWriter(countPath, StandardOpenOption.CREATE)) {
            writer.write("time,static\n");

            TreeMap<Double, Integer> staticCounts = initial.getStaticParticle().uniqueCollisionCount();

            for (Map.Entry<Double, Integer> entry : staticCounts.entrySet()) {
                writer.write(String.format(Locale.US, "%.6f,%d\n",
                        entry.getKey(),
                        entry.getValue()
                ));
            }
        } catch (IOException e) {
            System.out.println("Error al escribir el archivo de contadores: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void savePressures(String directory) {
        System.out.println("Guardando presiones en: " + directory + "/pressure.csv");
        Path pressurePath = getFilePath(directory, "pressure.csv");

        try (BufferedWriter writer = Files.newBufferedWriter(pressurePath, StandardOpenOption.CREATE)) {
            writer.write("time,bottom,right,top,left,static\n");

            // Get all time points from all momentum TreeMaps
            Set<Double> allTimes = new TreeSet<>();
            allTimes.addAll(walls.get(WallType.BOTTOM).momentumCount().keySet());
            allTimes.addAll(walls.get(WallType.RIGHT).momentumCount().keySet());
            allTimes.addAll(walls.get(WallType.TOP).momentumCount().keySet());
            allTimes.addAll(walls.get(WallType.LEFT).momentumCount().keySet());
            allTimes.addAll(initial.getStaticParticle().momentumCount().keySet());

            if(allTimes.size() > 2) {
                Iterator<Double> iterator = allTimes.iterator();
                Double max = null;
                Double secondMax = null;
                while (iterator.hasNext()) {
                    Double current = iterator.next();
                    if (max == null || current > max) {
                        secondMax = max;
                        max = current;
                    }
                }
                allTimes.remove(max);
                allTimes.remove(secondMax);
            }

            for (Double time : allTimes) {
                double bottomPressure = getValueOrZero(walls.get(WallType.BOTTOM).momentumCount(), time, 0.0) / (dt * l);
                double rightPressure = getValueOrZero(walls.get(WallType.RIGHT).momentumCount(), time, 0.0) / (dt * l);
                double topPressure = getValueOrZero(walls.get(WallType.TOP).momentumCount(), time, 0.0) / (dt * l);
                double leftPressure = getValueOrZero(walls.get(WallType.LEFT).momentumCount(), time, 0.0) / (dt * l);
                double staticPressure = getValueOrZero(initial.getStaticParticle().momentumCount(), time, 0.0) /
                        (dt * 2 * Math.PI * initial.getStaticParticle().getRadius());

                writer.write(String.format(Locale.US, "%.12f,%.12f,%.12f,%.12f,%.12f,%.12f\n",
                        time,
                        bottomPressure,
                        rightPressure,
                        topPressure,
                        leftPressure,
                        staticPressure
                ));
            }
            System.out.println("Finalizado guardado de presiones");
        } catch (IOException e) {
            System.out.println("Error al escribir el archivo de presiones: " + e.getMessage());
            e.printStackTrace();
        }
    }

    // Updated helper method for TreeMap
    private <T> T getValueOrZero(TreeMap<Double, T> map, Double time, T defaultValue) {
        return map.getOrDefault(time, defaultValue);
    }

}
