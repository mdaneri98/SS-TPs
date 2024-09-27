package damped_harmonic_oscillator.coupled_oscillators;

import damped_harmonic_oscillator.models.Particle;
import damped_harmonic_oscillator.models.State;

import java.util.LinkedList;
import java.util.List;

public class CoupledOscillatorSystem {

    // --- Parámetros ---
    private final int n;            // Cantidad osciladores
    private final int distance;     // Distancia entre centros.
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;

    // --- Cond. iniciales ---
    //private final double initialPosition;
    //private final double initialAmplitud;

    public CoupledOscillatorSystem(int n, double b, double k, double mass, double maxTime, int distance) {
        this.n = n;
        this.distance = distance;
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
    }

    private List<State> initialize(double initialPosition, double initialVelocity) {
        List<State> states = new LinkedList<>();
        for (int i = 0; i < n; i++) {
            states.add(new State(0, new Particle(0, initialPosition, initialVelocity, this.mass)));
        }
        return states;
    }

    private double getInitialVelocity() {
        //FIXME: Chequearlo.
        return -this.distance * b / (2 * mass);
    }

}
