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
		
		this.dt = 0.001;
		
		this.state = initial;
	}
	
	
	@Override
	public boolean hasNext() {
		return state.getPlayer().getPosition().getX() > 0;
	}

	@Override
	public State next() {
		Set<Particle> newParticles = new HashSet<>();
		
		Particle newPlayer = generate(state.getPlayer(), field);
		for (Particle p : state.getParticles()) {
			newParticles.add(generate(p, newPlayer));
		}
		
		
		
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
		} else {
			// -> ¿𝑟(𝑡 − 𝛥𝑡)?
			double newRadius = p.getActualRadius() + p.getMaxRadius() * dt / p.getTau();
			return Math.min(newRadius, p.getMaxRadius());
		}
	}
	
	private Velocity updateVelocity(Particle p, Set<Particle> contacts) {
		double[] newDirection = new double[2];
		if (contacts.isEmpty()) {
			// It should be the same as the direction on p.
			double mod1 = Math.sqrt(
					Math.pow((p.getVelocity().getDirection()[0] - p.getTarget().getPosition().getX()), 2) 
					+ 
					Math.pow((p.getVelocity().getDirection()[1] - p.getTarget().getPosition().getY()), 2));
					
			newDirection[0] = p.getVelocity().getDirection()[0] - p.getTarget().getPosition().getX() / mod1;
			newDirection[1] = p.getVelocity().getDirection()[1] - p.getTarget().getPosition().getY() / mod1;
			
			double v_i = p.getMaxVelocity() * Math.pow(( (p.getActualRadius() - p.getMinRadius()) / p.getMaxRadius() - p.getMinRadius()), beta);
			return new Velocity(newDirection, v_i);
		} else {
			// It should be a new direction.
			Particle contact = contacts.iterator().next();
			
			double mod1 = Math.sqrt(
					Math.pow((p.getVelocity().getDirection()[0] - contact.getPosition().getX()), 2) 
					+ 
					Math.pow((p.getVelocity().getDirection()[1] - contact.getPosition().getY()), 2));
					
			newDirection[0] = p.getVelocity().getDirection()[0] - contact.getPosition().getX() / mod1;
			newDirection[1] = p.getVelocity().getDirection()[1] - contact.getPosition().getY() / mod1;
		
			double v_i = p.getMaxVelocity();
			return new Velocity(newDirection, v_i);
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
