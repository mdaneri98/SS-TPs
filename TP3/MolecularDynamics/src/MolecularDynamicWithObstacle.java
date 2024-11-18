import models.Event;
import models.FutureCollision;
import models.Obstacle;
import models.particles.Particle;
import models.particles.StaticParticle;
import models.walls.Wall;
import models.walls.WallType;
import models.State;

import java.util.*;

public class MolecularDynamicWithObstacle implements Iterator<State> {

    private double velocity;
    private double radius;
    private double mass;
    private double staticRadius;
    private double dt;
    private List<State> states;

    public MolecularDynamicWithObstacle(double velocity, double radius, double mass, double staticRadius, State initial, double dt) {
        this.velocity = velocity;
        this.radius = radius;
        this.mass = mass;
        this.staticRadius = staticRadius;
        this.dt = dt;

        this.states = new LinkedList<>();
        this.states.add(initial);

        for (Wall wall : initial.getWalls().values()) {
            wall.collisionCount().put(0.0, 0);
            wall.momentumCount().put(0.0, 0.0);
        }

    }

    @Override
    public boolean hasNext() {
        return true;
    }

    @Override
    public State next() {
        if (states.size() >= 3)
            states.removeFirst();

        State currentState = states.getLast();

        Set<FutureCollision> collisionList = currentState.getCollisionSet();
        FutureCollision nextCollision = collisionList.iterator().next();

        /* Calculo de presiones */
        updateCounts(currentState.getTime() + nextCollision.getTc(), nextCollision);


        /* Clonamos las particulas y avanzamos hacia la colisión. */
        StaticParticle saveStaticParticle = null;
        Set<Particle> saveParticles = new HashSet<>(); /* No se les aplica la colisión, se utilizan para el guardado del estado */
        for (Particle p : currentState.getParticles()) {
        	if (p.getId() == 0)
        		saveStaticParticle = (StaticParticle)p;

            Particle saveParticle = p.clone();
            saveParticle.move(nextCollision.getTc());
            saveParticles.add(saveParticle);
        }

        /* Aplicamos las colisiones */
        Set<Particle> nextParticles = new HashSet<>();  /* Se les aplica la colisión, se utilizan para calcular el siguiente estado */
        Particle collisionParticle = null;
        Obstacle collisionObstacle = null;
        StaticParticle nextStaticParticle = null;
        for (Particle p : currentState.getParticles()) {
        	if (p.getId() == 0)
        		nextStaticParticle = (StaticParticle)p;

            Particle nextParticle = p.clone();
            nextParticle.move(nextCollision.getTc());

            if (nextCollision.getParticle().equals(nextParticle)) {
                collisionParticle = nextParticle;
            }
            if (nextCollision.getObstacle().equals(nextParticle)) {
                collisionObstacle = nextParticle;
            }
            nextParticles.add(nextParticle);
        }
        if (collisionObstacle == null) {
            collisionObstacle = nextCollision.getObstacle();
        }
        /* Se aplica sobre las instancias nuevas recién creadas. */
        Event.applyCollision(collisionParticle, collisionObstacle);


        /* Guardamos el estado para la siguiente iteración. */
        State nextState = new State(currentState.getTime() + nextCollision.getTc(), currentState.getWalls(), nextParticles, nextStaticParticle);
        states.add(nextState);

        /* Este estado se utiliza para guardar (Punto 4 del algoritmo). */
        return new State(currentState.getTime() + nextCollision.getTc(), currentState.getWalls(), saveParticles, saveStaticParticle);
    }

    private void updateCounts(double time, FutureCollision futureCollision) {
        // Actualizar contadores usando pattern matching
        Obstacle obstacle = futureCollision.getObstacle();
        Particle movingParticle = futureCollision.getParticle();

        if (obstacle instanceof Wall wall) {
            updateCounts(time, wall, movingParticle);
        } else if (obstacle instanceof StaticParticle staticObstacle) {
            updateCounts(time, staticObstacle, movingParticle);
        } else if (movingParticle instanceof StaticParticle staticMoving &&
                obstacle instanceof Particle particle) {
            updateCounts(time, staticMoving, particle);
        }
    }

    private void updateCounts(double time, Wall wall, Particle p) {
        int currentCollisions = wall.collisionCount().getOrDefault(time, 0);
        double currentMomentum = wall.momentumCount().getOrDefault(time, 0d);

        // Calculate new momentum
        double transferredMomentum;
        if (wall.getType() == WallType.LEFT || wall.getType() == WallType.RIGHT) {
            transferredMomentum = Math.abs(2 * p.getMass() * Math.abs(p.getVelocity().getX()));
        } else {
            transferredMomentum = Math.abs(2 * p.getMass() * Math.abs(p.getVelocity().getY()));
        }

        // Update counts
        wall.collisionCount().put(time, currentCollisions + 1);
        wall.momentumCount().put(time, currentMomentum + transferredMomentum);
    }

    private void updateCounts(double currentTime, StaticParticle sp, Particle p) {
        int currentCollisions = sp.collisionCount().getOrDefault(currentTime, 0);
        double currentMomentum = sp.momentumCount().getOrDefault(currentTime, 0d);
        int currentUniqueCollisions = sp.uniqueCollisionCount().getOrDefault(currentTime, 0);

        // Calculate momentum transfer
        double deltaX = sp.getPosition().getX() - p.getPosition().getX();
        double deltaY = sp.getPosition().getY() - p.getPosition().getY();
        double deltaVx = -p.getVelocity().getX();
        double deltaVy = -p.getVelocity().getY();
        double deltaVdeltaR = deltaVx * deltaX + deltaVy * deltaY;
        double sigma = p.getRadius() + sp.getRadius();
        double transferredMomentum = Math.abs((2 * p.getMass() * deltaVdeltaR) / sigma);

        // Update collision counts
        sp.collisionCount().put(currentTime, currentCollisions + 1);
        sp.momentumCount().put(currentTime, currentMomentum + transferredMomentum);

        // Handle unique collisions
        if (!sp.getCollidedParticles().contains(p.getId())) {
            sp.uniqueCollisionCount().put(currentTime, currentUniqueCollisions + 1);
            sp.getCollidedParticles().add(p.getId());
        }
    }

}
