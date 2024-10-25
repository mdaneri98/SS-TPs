import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Random;
import java.util.Set;

import models.Field;
import models.Particle;
import models.Position;
import models.Target;
import models.Velocity;

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

	private final double dt;

	private Set<Integer> repelledParticles = new HashSet<>();

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

		this.dt = 0.0001;

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

		// Limpiar el set de partículas repelidas del dt anterior
		repelledParticles.clear();

		for (Particle p : state.getParticles()) {
			Particle newParticle = generate(p, state.getPlayer());
			newParticles.add(newParticle);
		}
		Particle newPlayer = generate(state.getPlayer(), field);

		state = new State(state.getTime() + dt, field, newPlayer, newParticles);
		return state;
	}

	private Particle generate(Particle p, Target target) {
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
		double[] newDirection = new double[2];

		if (contacts.isEmpty()) {
			// Cálculo de e_t = (r_i - T_i)/|r_i - T_i| según la descripción
			double dx = p.getTarget().getPosition().getX() - p.getPosition().getX();
			double dy = p.getTarget().getPosition().getY() - p.getPosition().getY();

			double magnitude = Math.sqrt(dx * dx + dy * dy);
			newDirection[0] = dx / magnitude;
			newDirection[1] = dy / magnitude;

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
			double dx = p.getPosition().getX() - contact.getPosition().getX();
			double dy = p.getPosition().getY() - contact.getPosition().getY();

			double magnitude = Math.sqrt(dx * dx + dy * dy);

			newDirection[0] = dx / magnitude;
			newDirection[1] = dy / magnitude;

			System.out.println(String.format("[Choque] [%d{x: %.3f, y: %.3f}]->[%d]",
					p.getId(),
					newDirection[0] * p.getMaxVelocity(),
					newDirection[1] * p.getMaxVelocity(),
					contact.getId()));

			return new Velocity(newDirection, p.getMaxVelocity());
		}
	}

	private Position updatePosition(Particle p, double dt) {
		double vx = p.getVelocity().getDirection()[0] * p.getVelocity().getMod();
		double vy = p.getVelocity().getDirection()[1] * p.getVelocity().getMod();

		double newX = Math.max(0, Math.min(field.getWidth(), p.getPosition().getX() + vx * dt));
		double newY = Math.max(0, Math.min(field.getHeight(), p.getPosition().getY() + vy * dt));

		return new Position(newX, newY);
	}

}
