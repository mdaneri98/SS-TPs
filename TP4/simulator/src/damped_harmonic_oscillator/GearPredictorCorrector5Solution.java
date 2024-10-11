package damped_harmonic_oscillator;

import damped_harmonic_oscillator.models.Particle;
import damped_harmonic_oscillator.models.State;

import java.util.*;

public class GearPredictorCorrector5Solution implements Iterator<State> {

    // --- Parámetros ---
    private final double b;         // coeficiente de amortiguamiento
    private final double k;         // constante elástica del resorte
    private final double mass;
    private final double maxTime;
    private final double timestep;

    private final LinkedList<State> stateList;

    private List<Double> params = new LinkedList<>();
    private final double[] alphas = new double[]{3.0/16.0, 251.0/360.0, 1.0, 11.0/18.0, 1.0/6.0, 1.0/60.0};

    public GearPredictorCorrector5Solution(double b, double k, double mass, double maxTime, double timestep, State initialState) {
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.timestep = timestep;

        this.stateList = new LinkedList<>();
        stateList.add(initialState);
        params = getParams(initialState);
    }

    @Override
    public boolean hasNext() {
        return stateList.peekLast().getTime() <= this.maxTime;
    }

    @Override
    public State next() {
        State currentState = stateList.peekLast(); // Estado anterior

        double currentTime = currentState.getTime(); // Tiempo anterior
        double nextTime = currentTime + timestep;

        List<Double> predictedValues = predict(); // Predicción de los valores

        double getDeltaR2 = getDeltaR2(predictedValues);
        List<Double> correctedValues = correct(predictedValues, getDeltaR2);

        // Nueva particula y estado.
        Particle newParticle = currentState.getParticle().clone();
        newParticle.setPosition(correctedValues.get(0));
        newParticle.setVelocity(correctedValues.get(1));

        State newState = new State(nextTime, newParticle);
        stateList.add(newState);

        return newState;
    }

/*    private double getDeltaR2(List<Double> predictedValues) {
        double deltaA = - ((k/mass) * (predictedValues.get(0) - params.get(0))
                - (b/mass) * predictedValues.get(1))
                - predictedValues.get(2);
        return deltaA * Math.pow(timestep, 2) / 2.0;
    }*/

    private double getDeltaR2(List<Double> predicted) {
        double r0 = params.get(0);
        double rp = predicted.get(0);
        double rp1 = predicted.get(1);
        double rp2 = predicted.get(2);

        double rAux = - (k/mass) * (rp - r0)
                - (b/mass) * rp1;
        double deltaA = rAux - rp2;
        return deltaA * timestep * timestep / 2.0;
    }

    private List<Double> predict (){
        List<Double> predictions = new ArrayList<>();

        predictions.add(params.get(1) + params.get(2) * timestep + params.get(3) * (timestep * timestep) / 2.0 + params.get(4) * Math.pow(timestep, 3) / 6.0 + params.get(5) * Math.pow(timestep, 4) / 24.0 + params.get(6) * Math.pow(timestep, 5) / 120.0);
        predictions.add(params.get(2) + params.get(3) * timestep + params.get(4) * (timestep * timestep) / 2.0 + params.get(5) * Math.pow(timestep, 3) / 6.0  + params.get(6) * Math.pow(timestep, 4) / 24.0);
        predictions.add(params.get(3) + params.get(4) * timestep + params.get(5) * (timestep * timestep) / 2.0 + params.get(6) * Math.pow(timestep, 3) / 6.0);
        predictions.add(params.get(4) + params.get(5) * timestep + params.get(6) * (timestep * timestep) / 2.0);
        predictions.add(params.get(5) + params.get(6) * timestep);
        predictions.add(params.get(6));

        return predictions;
    }

    private List<Double> correct(List<Double> predictedValues, double deltaR2) {
        List<Double> correctedValues = new LinkedList<>();
        correctedValues.add(predictedValues.get(0) + alphas[0] * deltaR2);
        correctedValues.add(predictedValues.get(1) + alphas[1] * deltaR2 / timestep);
        correctedValues.add(predictedValues.get(2) + alphas[2] * deltaR2 * 2.0 / Math.pow(timestep, 2));
        correctedValues.add(predictedValues.get(3) + alphas[3] * deltaR2 * 6.0 / Math.pow(timestep, 3));
        correctedValues.add(predictedValues.get(4) + alphas[4] * deltaR2 * 24.0 / Math.pow(timestep, 4));
        correctedValues.add(predictedValues.get(5) + alphas[5] * deltaR2 * 120.0 / Math.pow(timestep, 5));

        for (int i = 1; i <= 6; i++) {
            params.set(i, correctedValues.get(i-1));
        }

        return correctedValues;
    }

    private List<Double> getParams(State initial) {
        List<Double> params = new ArrayList<>(7);

        double r0 = 0.0;
        double r = initial.getParticle().getPosition();
        double r1 =  initial.getParticle().getVelocity();
        double r2 = -(k/mass) * r - (b/mass)* r1;
        double r3 = -(k/mass) * r1 - (b/mass) * r2;
        double r4 = -(k/mass) * r2 - (b/mass) * r3;
        double r5 = -(k/mass) * r3 - (b/mass) * r4;

        params.add(r0);
        params.add(r);
        params.add(r1);
        params.add(r2);
        params.add(r3);
        params.add(r4);
        params.add(r5);

        return params;
    }

}