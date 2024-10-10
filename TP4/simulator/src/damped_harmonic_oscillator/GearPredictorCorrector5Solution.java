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
    private final double initialAmplitud;
    private final double timestep;

    private final LinkedList<State> stateList;

    private final LinkedList<Map<String, Double>> paramsList = new LinkedList<>();

    private final double[] alphas = new double[]{3.0/16, 251.0/360, 1, 11.0/18, 1.0/6, 1.0/60};

    public GearPredictorCorrector5Solution(double b, double k, double mass, double maxTime, double timestep, double initialAmplitud, State initialState) {
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.initialAmplitud = initialAmplitud;
        this.timestep = timestep;

        this.stateList = new LinkedList<>();
        stateList.add(initialState);
        paramsList.add(getParams(initialState));
    }

    @Override
    public boolean hasNext() {
        return stateList.peekLast().getTime() < this.maxTime;
    }

    @Override
    public State next() {
        if (stateList.size() == 3) {
            stateList.removeFirst();
        }
        if (paramsList.size() == 3) {
            paramsList.removeFirst();
        }

        State currentState = stateList.peekLast(); // Estado anterior

        double currentTime = currentState.getTime(); // Tiempo anterior
        double nextTime = currentTime + timestep;

        Map<String, Double> currentParams = paramsList.peekLast();
        Map<String, Double> predictedValues = predict(currentParams); // Predicción de los valores

        double getDeltaR2 = getDeltaR2(predictedValues);
        Map<String, Double> correctedValues = correct(predictedValues, getDeltaR2);

        paramsList.add(correctedValues); // Añadimos los valores corregidos a la lista de parámetros

        // Nueva particula y estado.
        Particle newParticle = currentState.getParticle().clone();
        newParticle.setPosition(correctedValues.get("r0"));
        newParticle.setVelocity(correctedValues.get("r1"));

        State newState = new State(nextTime, newParticle);
        stateList.add(newState);

        return newState;
    }

    private double getDeltaR2(Map<String, Double> predictedValues) {
        double predictedForce = -k * predictedValues.get("r0") - b * predictedValues.get("r1");
        double predictedAcceleration = predictedForce / mass;
        return (predictedAcceleration - predictedValues.get("r2")) * (Math.pow(timestep, 2) / 2);
    }

    private double getForce(Particle p) {
        double position = p.getPosition();
        double velocity = p.getVelocity();

        // Oscilación amortiguada: F = -kx - bv
        double elasticForce = position * (-k);  // Fuerza de Hooke
        double dampingForce = velocity * (-b);  // Fuerza de amortiguamiento

        return elasticForce + dampingForce;
    }

    private Map<String, Double> predict (Map<String, Double> params){
        Map<String, Double> predictedValues = new HashMap<>();
        predictedValues.put("r0", params.get("r0") + params.get("r1")*timestep + params.get("r2")*Math.pow(timestep,2)/2 + params.get("r3")*Math.pow(timestep,3)/6 + params.get("r4")*Math.pow(timestep,4)/24 + params.get("r5")*Math.pow(timestep,5)/120);
        predictedValues.put("r1", params.get("r1") + params.get("r2")*timestep + params.get("r3")*Math.pow(timestep,2)/2 + params.get("r4")*Math.pow(timestep,3)/6 + params.get("r5")*Math.pow(timestep,4)/24);
        predictedValues.put("r2", params.get("r2") + params.get("r3")*timestep + params.get("r4")*Math.pow(timestep,2)/2 + params.get("r5")*Math.pow(timestep,3)/6);
        predictedValues.put("r3", params.get("r3") + params.get("r4")*timestep + params.get("r5")*Math.pow(timestep,2)/2);
        predictedValues.put("r4", params.get("r4") + params.get("r5")*timestep);
        predictedValues.put("r5", params.get("r5"));
        return predictedValues;
    }

    private Map<String, Double> correct (Map<String, Double> predictedValues, double deltaR2){
        Map<String, Double> correctedValues = new HashMap<>();
        for (int i=0; i<6; i++){
            double corrected = predictedValues.get("r" + i) + alphas[i] * deltaR2 * (factorial(i) / Math.pow(timestep, i));
            correctedValues.put("r" + i, corrected);
        }
        return correctedValues;
    }
    /*
    for (int i = 0; i < 6; i++) {
        double value = 0;
        for (int j = i; j < 6; j++) {
            value += params.get("r" + j) * Math.pow(timestep, j-i) / factorial(j-i);
        }
        predictedValues.put("r" + i, value);
    }
     */

    private Map<String, Double> getParams(State initial){
        Map<String, Double> params = new HashMap<>();
        params.put("r0", initial.getParticle().getPosition());
        params.put("r1", initial.getParticle().getVelocity());
        // params.put("r2", ((-k/mass)*params.get("r0")));
        params.put("r2", (-k/mass)*params.get("r0") - (b/mass)*params.get("r1"));
        params.put("r3", (-(k/mass)*params.get("r1")));
        params.put("r4", ((-k/mass)*params.get("r2")));
        params.put("r5", ((-k/mass)*params.get("r3")));
        return params;
    }

    private int factorial(int n) {
        int factorial = 1;
        for (int i = 2; i <= n; ++i) {
            factorial *= i;
        }
        return factorial;
    }

}
