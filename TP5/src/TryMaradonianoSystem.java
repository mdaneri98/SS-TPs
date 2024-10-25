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
		Velocity newVelocity = updateVelocity(p, contacts);
		Position newPosition = updatePosition(p, dt);

		return new Particle(p.getId(), newPosition, target, newVelocity, p.getMaxVelocity(), p.getMinRadius(), p.getMaxRadius(), newRadius, p.getTau());
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
		if (hasContact) {
			return p.getMinRadius();
		}
		// -> ¿𝑟(𝑡 − 𝛥𝑡)?
		double newRadius = p.getActualRadius() + p.getMaxRadius() * dt / p.getTau();
		return Math.min(newRadius, p.getMaxRadius());
	}
	
	private Velocity updateVelocity(Particle p, Set<Particle> contacts) {
		Vector<Double> newDirection;

		if (contacts.isEmpty()) {
			// Cálculo de e_t = (r_i - T_i)/|r_i - T_i|
			newDirection = unitDirectionVector(p.getTarget().getPosition(), p.getPosition());
			
			// Cálculo de v_i
			double v_i = p.getMaxVelocity() * Math.pow(
					(p.getActualRadius() - p.getMinRadius()) /
							(p.getMaxRadius() - p.getMinRadius()),
					beta
			);

			return new Velocity(newDirection, v_i);
		} else {
			Particle contact = contacts.iterator().next();
	
			// Cálculo de e_ij = (r_i - r_j)/|r_i - r_j|
			newDirection = unitDirectionVector(p.getPosition(), contact.getPosition());
			
			System.out.println(String.format("[Choque] [%d{x: %.3f, y: %.3f}]->[%d]",
					p.getId(),
					newDirection.getFirst() * p.getMaxVelocity(),
					newDirection.getLast() * p.getMaxVelocity(),
					contact.getId()));
	
			return new Velocity(newDirection, p.getMaxVelocity());
		}
	}
	
	// ============ EL RUGBIER ============
	private Particle avoid(Particle p, Target target) {
		// Check if any particle is in contact with other particle or wall
		boolean hasFieldContact = p.isInsidePersonalSpace(field);

		Velocity newVelocity = updateVelocity(p, this.onVision(p));
		Position newPosition = updatePosition(p, dt);

		return new Particle(p.getId(), newPosition, target, newVelocity, p.getMaxVelocity(), p.getMinRadius(), p.getMaxRadius(), p.getActualRadius(), p.getTau());
	}
	
	// Método avoidManeuver: Calcula la maniobra de evitación
	private Velocity avoidManeuver(Particle p, Set<Particle> onVision) {
	    Vector<Double> avoidanceVector = new Vector<>(List.of(0.0, 0.0));

	    for (Particle other : onVision) {
	    	Vector<Double> eij= unitDirectionVector(p.getPosition(), other.getPosition());
	    	
	    	Velocity relativeVelocity = other.getVelocity().subtract(p.getVelocity());
	    	double beta = Utils.angleBetweenVectors(p.getVelocity().getDirection(), relativeVelocity.getDirection());
	    	
	    	Vector<Double> directionToOther = unitDirectionVector(other.getPosition(), p.getPosition());
	        double alpha = Utils.angleBetweenVectors(directionToOther, relativeVelocity.getDirection());
	        double fAlpha = Math.abs(Math.abs(alpha) - Math.PI / 2);
	        Utils.rotate(directionToOther, -Math.signum(alpha) * fAlpha);

	        double distance = p.getPosition().distanceTo(other.getPosition());
	        double weight = ap * Math.exp(-distance / bp);

	        avoidanceVector.set(0, avoidanceVector.get(0) + weight * directionToOther.get(0));
	        avoidanceVector.set(1, avoidanceVector.get(1) + weight * directionToOther.get(1));
	    }

	    avoidanceVector = Utils.normalize(avoidanceVector);
	    double newVelocityMagnitude = Math.min(p.getMaxVelocity(), Utils.magnitude(avoidanceVector));
	    return new Velocity(avoidanceVector, newVelocityMagnitude);
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
