import java.util.HashSet;
import java.util.Random;
import java.util.Set;

import models.Field;
import models.Particle;
import models.Position;
import models.Velocity;

public class TryMaradoniano {

	
	private final int N;
	private final Field field;
	private final double blueVelocityMax;
	private final double redVelocityMax;
	private final double blueTau;
	private final double redTau;
	private final double minRadius; 
	private final double maxRadius;
	
	
	public TryMaradoniano(int N, Field field, double blueVelocityMax, double redVelocityMax, double blueTau, double redTau, double minRadius, double maxRadius) {
		this.N = N;
		this.field = field;
		this.blueVelocityMax = blueVelocityMax;
		this.redVelocityMax = redVelocityMax;
		this.blueTau = blueTau;
		this.redTau = redTau;
		this.minRadius = minRadius;
		this.maxRadius = maxRadius;
	}
	
	public State initialState() {
		Random random = new Random();
		Set<Particle> particles = new HashSet<>();
			
		while (particles.size() < N) {
			// Posición x aleatoria dentro del área L x L
            double x = maxRadius + random.nextDouble() * (field.getWidth() - 2 * maxRadius);
            double y = maxRadius + random.nextDouble() * (field.getHeight() - 2 * maxRadius);
            
            Particle blue = new Particle(particles.size() + 1, new Position(x, y), new Position(field.getWidth(), field.getHeight()/2.0), new Velocity(new double[] {0,0}, blueVelocityMax), blueVelocityMax, minRadius, maxRadius, maxRadius);
            
            boolean match = false;
            for (Particle particle : particles) {
                match = blue.isInside(particle);
                if (match)
                    break;
            }
            if (!match)
            	particles.add(blue);
		}
		
		Particle player = new Particle(0, new Position(field.getWidth(), field.getHeight()/2.0), new Position(0, field.getHeight()/2.0), new Velocity(new double[] {0,0}, redVelocityMax), redVelocityMax, minRadius, maxRadius, maxRadius);
		return new State(0.0, field, player, particles);
	}
	
	public void run() {
		TryMaradonianoSystem tms = new TryMaradonianoSystem(N, field, blueVelocityMax, redVelocityMax, blueTau, redTau, minRadius, maxRadius, initialState());
		while (tms.hasNext()) {
			State current = tms.next();
			
			//TODO: Save state
			
			
		}
		
	}
	
	
}
