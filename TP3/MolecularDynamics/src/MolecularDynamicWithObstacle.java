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
        updateCounts(nextCollision);
        

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

    private void updateCounts(FutureCollision futureCollision) {
        State state = states.getLast();
        Map<WallType, Wall> walls = state.getWalls();
        WallType[] wallTypes = WallType.values();
        
        // Verificar si estamos en un nuevo intervalo de tiempo
        double currentInterval = Math.floor(state.getTime() / dt);
        double previousInterval = Math.floor((state.getTime() - futureCollision.getTc()) / dt);
        
        // Si cambió el intervalo, inicializar nuevos contadores
        if (currentInterval > previousInterval) {
            for (WallType type : wallTypes) {
                walls.get(type).collisionCount().add(0);
            }
        }
        state.getStaticParticle().collisionCount().add(0);
        
        // Incrementar el contador de colisiones para cada pared
        for (WallType type : wallTypes) {
            Wall wall = walls.get(type);
            List<Integer> counts = wall.collisionCount();
            int lastIndex = counts.size() - 1;
            int newCount = counts.getLast() + 1;
            counts.set(lastIndex, newCount);
        }
        
        StaticParticle staticParticle = state.getStaticParticle();
        List<Integer> counts = staticParticle.collisionCount();
        int lastIndex = counts.size() - 1;
        int newCount = counts.getLast() + 1;
        counts.set(lastIndex, newCount);
        
    }
    
}
