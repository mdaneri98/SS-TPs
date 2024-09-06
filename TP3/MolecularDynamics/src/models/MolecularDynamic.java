package models;

import java.util.*;

public class MolecularDynamic {

    private final double VELOCITY = 1;
    private final double RADIUS = 0.001;
    private final double MASS = 1;

    private int N;

    // Horizontal, Vertical
    private List<Wall> walls = new ArrayList<>();
    private Map<Integer, State> states;

    private StaticParticle staticParticle;

    public MolecularDynamic(int n, double l, double staticRadius) {
        N = n;

        createWalls(l);

        states = new HashMap<>();
        states.put(0, generateInitialState(staticRadius));
    }

    private void createWalls(double L) {
        walls.add(new HorizontalWall(L));
        walls.add(new VerticalWall(L));
    }

    private State generateInitialState(double staticRadius) {
        Random random = new Random();
        Set<Particle> particleSet = new HashSet<>();

        double L = walls.get(0).getL();
        staticParticle = new StaticParticle(0, L/2.0, L/2.0, 0, 0, staticRadius, MASS);
        particleSet.add(staticParticle);

        while (particleSet.size() < N) {
            // Posición x aleatoria dentro del área L x L
            double x = random.nextDouble() * L;
            double y = random.nextDouble() * L;
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
        return new State(walls, particleSet);
    }


    public void run(int maxEpoch) {
        int epoch = 1;
        while (epoch <= maxEpoch) {
            State currentState = states.get(epoch - 1);
            if (currentState == null)
                break;
            TreeMap<Double, Pair<Particle, Obstacle>> nextCollide = currentState.getCollidesByTime();

            double tc = nextCollide.firstKey();
            Pair<Particle, Obstacle> pair = nextCollide.firstEntry().getValue();


            State newState;
            Set<Particle> newSet = new HashSet<>();
            for (Particle p : currentState.getParticleSet()) {
                if (!p.equals(pair.getLeft()) && !p.equals(pair.getRight())) {
                    // Particula no colisiona, actualizamos su ubicación.
                    double newX = p.getPosX() + p.getVelocityX() * tc;
                    double newY = p.getPosY() + p.getVelocityY() * tc;
                    newSet.add(new Particle(p.getId(), newX, newY, p.getVelocity(), p.getAngle(), p.getRadius(), p.getMass()));
                }
            }

            //p colisiona con pair.getRight()
            // p1 -> p2     => p1.applyCollision(p2) && p2.applyCollision(p1)
            // p1 -> |      => |.applyCollision(p1) && p1.applyCollision(|)
            Obstacle obstacle = pair.getRight();
            Particle particleCollided = pair.getLeft();

            newSet.add(obstacle.applyCollision(particleCollided));
            if (obstacle instanceof Particle)
                newSet.add(particleCollided.applyCollision((Particle) obstacle));


            states.put(epoch, new State(walls, newSet));
            epoch++;
        }
    }

    public Map<Integer, State> getStates() {
        return states;
    }

}
