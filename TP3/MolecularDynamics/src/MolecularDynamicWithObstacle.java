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
        
        double currentTime = state.getTime();
        double collisionTime = currentTime - futureCollision.getTc();
        
        int currentInterval = (int)(currentTime / dt);
        int previousInterval = (int)(collisionTime / dt);

        // Inicializar contadores para nuevo intervalo
        if (currentInterval > previousInterval) {
            walls.values().forEach(wall -> wall.collisionCount().add(0));
            state.getStaticParticle().collisionCount().add(0);
        }

        // Actualizar contador de colisiones
        if (futureCollision.getObstacle() instanceof Wall wall) {
        	updateCounts(wall, futureCollision.getParticle());
        } else if (futureCollision.getObstacle() instanceof StaticParticle particle) {
            updateCounts(particle, futureCollision.getParticle());
        }
    }

    private void updateCounts(Wall wall, Particle p) {
        // Inicializar listas si están vacías
        if (wall.momentumCount().isEmpty()) {
            wall.momentumCount().add(0.0);
        }

        int lastIndex = wall.collisionCount().size() - 1;
        wall.collisionCount().set(lastIndex, wall.collisionCount().getLast() + 1);

        // Calcular momento transferido según el tipo de pared
        double transferredMomentum;
        if (wall.getType() == WallType.LEFT || wall.getType() == WallType.RIGHT) {
            transferredMomentum = Math.abs(2 * p.getMass() * Math.abs(p.getVelocity().getX()));
        } else {
            transferredMomentum = Math.abs(2 * p.getMass() * Math.abs(p.getVelocity().getY()));
        }

        // Asegurar que la lista de momentos tenga el mismo tamaño que la de colisiones
        while (wall.momentumCount().size() <= lastIndex) {
            wall.momentumCount().add(0.0);
        }
        
        wall.momentumCount().set(lastIndex, wall.momentumCount().getLast() + transferredMomentum);
    }

    private void updateCounts(StaticParticle sp, Particle p) {
        if (sp.momentumCount().isEmpty()) {
            sp.momentumCount().add(0.0);
        }

        int lastIndex = sp.collisionCount().size() - 1;
        sp.collisionCount().set(lastIndex, sp.collisionCount().getLast() + 1);

        // Calcular momento transferido al obstáculo
        double deltaX = sp.getPosition().getX() - p.getPosition().getX();
        double deltaY = sp.getPosition().getY() - p.getPosition().getY();
        double deltaVx = -p.getVelocity().getX();  // Velocidad relativa
        double deltaVy = -p.getVelocity().getY();
        
        double deltaVdeltaR = deltaVx * deltaX + deltaVy * deltaY;
        double sigma = p.getRadius() + sp.getRadius();
        // Tomamos el valor absoluto del momento transferido
        double transferredMomentum = Math.abs((2 * p.getMass() * deltaVdeltaR) / sigma);

        while (sp.momentumCount().size() <= lastIndex) {
            sp.momentumCount().add(0.0);
        }
        
        sp.momentumCount().set(lastIndex, sp.momentumCount().getLast() + transferredMomentum);
    }
    
}
