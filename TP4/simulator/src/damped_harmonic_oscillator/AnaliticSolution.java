package damped_harmonic_oscillator;

import damped_harmonic_oscillator.models.Particle;
import damped_harmonic_oscillator.models.State;

import java.nio.file.Path;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

public class AnaliticSolution implements Iterator<State> {

    // --- Parámetros ---
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;
    private final double initialAmplitud;
    private final double timestep;

    private final LinkedList<State> stateList;

    public AnaliticSolution(double b, double k, double mass, double maxTime, double timestep, double initialAmplitud, State initialState) {
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.initialAmplitud = initialAmplitud;
        this.timestep = timestep;

        this.stateList = new LinkedList<>();
        stateList.add(initialState);
    }

    public boolean hasNext() {
        return stateList.peekLast().getTime() < this.maxTime;
    }

    @Override
    public State next() {
        State previousState = stateList.peekLast();

        double currentTime = previousState.getTime() + timestep;
        Particle currentParticle = previousState.getParticle().clone();

        double newPos = this.initialAmplitud
                * Math.pow(Math.E, -(this.b / (2 * currentParticle.getMass())) * currentTime)
                * Math.cos(Math.sqrt((this.k / currentParticle.getMass()) - (this.b * this.b / (4 * this.mass * this.mass))) * currentTime);
        currentParticle.setPosition(newPos);

        stateList.add(new State(currentTime, currentParticle));
        return stateList.peekLast();
    }

}
