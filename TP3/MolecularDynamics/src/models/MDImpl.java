package models;

import java.sql.SQLOutput;
import java.util.*;



public class MDImpl {

    private final double VELOCITY = 1;
    private final double RADIUS = 0.001;
    private final double MASS = 1;

    private int N;

    // Horizontal, Vertical
    private Map<WallType, Wall> walls = new HashMap<>();

    private Map<Integer, State> states;

    private StaticParticle staticParticle;

    public MDImpl(int n, double l, double staticRadius) {
        N = n;

        createWalls(l);

        states = new HashMap<>();
        states.put(0, generateInitialState(staticRadius));
    }

    public static MDImpl newInstance(int n, double l, double staticRadius, Set<Particle> initialParticles) {
        MDImpl current = new MDImpl(n, l, staticRadius);

        current.states = new HashMap<>();
        current.states.put(0, new State(0, current.getWalls(), initialParticles));

        return current;
    }


    private void createWalls(double L) {
        walls.put(WallType.BOTTOM, new HorizontalWall(L));
        walls.put(WallType.RIGHT, new VerticalWall(L));
        walls.put(WallType.TOP, new HorizontalWall(L));
        walls.put(WallType.LEFT, new VerticalWall(L));
    }

    private State generateInitialState(double staticRadius) {
        Random random = new Random();
        Set<Particle> particleSet = new HashSet<>();

        double L = walls.get(WallType.LEFT).getL();
        staticParticle = new StaticParticle(0, L/2.0, L/2.0, 0, 0, staticRadius, MASS);
        particleSet.add(staticParticle);

        while (particleSet.size() < N) {
            // Posición x aleatoria dentro del área L x L
            double x = random.nextDouble() * (L - 2 * RADIUS) + RADIUS;
            double y = random.nextDouble() * (L - 2 * RADIUS) + RADIUS;

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
        return new State(0, walls, particleSet);
    }


    public void run(int maxEpoch, double collisionDelta) {
        int epoch = 1;
        while (epoch <= maxEpoch) {
            State currentState = states.get(epoch - 1);
            System.out.println("Time[" + currentState.getTime() + "]");


            PriorityQueue<Collision> collisionQueue = currentState.getCollisionList();
            System.out.println("epoc[" + epoch + "] | Los siguientes tc colisiones son: ");
            for (Collision collision : collisionQueue) {
                Double time = collision.getTc();
                System.out.println(time + "s" + " entre " + collision.getParticle() + " y " + collision.getObstacle());
            }


            Collision nextCollision = collisionQueue.poll();
            System.out.println("Próxima colisión: " + nextCollision);

            Set<Particle> newSet = new HashSet<>();
            for (Particle p : currentState.getParticleSet()) {
                if (!p.equals(nextCollision.getParticle()) && !p.equals(nextCollision.getObstacle())) {
                    // Particula no colisiona, actualizamos su ubicación.
                    Particle newParticle = new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelX(), p.getVelY(), p.getRadius(), p.getMass());
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
                particleCollided.move(nextCollision.getTc());
                obstacleParticle.move(nextCollision.getTc());
                newSet.add(particleCollided.applyCollision(obstacleParticle));
                newSet.add(obstacle.applyCollision(particleCollided));
            } else {
                particleCollided.move(nextCollision.getTc());
                newSet.add(obstacle.applyCollision(particleCollided));
            }

            /* Nuevo intervalo para contabilizar las colisiones por segundo. */
            double previousTime = states.get(epoch-1).getTime();
            if (previousTime + nextCollision.getTc() >= collisionDelta) {
                staticParticle.newInterval();
                walls.get(WallType.BOTTOM).newInterval();
                walls.get(WallType.RIGHT).newInterval();
                walls.get(WallType.TOP).newInterval();
                walls.get(WallType.LEFT).newInterval();
            }

            /*
            for (Particle p : currentState.getParticleSet()) {
                if (p.getId() != 0 && Math.hypot(p.getVelX(), p.getVelY()) != VELOCITY) {
                    System.out.println("Velocidad: " + p.getVelX() + p.getVelY() + " | Módulo: " + Math.hypot(p.getVelX(), p.getVelY()));
                }
            }
             */

            states.put(epoch, new State(previousTime + nextCollision.getTc(), walls, newSet));
            epoch++;
        }
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
