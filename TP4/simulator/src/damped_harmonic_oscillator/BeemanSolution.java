package damped_harmonic_oscillator;

import damped_harmonic_oscillator.models.Particle;
import damped_harmonic_oscillator.models.State;

import java.util.Iterator;
import java.util.LinkedList;

public class BeemanSolution implements Iterator<State> {


    // --- Parámetros ---
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double maxTime;
    private final double timestep;

    private final LinkedList<State> stateList;

    private boolean firstState;

    public BeemanSolution(double b, double k, double maxTime, double timestep, State initialState) {
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

        double ctime = currentState.getTime();
        Particle cp = currentState.getParticle();

        double nextTime = ctime + timestep;

        // Obtener las aceleraciones actuales y anteriores
        double currentAcceleration = getAceleration(cp); // a(t)
        double previousAcceleration = getAceleration(previousState.getParticle()); // a(t - Δt)

        // --- Actualización de posición usando Beeman ---
        double newPosition = cp.getPosition()
                + cp.getVelocity() * timestep
                + (1 / 6.0) * (4 * currentAcceleration - previousAcceleration) * Math.pow(timestep, 2);

        // --- Predicción de la nueva velocidad ---
        double predictedVelocity = cp.getVelocity()
                + (3 / 2.0) * currentAcceleration * timestep
                - (1 / 2.0) * previousAcceleration * timestep;

        // Creamos una nueva partícula con la nueva posición para calcular la nueva aceleración en t + Δt
        Particle predictedParticle = cp.clone();
        predictedParticle.setPosition(newPosition);
        predictedParticle.setVelocity(predictedVelocity); // Usamos la velocidad predicha

        double newAcceleration = getAceleration(predictedParticle); // a(t + Δt)

        // --- Corrección de la nueva velocidad usando Beeman ---
        double newVelocity = cp.getVelocity()
                + (1 / 6.0) * (2 * newAcceleration + 5 * currentAcceleration - previousAcceleration) * timestep;

        // Clonar la partícula y actualizar posición y velocidad
        Particle np = cp.clone();
        np.setPosition(newPosition);
        np.setVelocity(newVelocity);

        // Crear y agregar el nuevo estado
        State newState = new State(nextTime, np);
        stateList.add(newState);

        return newState;
    }

    private double getForce(Particle p) {
        double position = p.getPosition();
        double velocity = p.getVelocity();

        // Oscilación amortiguada: F = -kx - bv
        double elasticForce = position * (-k);  // Fuerza de Hooke
        double dampingForce = velocity * (-b);  // Fuerza de amortiguamiento

        return elasticForce + dampingForce;
    }

    private double getAceleration(Particle p) {
        return getForce(p) / p.getMass();
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

}
