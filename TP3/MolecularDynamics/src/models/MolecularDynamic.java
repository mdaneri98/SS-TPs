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
        State currentState = states.get(states.size() - 1);
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





        states.put(newState);
    }


}
