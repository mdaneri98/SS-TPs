package damped_harmonic_oscillator;

import damped_harmonic_oscillator.models.State;

import java.util.Iterator;
import java.util.LinkedList;

public class GearPredictorCorrector5 implements Iterator<State> {


    // --- Parámetros ---
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;
    private final double initialAmplitud;
    private final double timestep;

    private final LinkedList<State> stateList;

    public GearPredictorCorrector5(double b, double k, double mass, double maxTime, double timestep, double initialAmplitud, State initialState) {
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.initialAmplitud = initialAmplitud;
        this.timestep = timestep;

        this.stateList = new LinkedList<>();
        stateList.add(initialState);
    }

    @Override
    public boolean hasNext() {
        return false;
    }

    @Override
    public State next() {
        return null;
    }

}
