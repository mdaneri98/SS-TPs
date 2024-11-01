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

		this.ap = 1.1;
		this.bp = 2.1;
		
		this.state = initial;
		this.dt = minRadius / (2 * redVelocityMax);
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
		Vector<Double> newDirection = avoidManeuver(p);
		Position newPosition = updatePosition(p, dt);

		return new Particle(p.getId(), newPosition, target, new Velocity(newDirection, newModule), p.getMaxVelocity(), p.getMinRadius(), p.getMaxRadius(), p.getActualRadius(), p.getTau());
	}
	
	// Método avoidManeuver: Calcula la maniobra de evitación
	private Vector<Double> avoidManeuver(Particle player) {
		Vector<Double> avoidanceVector = new Vector<>(2);
		avoidanceVector.add(0.0);
		avoidanceVector.add(0.0);

		for (Particle p : state.getParticles()) {
			Vector<Double> e_ij = unitDirectionVector(p.getPosition(), player.getPosition());
			double distance_ij = p.getPosition().distanceTo(player.getPosition());


			for (int i = 0; i < 2; i++) {
				avoidanceVector.set(i, avoidanceVector.get(i) + e_ij.get(i) * ap * Math.exp(- distance_ij / bp));
			}
		}

		Vector<Double> targetDirection = unitDirectionVector(player.getTarget().getPosition(), player.getPosition()); 

		Vector<Double> resultVector = new Vector<Double>(
				List.of(
						targetDirection.get(0) + avoidanceVector.get(0),
						targetDirection.get(1) + avoidanceVector.get(1)
						)
				);

		return Utils.normalize(resultVector);
	}

	private Vector<Double> calculateWallCollision(Particle p) {
		return new Vector(List.of(0d,0d));
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
