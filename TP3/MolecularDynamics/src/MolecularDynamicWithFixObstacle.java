import models.Event;
import models.FutureCollision;
import models.Obstacle;
import models.particles.Particle;
import models.State;

import java.util.*;

public class MolecularDynamicWithFixObstacle implements Iterator<State> {

    private double velocity;
    private double radius;
    private double mass;
    private double staticRadius;
    private List<State> states;

    public MolecularDynamicWithFixObstacle(double velocity, double radius, double mass, double staticRadius, State initial) {
        this.velocity = velocity;
        this.radius = radius;
        this.mass = mass;
        this.staticRadius = staticRadius;

        this.states = new LinkedList<>();
        this.states.add(initial);
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

        List<FutureCollision> collisionList = currentState.getOrderedCollisionList();
        FutureCollision nextCollision = collisionList.getFirst();

        System.out.println(nextCollision);

        /* Clonamos las particulas y avanzamos hacia la colisión. */
        Set<Particle> saveParticles = new HashSet<>(); /* No se les aplica la colisión, se utilizan para el guardado del estado */
        for (Particle p : currentState.getParticles()) {
            Particle saveParticle = p.clone();
            saveParticle.move(nextCollision.getTc());
            saveParticles.add(saveParticle);
        }

        /* Aplicamos las colisiones */
        Set<Particle> nextParticles = new HashSet<>();  /* Se les aplica la colisión, se utilizan para calcular el siguiente estado */
        Particle collisionParticle = null;
        Obstacle collisionObstacle = null;
        for (Particle p : currentState.getParticles()) {
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
        Event.applyCollision(collisionParticle, collisionObstacle);


        /* Guardamos el estado para la siguiente iteración. */
        State nextState = new State(currentState.getTime() + nextCollision.getTc(), currentState.getWalls(), nextParticles);
        states.add(nextState);

        /* Este estado se utiliza para guardar (Punto 4 del algoritmo). */
        return new State(currentState.getTime() + nextCollision.getTc(), currentState.getWalls(), saveParticles);
    }

}
