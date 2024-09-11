package models;

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

    private void createWalls(double L) {
        walls.put(WallType.BOTTOM, new HorizontalWall(L));
        walls.put(WallType.RIGHT, new VerticalWall(L));
        walls.put(WallType.TOP, new VerticalWall(L));
        walls.put(WallType.LEFT, new HorizontalWall(L));
    }

    private State generateInitialState(double staticRadius) {
        Random random = new Random();
        Set<Particle> particleSet = new HashSet<>();

        double L = walls.get(WallType.LEFT).getL();
        staticParticle = new StaticParticle(0, L/2.0, L/2.0, 0, 0, staticRadius, MASS);
        particleSet.add(staticParticle);

        while (particleSet.size() < N) {
            // Posición x aleatoria dentro del área L x L
            double x = random.nextDouble() * (L - RADIUS);
            double y = random.nextDouble() * (L - RADIUS);
            double angle = random.nextDouble() * Math.PI * 2;
            Particle newParticle = new Particle(particleSet.size(), x, y, VELOCITY, angle, RADIUS, MASS);

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
            if (currentState == null)
                break;
            TreeMap<Double, Pair<Particle, Obstacle>> nextCollide = currentState.getCollidesByTime();

            double tc = nextCollide.firstKey();
            System.out.println("TC: " + tc);
            Pair<Particle, Obstacle> pair = nextCollide.firstEntry().getValue();

            Set<Particle> newSet = new HashSet<>();
            for (Particle p : currentState.getParticleSet()) {
                if (!p.equals(pair.getLeft()) && !p.equals(pair.getRight())) {
                    // Particula no colisiona, actualizamos su ubicación.
                    Particle newParticle = new Particle(p.getId(), p.getPosX(), p.getPosY(), p.getVelocity(), p.getAngle(), p.getRadius(), p.getMass());
                    newParticle.move(tc);
                    newSet.add(newParticle);
                }
            }

            //p colisiona con pair.getRight()
            // p1 -> p2     => p1.applyCollision(p2) && p2.applyCollision(p1)
            // p1 -> |      => |.applyCollision(p1) && p1.applyCollision(|)
            Obstacle obstacle = pair.getRight();
            Particle particleCollided = pair.getLeft();
            particleCollided.move(tc);

            newSet.add(obstacle.applyCollision(particleCollided));
            if (obstacle instanceof Particle obstacleParticle) {
                obstacleParticle.move(tc);
                newSet.add(particleCollided.applyCollision(obstacleParticle));
            }

            /* Nuevo intervalo para contabilizar las colisiones por segundo. */
            double previousTime = states.get(epoch-1).getTime();
            if (previousTime + tc >= collisionDelta) {
                staticParticle.newInterval();
                walls.get(WallType.BOTTOM).newInterval();
                walls.get(WallType.RIGHT).newInterval();
                walls.get(WallType.TOP).newInterval();
                walls.get(WallType.LEFT).newInterval();
            }

            states.put(epoch, new State(previousTime + tc, walls, newSet));
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
