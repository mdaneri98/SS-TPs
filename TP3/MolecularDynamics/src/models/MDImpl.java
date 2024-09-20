package models;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.SQLOutput;
import java.util.*;



public class MDImpl {

    private final double VELOCITY = 1;
    private final double RADIUS = 0.001;
    private final double MASS = 1;

    private int N;

    private int lastSavedState = -1;

    private double staticRadius;

    // Horizontal, Vertical
    private Map<WallType, Wall> walls = new HashMap<>();
    private Map<Double, Double> wallsPressure = new HashMap<>();
    private Map<Double, Double> staticParticlePressure = new HashMap<>();


    private LinkedList<State> states;

    private StaticParticle staticParticle;

    public MDImpl(int n, double l, double staticRadius) {
        N = n;
        this.staticRadius = staticRadius;
        states = new LinkedList<>();

        createWalls(l);
    }

    public static MDImpl newInstance(int n, double l, double staticRadius, Set<Particle> initialParticles) {
        MDImpl current = new MDImpl(n, l, staticRadius);

        current.states = new LinkedList<>();
        current.states.add(new State(0, current.getWalls(), initialParticles));

        return current;
    }


    private void createWalls(double L) {
        walls.put(WallType.HORIZONTAL, new HorizontalWall(L));
        walls.put(WallType.VERTICAL, new VerticalWall(L));
    }

    private State generateInitialState(double time, double staticRadius) {
        Random random = new Random();
        Set<Particle> particleSet = new HashSet<>();

        double L = walls.get(WallType.VERTICAL).getL();
        staticParticle = new StaticParticle(0, L/2.0, L/2.0, 0, 0, staticRadius, MASS);
        particleSet.add(staticParticle);

        while (particleSet.size() < N) {
            // Posición x aleatoria dentro del área L x L
            double x = RADIUS + random.nextDouble() * (L - 2 * RADIUS);
            double y = RADIUS + random.nextDouble() * (L - 2 * RADIUS);

            double angle = random.nextDouble() * (2 * Math.PI);
            double vx = Math.cos(angle) * VELOCITY;
            double vy = Math.sin(angle) * VELOCITY;

            Particle newParticle = new Particle(particleSet.size(), x, y, vx, vy, RADIUS, MASS);

            boolean match = false;
            for (Particle particle : particleSet) {
                match = newParticle.isInside(particle);
                if (match)
                    break;
            }
            if (!match)
                particleSet.add(newParticle);
        }
        return new State(time, walls, particleSet);
    }

    public void save_static(String directoryPath, State state) {
        try {
            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String staticPath = Paths.get(directoryPath, "static.txt").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                writer.write("" + this.walls.get(WallType.VERTICAL).getL() + "\n");
                writer.write("" + state.getParticles().size() + "\n");
                for (Particle particle : state.getParticles()) {
                    writer.write(particle.getRadius() + "\t" + particle.getMass() + "\t" + 1 + "\n");
                }
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }
    }

    public void save_states(String directoryPath) {
        try {
            String dynamicPath = Paths.get(directoryPath, "dynamic.txt").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(dynamicPath, true))) {
            // Iterar sobre los estados sin eliminar el último
                while (states.size() > 2) {
                    State state = states.poll();  // Elimina y obtiene el primer estado
                    writer.write("" + state.getTime());
                    writer.newLine();

                    for (Particle particle : state.getParticles()) {
                        writer.append(particle.getId() + "\t" + particle.getPosX() + "\t" + particle.getPosY() + "\t" + particle.getVelX() + "\t" + particle.getVelY());
                        writer.newLine();
                    }
                }
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }
    }

    public void run(int maxSeconds) {

        double start = System.currentTimeMillis();
        states.add(generateInitialState(0, this.staticRadius));

        /* Guardamos información estática */
        String projectPath = Paths.get("").toAbsolutePath().toString();
        Path directoryPath = Paths.get(projectPath, String.format("test/output"));
        save_static(directoryPath.toString(), states.peek());


        while (true) {
            State currentState = states.pop();
            states.add(currentState);
            //System.out.println("Time[" + currentState.getTime() + "]");

            List<Collision> collisionList = currentState.getCollisionList();

            Collision nextCollision = collisionList.get(0);
            for (Collision collision : collisionList) {
                if (collision.getTc() < nextCollision.getTc()) {
                    nextCollision = collision;
                }
            }

            Set<Particle> newSet = new HashSet<>();
            for (Particle p : currentState.getParticleSet()) {
                if (!p.equals(nextCollision.getParticle()) && !(nextCollision.getObstacle() instanceof Particle && p.equals((Particle) nextCollision.getObstacle()))) {                        // Particula no colisiona, actualizamos su ubicación.
                    Particle newParticle = null;
                    if (p.getId() == 0)
                        newParticle = new StaticParticle(p.getId(), p.getPosX(), p.getPosY(), p.getVelX(), p.getVelY(), p.getRadius(), p.getMass());
                    else
                        newParticle = new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelX(), p.getVelY(), p.getRadius(), p.getMass());

                    newParticle.move(nextCollision.getTc());
                    newSet.add(newParticle);
                }
            }

            //p colisiona con pair.getRight()
            // p1 -> p2     => p1.applyCollision(p2) && p2.applyCollision(p1)
            // p1 -> |      => |.applyCollision(p1) && p1.applyCollision(|)
            Obstacle obstacle = nextCollision.getObstacle();
            Particle particleCollided = nextCollision.getParticle();

            Set<Particle> collidedParticles = new HashSet<>();
            collidedParticles.add(particleCollided);

            particleCollided.move(nextCollision.getTc());
            if (obstacle instanceof Particle obstacleParticle) {
                if (obstacleParticle.getId() == 0) {
                    collidedParticles.add(obstacleParticle);

                    double momentum = ((StaticParticle) obstacleParticle).getMomentum(particleCollided);
                    if (momentum > 0.5)
                        wallsPressure.put(currentState.getTime(), momentum);
                    staticParticlePressure.put(currentState.getTime(), momentum);

                    newSet.add(obstacleParticle.applyCollision(particleCollided));
                    newSet.add(obstacleParticle);
                } else {
                    obstacleParticle.move(nextCollision.getTc());
                    collidedParticles.add(obstacleParticle);

                    newSet.add(obstacleParticle.applyCollision(particleCollided));
                    newSet.add(particleCollided.applyCollision(obstacleParticle));
                }
            } else if (obstacle instanceof Wall wall) {
                // Wall
                Double momentum = wall.getMomentum(particleCollided);
                if (momentum > 0.5)
                    wallsPressure.put(currentState.getTime(), momentum);

                newSet.add(obstacle.applyCollision(particleCollided));
            }

//            State lastState = states.pop();
            double previousTime = currentState.getTime();

            //List<Collision> collisionListCopy = new LinkedList<>(currentState.getCollisionList());
            //collisionListCopy.remove(nextCollision);
            System.out.println("Collision tc:" + nextCollision.getTc());
            states.add(new State(previousTime + nextCollision.getTc(), walls, newSet));

            if (states.size() > 6) {
                projectPath = Paths.get("").toAbsolutePath().toString();
                directoryPath = Paths.get(projectPath, String.format("test/output"));
                save_states(directoryPath.toString());
            }

            double end = System.currentTimeMillis();
            if (end - start > maxSeconds) {
                break;
            }
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

            double pressure = sumMomentum / (momentums.get(i).size() * deltaTime * this.getWalls().get(WallType.VERTICAL).getL());
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
            double contactArea = 2 * Math.PI * staticParticle.getRadius();

            double pressure = sumMomentum / (momentums.get(i).size() * deltaTime * contactArea);
            pressureByTime.put(deltaTime*i, pressure);
        }
        return pressureByTime;
    }

    public LinkedList<State> getStates() {
        return states;
    }

    public StaticParticle getStaticParticle() {
        return staticParticle;
    }

    public Map<WallType, Wall> getWalls() {
        return walls;
    }

}
