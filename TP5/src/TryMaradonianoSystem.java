import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.Vector;

import models.Field;
import models.Particle;
import models.Position;
import models.Target;
import models.Velocity;
import utils.Utils;

public class TryMaradonianoSystem implements Iterator<State> {

	static int i = 20;

	// ====== From paper ======
	private final double beta = 0.9;

	// ====== Parameters ======
	private final int N;
	private final double blueVelocityMax;
	private final double redVelocityMax;

	private final double blueTau;
	private final double redTau;

	private final double minRadius;
	private final double maxRadius;

	// ====== FIXED VALUES ======
	private final double ap;
	private final double bp;
	private final double dt;

	private final Field field;

	// ====== ... ======
	private State state;

	public TryMaradonianoSystem(int N, Field field, double blueVelocityMax, double redVelocityMax, double blueTau, double redTau, double minRadius, double maxRadius, State initial) {
		this.N = N;
		this.field = field;
		this.blueVelocityMax = blueVelocityMax;
		this.redVelocityMax = redVelocityMax;
		this.blueTau = blueTau;
		this.redTau = redTau;
		this.minRadius = minRadius;
		this.maxRadius = maxRadius;

		this.ap = 0.3;
		this.bp = 0.3;
		this.dt = 0.001;

		this.state = initial;
	}


	@Override
	public boolean hasNext() {
		for (Particle p : state.getParticles())
			if (state.getPlayer().isInside(p)) {
				return false;
			}
		return state.getPlayer().getPosition().getX() > 0;
	}

	@Override
	public State next() {
		Set<Particle> newParticles = new HashSet<>();

		for (Particle p : state.getParticles()) {
			Particle newParticle = chase(p, state.getPlayer());
			newParticles.add(newParticle);
		}
		Particle newPlayer = avoid(state.getPlayer(), field);

		state = new State(state.getTime() + dt, field, newPlayer, newParticles);
		return state;
	}
	
	// ============ NPC'S ============
	private Particle chase(Particle p, Target target) {
		// Check if any particle is in contact with other particle or wall
		boolean hasFieldContact = p.isInsidePersonalSpace(field);
		Set<Particle> contacts = checkContact(p);

		double newRadius = updateRadius(p, !contacts.isEmpty()); /* Unicamente se achica si colisiona con otra particula => ¡No contra pared! */
		double newModule = updateModule(p, newRadius);
		Vector<Double> newDirection = updateDirection(p, contacts);
		Position newPosition = updatePosition(p, dt);

		return new Particle(p.getId(), newPosition, target, new Velocity(newDirection, newModule), p.getMaxVelocity(), p.getMinRadius(), p.getMaxRadius(), newRadius, p.getTau());
	}

	private Set<Particle> checkContact(Particle p) {
		Set<Particle> contacts = new HashSet<Particle>();

		// Verificar contacto con el jugador si la partícula no es el jugador
		if (!p.equals(state.getPlayer()) && p.isInsidePersonalSpace(state.getPlayer())) {
			contacts.add(state.getPlayer());
		}

		// Verificar contacto con otras partículas
		for (Particle other : state.getParticles()) {
			if (p.equals(other))
				continue;
			if (p.isInsidePersonalSpace(other)) {
				contacts.add(other);
			}
		}

		return contacts;
	}

	private double updateRadius(Particle p, boolean hasContact) {
		if (hasContact)
			return p.getMinRadius();
		
		double newRadius = p.getActualRadius() + p.getMaxRadius() * dt / p.getTau();
		return Math.min(newRadius, p.getMaxRadius());
	}
	
	private double updateModule(Particle p, double newRadius) {
		if (newRadius == p.getMinRadius())
			return p.getMaxRadius();
		return p.getMaxVelocity() * Math.pow( (newRadius - p.getMinRadius()) / (p.getMaxRadius() - p.getMinRadius()) , this.beta);
	}
	
	private Vector<Double> updateDirection(Particle p, Set<Particle> contacts) {
		Vector<Double> newDirection;

		if (contacts.isEmpty()) {
			// Cálculo de e_t = (r_i - T_i)/|r_i - T_i|
			newDirection = unitDirectionVector(p.getTarget().getPosition(), p.getPosition());
		} else {
			Particle contact = contacts.iterator().next();
	
			// Cálculo de e_ij = (r_i - r_j)/|r_i - r_j|
			newDirection = unitDirectionVector(p.getPosition(), contact.getPosition());
			
			/*System.out.println(String.format("[Choque] [%d{x: %.3f, y: %.3f}]->[%d]",
					p.getId(),
					newDirection.getFirst() * p.getMaxVelocity(),
					newDirection.getLast() * p.getMaxVelocity(),
					contact.getId()));
					*/
		}
		return newDirection;
	}
	
	// ============ EL RUGBIER ============
	private Particle avoid(Particle p, Target target) {
		// Check if any particle is in contact with other particle or wall
		boolean hasFieldContact = p.isInsidePersonalSpace(field);
		Set<Particle> contacts = checkContact(p);
		
		double newRadius = updateRadius(p, !contacts.isEmpty()); /* Unicamente se achica si colisiona con otra particula => ¡No contra pared! */
		double newModule = p.getMaxVelocity();	/* FIXME: Preguntar cual sería la velocidad del rugbier. */
		Vector<Double> newDirection = avoidManeuver(p, onVision(p));
		Position newPosition = updatePosition(p, dt);

		return new Particle(p.getId(), newPosition, target, new Velocity(newDirection, newModule), p.getMaxVelocity(), p.getMinRadius(), p.getMaxRadius(), p.getActualRadius(), p.getTau());
	}
	
	// Método avoidManeuver: Calcula la maniobra de evitación
	private Vector<Double> avoidManeuver(Particle p, Set<Particle> onVision) {
	    Vector<Double> avoidanceVector = new Vector<>(2);
	    avoidanceVector.add(0.0);
	    avoidanceVector.add(0.0);

	    for (Particle other : onVision) {
	    	System.out.println(String.format("Rugbier velocity: %f %f", p.getVelocity().getDirection().getFirst() * p.getVelocity().getMod(), p.getVelocity().getDirection().getLast() * p.getVelocity().getMod()));
	    	System.out.println(String.format("Particle velocity: %f %f", other.getVelocity().getDirection().getFirst() * other.getVelocity().getMod(), other.getVelocity().getDirection().getLast() * other.getVelocity().getMod()));
	    	
	        // Step 1: Calculate relative velocity vij = vj - vi
	        Velocity vij = other.getVelocity().subtract(p.getVelocity());
	        System.out.println("Relative velocity (vij): " + vij);

	        // Step 2: Compute angle β between vij and direction to target
	        Vector<Double> targetDirection = unitDirectionVector(p.getTarget().getPosition(), p.getPosition());//new Vector<>(List.of(p.getTarget().getPosition().getX(), p.getTarget().getPosition().getY()));
	        double beta = Utils.angleBetweenVectors(targetDirection, vij.getDirection());
	        System.out.println("Angle beta: " + beta);

	        // Step 3: Check if avoidance is needed
	        if (Math.abs(beta) < Math.PI / 2) {
	            System.out.println("Skipping particle, it's moving away");
	            continue; // Skip this particle as it's moving away
	        }

	        // Step 4: Construct unit vector e^ij (from particle i to j)
	        Vector<Double> eij = unitDirectionVector(other.getPosition(), p.getPosition());
	        System.out.println("Unit vector e^ij: " + eij);

	        // Step 5: Calculate angle α between e^ij and relative velocity
	        double alpha = Utils.angleBetweenVectors(eij, vij.getDirection());
	        System.out.println("Angle alpha: " + alpha);

	        // Step 6: Compute f(α) = |α - π/2|
	        double fAlpha = Math.abs(alpha - Math.PI / 2);
	        System.out.println("f(alpha): " + fAlpha);

	        // Step 7: Rotate e^ij by -sign(α)f(α)
	        Vector<Double> rotatedEij = Utils.rotate(eij, -Math.signum(alpha) * fAlpha);
	        System.out.println("Rotated e^ij: " + rotatedEij);

	        // Step 8: Apply weight based on distance
	        double distance = Utils.distance(p.getPosition(), other.getPosition());
	        double weight = ap * Math.exp(-distance / bp);
	        System.out.println("Weight: " + weight);

	        // Add weighted contribution to avoidance vector
	        avoidanceVector.set(0, avoidanceVector.get(0) + weight * rotatedEij.get(0));
	        avoidanceVector.set(1, avoidanceVector.get(1) + weight * rotatedEij.get(1));
	        System.out.println("Avoidance vector: " + avoidanceVector);
	    }

	    try {
	        Vector<Double> normalizedAvoidanceVector = Utils.normalize(avoidanceVector);
	        //System.out.println("Normalized avoidance vector: " + normalizedAvoidanceVector);
	        return normalizedAvoidanceVector;
	    } catch (ArithmeticException e) {
	        // Handle case where no avoidance is needed
	        //System.out.println("No avoidance needed, returning original vector: " + avoidanceVector);
	        return avoidanceVector;
	    }
	}

	// Método onVision: Obtiene las dos partículas más cercanas en el campo visual
	private Set<Particle> onVision(Particle p) {
	    List<Particle> visibleParticles = new ArrayList<>();
	    
	    for (Particle other : state.getParticles()) {
	        if (p.equals(other)) continue;

	        Vector<Double> directionToOther = unitDirectionVector(other.getPosition(), p.getPosition());
	        double angle = Utils.angleBetweenVectors(p.getVelocity().getDirection(), directionToOther);

	        if (angle >= -Math.PI / 2 && angle <= Math.PI / 2) {
	            visibleParticles.add(other);
	        }
	    }

	    // Ordenar las partículas visibles por distancia a `p`
	    visibleParticles.sort(Comparator.comparingDouble(other -> p.distanceTo(other)));

	    // Seleccionar las dos primeras partículas más cercanas y devolver como un Set
	    return new HashSet<>(visibleParticles.subList(0, Math.min(2, visibleParticles.size())));
	}


	
	
	// ============ SAME ============
	private Vector<Double> unitDirectionVector(Position d1, Position d2) {
		double dx = d1.getX() - d2.getX();
		double dy = d1.getY() - d2.getY();
		double magnitude = Math.sqrt(dx * dx + dy * dy);
		return new Vector<Double>(List.of(dx / magnitude, dy / magnitude));
	}
	
	private Position updatePosition(Particle p, double dt) {
		double vx = p.getVelocity().getDirection().getFirst() * p.getVelocity().getMod();
		double vy = p.getVelocity().getDirection().getLast() * p.getVelocity().getMod();

		double newX = Math.max(0, Math.min(field.getWidth(), p.getPosition().getX() + vx * dt));
		double newY = Math.max(0, Math.min(field.getHeight(), p.getPosition().getY() + vy * dt));

		return new Position(newX, newY);
	}

}
