package forced_oscillator;

import forced_oscillator.models.Particle;
import forced_oscillator.models.State;

import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;

public class CoupledVerletSolution implements Iterator<State> {


    // --- Parámetros ---
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;
    private final double amplitud;
    private final double timestep;

    private final LinkedList<State> stateList;

    private boolean firstState;
    private int n;

    public CoupledVerletSolution(double k, double mass, double maxTime, double timestep, double amplitud, State initialState) {
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.amplitud = amplitud;
        this.timestep = timestep;

        this.firstState = true;
        this.n = initialState.getParticles().size();

        this.stateList = new LinkedList<>();
        stateList.add(initialState);
    }

    private double getForce(State state, Particle p) {
        List<Particle> particles = state.getParticles();
        int particleIndex = p.getId();

        if (particleIndex == 0) {
            return -this.k * (particles.get(particleIndex).getPosition() - particles.get(particleIndex + 1).getPosition());
        } else if (particleIndex > 0 && particleIndex < n - 1) {
            return -this.k * (particles.get(particleIndex).getPosition() - particles.get(particleIndex - 1).getPosition()) -
                    this.k * (particles.get(particleIndex).getPosition() - particles.get(particleIndex + 1).getPosition());
        } else if (particleIndex == n - 1) {
            double forceRestauradora = -this.k * (particles.get(particleIndex).getPosition() - particles.get(particleIndex - 1).getPosition());

            // Calcular la fuerza externa
            double omega = Math.sqrt(this.k / this.mass); // Frecuencia angular
            double fuerzaExterna = this.amplitud * Math.cos(omega * state.getTime());

            return forceRestauradora + fuerzaExterna;
        }

        return 0; // No debería llegar aquí
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
        List<Particle> previousParticles = previousState.getParticles();

        double ctime = currentState.getTime();
        List<Particle> currentParticles = currentState.getParticles();

        double nextTime = ctime + timestep;

        List<Particle> newParticles = new LinkedList<>();
        for (int i = 0; i < currentParticles.size(); i++) {
            Particle cp = currentParticles.get(i);
            Particle pp = previousParticles.get(i);

            // Actualizar la posición usando Verlet: r(t + Δt) = 2r(t) - r(t - Δt) + F(t) * Δt^2 / m
            double newPosition = 2 * cp.getPosition() - pp.getPosition() +
                    (getForce(currentState, cp) * Math.pow(timestep, 2)) / cp.getMass();

            // Calcular la nueva velocidad usando Verlet: v(t) = (r(t + Δt) - r(t)) / Δt
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
            double newVel = cp.getVelocity() + timestep * (getForce(actualState, cp) / cp.getMass());
            double newPos = cp.getPosition() + timestep * cp.getVelocity();

            // Actualizar la partícula con la nueva posición y velocidad
            Particle newParticle = cp.clone();
            newParticle.setPosition(newPos);
            newParticle.setVelocity(newVel);

            newParticles.add(newParticle);
        }

        stateList.add(new State(ct + timestep, newParticles));
        return stateList.peekLast();
    }


}
