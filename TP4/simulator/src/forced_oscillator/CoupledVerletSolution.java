package forced_oscillator;

import forced_oscillator.models.Particle;
import forced_oscillator.models.State;

import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;


public class CoupledVerletSolution implements Iterator<State> {

    // --- Parámetros ---
    private final double k;         // Constante elástica del resorte
    private final double mass;
    private final double maxTime;
    private final double amplitud;

    private final double w;         // Frec. angular
    private final double wf;        // Frec. angular de la fuerza
    private final double timestep;

    private boolean firstTime;
    private final LinkedList<State> stateList;

    private final int n;

    public CoupledVerletSolution(double k, double mass, double maxTime, double amplitud, double wf, State initialState) {
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.amplitud = amplitud;
        this.wf = wf;

        this.w = Math.sqrt(k / mass);
        this.timestep = Math.max(1 / (100 * w), 1e-3);

        this.firstTime = true;
        this.n = initialState.getParticles().size();

        this.stateList = new LinkedList<>();
        stateList.add(initialState);


        // Mensaje en salida estándar con todos los datos iniciales y parámetros
        System.out.println("Inicializando CoupledVerlet con los siguientes parámetros:");
        System.out.println("k: " + k);
        System.out.println("mass: " + mass);
        System.out.println("w" + w);
        System.out.println("maxTime: " + maxTime);
        System.out.println("timestep: " + timestep);
        System.out.println("frec. angular de la fuerza: " + this.wf);
        System.out.println("amplitud de la fuerza: " + amplitud);
        System.out.println("initialState: " + initialState);
        System.out.println("w0 ideal: " + Math.sin(Math.PI/n) * Math.sqrt(this.k/this.mass)); //debería dar ~10
    }

    private double getForce(State state, Particle p) {
        int particleIndex = p.getId();
        if (particleIndex <= 0 || particleIndex >= n - 1) {
            return 0; // Manejo para partículas límite
        }

        List<Particle> particles = state.getParticles();
        return -this.k * (particles.get(particleIndex).getPosition() - particles.get(particleIndex - 1).getPosition()) -
                this.k * (particles.get(particleIndex).getPosition() - particles.get(particleIndex + 1).getPosition());
    }

    @Override
    public boolean hasNext() {
        return stateList.peekLast().getTime() < this.maxTime;
    }

    @Override
    public State next() {
        if (firstTime) {
            firstTime = false;
            return eulersMethod();
        }
        if (stateList.size() == 3) {
            stateList.removeFirst();
        }

        // Obtener el estado anterior
        State previousState = stateList.get(stateList.size() - 2); // Estado anterior al actual
        State currentState = stateList.get(stateList.size() - 1);  // Estado actual

        double nextTime = currentState.getTime() + timestep;

        List<Particle> newParticles = new LinkedList<>();
        for (int i = 0; i < currentState.getParticles().size(); i++) {
            Particle cp = currentState.getParticles().get(i);
            Particle pp = previousState.getParticles().get(i);

            double newPosition = Double.POSITIVE_INFINITY;
            if (i > 0 && i < n - 1) {
                // Actualizar la posición usando Verlet: r(t + Δt) = 2r(t) - r(t - Δt) + F(t) * Δt^2 / m
                newPosition = 2 * cp.getPosition() - pp.getPosition() +
                        (Math.pow(timestep, 2) / cp.getMass()) * getForce(currentState, cp);
            } else if (i == 0) {
                newPosition = 0;  // Condición de frontera
            } else if (i == n - 1) {
                newPosition = this.amplitud * Math.sin(this.wf * nextTime);  // Oscilador forzado
            }

            // Calcular la nueva velocidad usando Verlet: v(t) = (r(t + Δt) - r(t)) / (2 * Δt)
            double newVelocity = (newPosition - pp.getPosition()) / (2 * timestep);

            // Clonar la partícula y actualizar posición y velocidad
            Particle np = cp.clone();
            np.setPosition(newPosition);
            np.setVelocity(newVelocity);

            newParticles.add(np);
        }

        // Crear y agregar el nuevo estado
        State newState = new State(nextTime, newParticles);
        stateList.add(newState);

        return newState;
    }
    private State eulersMethod() {
        // Obtener el estado anterior
        State actualState = stateList.peekLast();
        double ct = actualState.getTime();
        List<Particle> currentParticles = actualState.getParticles();

        List<Particle> newParticles = new LinkedList<>();
        for (Particle cp : currentParticles) {
            // Usar Euler para el primer paso
            double newVel = cp.getVelocity() + (timestep / cp.getMass()) * getForce(actualState, cp);
            double newPos = cp.getPosition() + timestep * cp.getVelocity() + (Math.pow(timestep, 2) / 2 * cp.getMass()) * getForce(actualState, cp);

            // Actualizar la partícula con la nueva posición y velocidad
            Particle newParticle = cp.clone();
            newParticle.setPosition(newPos);
            newParticle.setVelocity(newVel);

            newParticles.add(newParticle);
        }

        stateList.add(new State(ct + timestep, newParticles));
        return stateList.peekLast();
    }

    public double getTimestep() {
        return timestep;
    }

}
