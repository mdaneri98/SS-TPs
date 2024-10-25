


import java.util.Comparator;
import java.util.Objects;
import java.util.Set;

import models.Field;
import models.Particle;

public class State implements Comparator<State> {

    private final double time;
    private final Particle player;
    private final Set<Particle> particles;
    private final Field field;

    public State(double time, Field field, Particle player, Set<Particle> particles) {
        this.time = time;
        this.player = player;
        this.field = field;
        this.particles = particles;
    }


    // ====== Getters & Setters ======
    public double getTime() {
        return time;
    }

    public Set<Particle> getParticles() {
		return particles;
	}
    
    public Particle getPlayer() {
    	return player;
    }


	@Override
    public int hashCode() {
        return Objects.hash(time, particles);
    }

    @Override
    public String toString() {
        return "State{" +
                "time=" + time +
                ", particles=" + particles +
                '}';
    }

    @Override
    public int compare(State o1, State o2) {
        return Double.compare(o1.time, o2.time);
    }

}
