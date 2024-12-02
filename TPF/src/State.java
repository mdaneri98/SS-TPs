


import java.util.Comparator;
import java.util.Objects;
import java.util.Set;

import models.Field;
import models.Particle;

public class State implements Comparator<State> {

    private final double time;
    private final Set<Particle> particles;

    public State(double time, Set<Particle> particles) {
        this.time = time;
        this.particles = particles;
    }


    // ====== Getters & Setters ======
    public double getTime() {
        return time;
    }

    public Set<Particle> getParticles() {
		return particles;
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
