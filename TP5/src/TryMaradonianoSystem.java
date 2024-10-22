import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Random;
import java.util.Set;

import models.Field;
import models.Particle;
import models.Position;
import models.Velocity;

public class TryMaradonianoSystem implements Iterator<State> {
	
	// ====== Parameters ======
	private final int N; 
	private final double blueVelocityMax;
	private final double redVelocityMax;
	
	private final double blueTau;
	private final double redTau;
	
	private final double minRadius; 
	private final double maxRadius;
	
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
		
		this.state = initial;
	}
	
	
	@Override
	public boolean hasNext() {
		return state.getPlayer().getPosition().getX() > 0;
	}

	@Override
	public State next() {
		
		
		return null;
	}
	
}
