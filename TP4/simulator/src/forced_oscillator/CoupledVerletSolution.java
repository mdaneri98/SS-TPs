package forced_oscillator;

import forced_oscillator.models.Particle;
import forced_oscillator.models.State;

import java.util.Collections;
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

        this.timestep = 1 / (100 * w);
        //this.timestep = Math.max(idealTimestep, 0.001); // Limitar el timestep a un máximo de 0.001

        this.firstTime = true;
        this.n = initialState.getParticles().size();

        this.stateList = new LinkedList<>();
        stateList.add(initialState);


/*        // Mensaje en salida estándar con todos los datos iniciales y parámetros
        System.out.println("Inicializando CoupledVerlet con los siguientes parámetros:");
        System.out.println("k: " + k);
        System.out.println("mass: " + mass);
        System.out.println("w" + w);
        System.out.println("maxTime: " + maxTime);
        System.out.println("timestep: " + timestep);
        System.out.println("frec. angular de la fuerza: " + this.wf);
        System.out.println("amplitud de la fuerza: " + amplitud);
        System.out.println("initialState: " + initialState);
        System.out.println("w ideal: " + Math.sin(Math.PI/n) * Math.sqrt(this.k/this.mass)); //debería dar ~10*/
    }

    private double getForce(Particle rightParticle, Particle p, Particle leftParticle) {
        int particleIndex = p.getId();
        if (particleIndex <= 0 || particleIndex >= n - 1) {
            return 0; // Manejo para partículas límite
        }

        return -k * (2 * p.getPosition() - rightParticle.getPosition() - leftParticle.getPosition());
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
        State currentState = stateList.peekLast();
        double nextTime = currentState.getTime() + timestep;

        LinkedList<Particle> newParticles = new LinkedList<>();


        // Última particula
        Particle lastParticle = currentState.getParticles().get(n-1).clone();
        lastParticle.setPosition(this.amplitud * Math.sin(this.wf * nextTime));
        //lastParticle.setVelocity((newPosition - pp.getPosition()) / (2 * timestep));
        newParticles.push(lastParticle);

        // Particulas intermedias
        for (int i = n - 2; i >= 1; i--) {
            Particle previousStateCenterParticle = previousState.getParticles().get(i);

            Particle centerParticle = currentState.getParticles().get(i);
            Particle leftParticle = currentState.getParticles().get(i+1);
            Particle rightParticle = currentState.getParticles().get(i-1);

            // Actualizar la posición usando Verlet: r(t + Δt) = 2r(t) - r(t - Δt) + F(t) * Δt^2 / m
            double rt = centerParticle.getPosition();
            double rtp = previousStateCenterParticle.getPosition();
            double force = getForce(rightParticle, centerParticle, leftParticle);
            double newPosition = 2 * rt - rtp + (Math.pow(timestep,2) / centerParticle.getMass()) * force;
            // Calcular la nueva velocidad usando Verlet: v(t) = (r(t + Δt) - r(t)) / (2 * Δt)
            double newVelocity = (newPosition - centerParticle.getPosition()) / (2 * timestep);

            // Clonar la partícula y actualizar posición y velocidad
            Particle np = centerParticle.clone();
            np.setPosition(newPosition);
            np.setVelocity(newVelocity);

            newParticles.push(np);
        }

        Particle firstParticle = currentState.getParticles().get(0).clone();
        newParticles.push(firstParticle);

        // Crear y agregar el nuevo estado
        State newState = new State(nextTime, newParticles);
        stateList.add(newState);

        return newState;
    }

    private State eulersMethod() {
        // Obtener el estado anterior
        State currentState = stateList.peekLast();
        double ct = currentState.getTime();
        double nextTime = ct + timestep;


        LinkedList<Particle> newParticles = new LinkedList<>();


        // Última particula
        Particle lastParticle = currentState.getParticles().get(n - 1).clone();
        lastParticle.setPosition(this.amplitud * Math.sin(this.wf * nextTime));
        //lastParticle.setVelocity((newPosition - pp.getPosition()) / (2 * timestep));
        newParticles.push(lastParticle);

        // Particulas intermedias
        for (int i = n - 2; i >= 1; i--) {
            Particle centerParticle = currentState.getParticles().get(i);
            Particle leftParticle = currentState.getParticles().get(i+1);
            Particle rightParticle = currentState.getParticles().get(i-1);

            double newVel = centerParticle.getVelocity() + (timestep / centerParticle.getMass()) * getForce(leftParticle, centerParticle, rightParticle);
            double newPos = centerParticle.getPosition() + timestep * centerParticle.getVelocity() + (Math.pow(timestep, 2) / 2 * centerParticle.getMass()) * getForce(leftParticle, centerParticle, rightParticle);

            // Clonar la partícula y actualizar posición y velocidad
            Particle np = centerParticle.clone();
            np.setPosition(newPos);
            np.setVelocity(newVel);

            newParticles.push(np);
        }

        Particle firstParticle = currentState.getParticles().get(0).clone();
        newParticles.push(firstParticle);

        // Crear y agregar el nuevo estado
        State newState = new State(nextTime, newParticles);
        stateList.add(newState);

        return newState;
    }

    public double getTimestep() {
        return timestep;
    }

}
