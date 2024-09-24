package damped_harmonic_oscillator;

import damped_harmonic_oscillator.models.Particle;
import damped_harmonic_oscillator.models.State;

import java.util.Iterator;
import java.util.LinkedList;

public class VerletSolution implements Iterator<State> {

    // --- Parámetros ---
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double maxTime;
    private final double timestep;

    private final LinkedList<State> stateList;

    private boolean firstState;

    public VerletSolution(double b, double k, double maxTime, double timestep, State initialState) {
        this.b = b;
        this.k = k;
        this.maxTime = maxTime;
        this.timestep = timestep;
        this.firstState = true;

        this.stateList = new LinkedList<>();
        stateList.add(initialState);
    }

    @Override
    public boolean hasNext() {
        return stateList.peekLast().getTime() < this.maxTime;
    }

    @Override
    public State next() {
        if (firstState) {
            firstState = false;
            return eulersMethod();
        }

        // Obtener el estado anterior
        State previousState = stateList.get(stateList.size() - 2); // Estado anterior al actual
        State currentState = stateList.peekLast();                 // Estado actual

        double ptime = previousState.getTime();
        Particle pp = previousState.getParticle();

        double ctime = currentState.getTime();
        Particle cp = currentState.getParticle();

        double nextTime = ctime + timestep;

        // Actualizar la posición usando Verlet: r(t + Δt) = 2r(t) - r(t - Δt) + F(t) * Δt^2 / m
        double newPosition = 2 * cp.getPosition() - pp.getPosition() +
                (getForce(cp) * Math.pow(timestep, 2)) / cp.getMass();

        // Calcular la nueva velocidad usando Verlet: v(t) = (r(t + Δt) - r(t)) / Δt
        double newVelocity = (newPosition - pp.getPosition()) / (2*timestep);

        // Clonar la partícula y actualizar posición y velocidad
        Particle np = cp.clone();
        np.setPosition(newPosition);
        np.setVelocity(newVelocity);

        // Crear y agregar el nuevo estado
        State newState = new State(nextTime, np);
        stateList.add(newState);

        return newState;
    }

    private State eulersMethod() {
        // Obtener el estado anterior
        State actualState = stateList.peekLast();
        double ct = actualState.getTime();
        Particle cp = actualState.getParticle();

        // Usar Euler para el primer paso
        double newVel = cp.getVelocity() + timestep * (getForce(cp) / cp.getMass());
        double newPos = cp.getPosition() + timestep * cp.getVelocity() + (Math.pow(timestep, 2) * getForce(cp) / (2*cp.getMass()));

        // Actualizar la partícula con la nueva posición y velocidad
        Particle newParticle = cp.clone();
        newParticle.setPosition(newPos);
        newParticle.setVelocity(newVel);

        stateList.add(new State(ct + timestep, newParticle));
        return stateList.peekLast();
    }

    public double getForce(Particle p) {
        double position = p.getPosition();
        double velocity = p.getVelocity();

        // Oscilación amortiguada: F = -kx - bv
        double elasticForce = position * (-k);  // Fuerza de Hooke
        double dampingForce = velocity * (-b);  // Fuerza de amortiguamiento

        return elasticForce + dampingForce;
    }

}
