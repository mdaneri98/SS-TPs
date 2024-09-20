package models;

import java.sql.SQLOutput;
import java.util.*;



public class MDImpl {

    private final double VELOCITY = 1;
    private final double RADIUS = 0.001;
    private final double MASS = 1;

    private int N;

    private double staticRadius;

    // Horizontal, Vertical
    private Map<WallType, Wall> walls = new HashMap<>();
    private Map<Double, Double> wallsPressure = new HashMap<>();
    private Map<Double, Double> staticParticlePressure = new HashMap<>();


    private Map<Integer, State> states;

    private StaticParticle staticParticle;

    public MDImpl(int n, double l, double staticRadius) {
        N = n;
        this.staticRadius = staticRadius;
        states = new HashMap<>();

        createWalls(l);
    }

    public static MDImpl newInstance(int n, double l, double staticRadius, Set<Particle> initialParticles) {
        MDImpl current = new MDImpl(n, l, staticRadius);

        current.states = new HashMap<>();
        current.states.put(0, new State(0, current.getWalls(), initialParticles));

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


    public void run(int maxSeconds) {
        int epoch = 1;

        double start = System.currentTimeMillis();
        states.put(0, generateInitialState(0, this.staticRadius));
        while (true) {
            State currentState = states.get(states.size()-1);
            //System.out.println("Time[" + currentState.getTime() + "]");

            TreeSet<Collision> collisionList = currentState.getCollisionList();
            /*
            System.out.println("epoc[" + epoch + "] | Los siguientes tc colisiones son: ");
            for (Collision collision : collisionList) {
                Double time = collision.getTc();
                System.out.println(time + "s" + " entre " + collision.getParticle() + " y " + collision.getObstacle());
            }
             */

            if (collisionList.isEmpty()) {
                System.out.println("No hay más colisiones.");
                break;
            }
            Collision nextCollision = collisionList.getFirst();
            //System.out.println("Próxima colisión: " + nextCollision);

            Set<Particle> newSet = new HashSet<>();
            for (Particle p : currentState.getParticleSet()) {
                if (!p.equals(nextCollision.getParticle()) && !p.equals(nextCollision.getObstacle())) {
                    /*
                    String green = "\u001B[32m";
                    String reset = "\u001B[0m";
                    System.out.println(green + "Movilizamos la particula " + p + reset);
                    */

                    // Particula no colisiona, actualizamos su ubicación.
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

            if (obstacle instanceof Particle obstacleParticle) {
                if (obstacleParticle.getId() == 0) {
                    particleCollided.move(nextCollision.getTc());

                    staticParticlePressure.put(currentState.getTime(), ((StaticParticle) obstacleParticle).getMomentum(particleCollided));

                    newSet.add(obstacleParticle.applyCollision(particleCollided));
                    newSet.add(obstacleParticle);
                } else {
                    particleCollided.move(nextCollision.getTc());
                    obstacleParticle.move(nextCollision.getTc());

                    newSet.add(obstacleParticle.applyCollision(particleCollided));
                    newSet.add(particleCollided.applyCollision(obstacleParticle));
                }
            } else if (obstacle instanceof Wall wall) {
                // Wall
                wallsPressure.put(currentState.getTime(), wall.getMomentum(particleCollided));
                particleCollided.move(nextCollision.getTc());
                newSet.add(obstacle.applyCollision(particleCollided));
            }

            double previousTime = states.get(epoch-1).getTime();
            double end = System.currentTimeMillis();

            states.put(epoch, new State(previousTime + nextCollision.getTc(), walls, newSet));
            //states.get(epoch).updateCollisionsTimes();
            epoch++;
            collisionList.removeFirst();

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

    public Map<Integer, State> getStates() {
        return states;
    }

    public StaticParticle getStaticParticle() {
        return staticParticle;
    }

    public Map<WallType, Wall> getWalls() {
        return walls;
    }

}
