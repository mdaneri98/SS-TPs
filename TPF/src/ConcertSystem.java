import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.Vector;

import models.*;
import utils.Utils;

public class ConcertSystem implements Iterator<State> {

	// ====== From paper ======
	private final double beta = 0.9;

	// ====== Parameters ======
	private final double maxVelocity;
	private final double tau;
	private final double minRadius;
	private final double maxRadius;

	// ====== FIXED VALUES ======
	private final double ap;
	private final double bp;
	private final double dt;

	private final Field field;

	// ====== ... ======
	private State state;

	public ConcertSystem(int N, Field field, double maxVelocity, double tau, double minRadius, double maxRadius, double ap, double bp, State initial) {
		this.field = field;
		this.tau = tau;
		this.maxVelocity = maxVelocity;
		this.minRadius = minRadius;
		this.maxRadius = maxRadius;

		this.ap = ap;
		this.bp = bp;
		
		this.state = initial;
		this.dt = minRadius / (2 * maxVelocity);
	}


	@Override
	public boolean hasNext() {
		return !state.getParticles().isEmpty();
	}

	@Override
	public State next() {
		Set<Particle> newParticles = new HashSet<>();

		for (Particle p : state.getParticles()) {
			Particle newParticle = escape(p);
			if (!hasEscaped(newParticle)) {
				newParticles.add(newParticle);
			} else {
				System.out.println("Particle " + newParticle.getId() + " has escaped");
			}
		}
		state = new State(state.getTime() + dt, newParticles);
		return state;
	}
	
	// ============ NPC'S ============
	private Particle escape(Particle p) {
		// Check if any particle is in contact with other particle or wall
		boolean hasFieldContact = p.isInsidePersonalSpace(field);
		Set<Particle> contacts = checkContact(p);

		double newRadius = updateRadius(p, !contacts.isEmpty()); /* Unicamente se achica si colisiona con otra particula => ¡No contra pared! */
		double newModule = updateModule(p, newRadius);
		Vector<Double> newDirection = updateDirection(p, contacts);
		Position newPosition = updatePosition(p, dt);
		p.getTarget().addSecondsElapsed(dt);

		return new Particle(p.getId(), newPosition, p.getTarget(), new Velocity(newDirection, newModule), p.getMaxVelocity(), p.getMinRadius(), p.getMaxRadius(), newRadius, p.getTau());
	}
	
	private Set<Particle> checkContact(Particle p) {
	    Set<Particle> contacts = new HashSet<Particle>();

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
			return p.getMaxVelocity();
		return p.getMaxVelocity() * Math.pow( (newRadius - p.getMinRadius()) / (p.getMaxRadius() - p.getMinRadius()) , this.beta);
	}
	
	private Vector<Double> updateDirection(Particle p, Set<Particle> contacts) {
		Vector<Double> newDirection;

		if (contacts.isEmpty()) {
			// Cálculo de e_t = (r_i - T_i)/|r_i - T_i|
			newDirection = unitDirectionVector(p.getTarget().getDoor().getInitial(), p.getPosition());
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

	public boolean hasEscaped(Particle p) {
		return Field.getInstance().getDoors().get(0).isInside(p.getPosition())
				|| Field.getInstance().getDoors().get(1).isInside(p.getPosition())
				|| Field.getInstance().getDoors().get(2).isInside(p.getPosition());
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
