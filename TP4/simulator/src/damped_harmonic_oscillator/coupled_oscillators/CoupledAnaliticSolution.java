package damped_harmonic_oscillator.coupled_oscillators;

import damped_harmonic_oscillator.coupled_oscillators.models.Particle;
import damped_harmonic_oscillator.coupled_oscillators.models.State;

import java.util.Iterator;
import java.util.LinkedList;

public class CoupledAnaliticSolution implements Iterator<State> {

    // --- Parámetros ---
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;
    private final double amplitud;
    private final double initialDistance;
    private final double timestep;

    private final LinkedList<State> stateList;

    public CoupledAnaliticSolution(double b, double k, double mass, double maxTime, double timestep, double initialDistance, double amplitud, State initialState) {
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.amplitud = amplitud;
        this.initialDistance = initialDistance;
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

        for (Particle p : previousState.getParticles()) {
            Particle currentParticleIndexed = p.clone();

            if (p.getId() == 0) {


            } else if (p.getId() == previousState.getParticles().size()-1) {
                // Última particula
                double newPos = this.amplitud
                        * Math.pow(Math.E, -(this.b / (2 * currentParticleIndexed.getMass())) * currentTime)
                        * Math.cos(Math.sqrt((this.k / currentParticleIndexed.getMass()) - (this.b * this.b / (4 * this.mass * this.mass))) * currentTime);
                currentParticleIndexed.setPosition(newPos);
            } else {
                // Particula intermedia

            }





        }


   //     stateList.add(new State(currentTime, currentParticle));
        return stateList.peekLast();
    }

}
