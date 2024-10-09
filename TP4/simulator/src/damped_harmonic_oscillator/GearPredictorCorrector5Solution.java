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

    private final LinkedList<List<Double>> paramsList = new LinkedList<>();

    private final double[] alphas = new double[]{3.0/16, 251.0/360, 1, 11.0/18, 1.0/6, 1.0/60};

    public GearPredictorCorrector5Solution(double b, double k, double mass, double maxTime, double timestep, double initialAmplitud, State initialState, List<Double> params) {
        this.b = b;
        this.k = k;
        this.mass = mass;
        this.maxTime = maxTime;
        this.initialAmplitud = initialAmplitud;
        this.timestep = timestep;

        this.stateList = new LinkedList<>();
        stateList.add(initialState);
        paramsList.add(params);
    }

    @Override
    public boolean hasNext() {
        return stateList.peekLast().getTime() < this.maxTime;
    }

    @Override
    public State next() {
     State previousState =stateList.peekLast(); // Estado anterior
     double previousTime = previousState.getTime(); // Tiempo anterior
     Particle previousParticle = previousState.getParticle(); // Partícula anterior

     List<Double> previousParams = paramsList.peekLast(); // Parámetros anteriores

     List<Double> predictedValues = predict(previousParams,timestep); // Predicción de los valores

     double getDeltaR2 = getDeltaR2(b, k, mass, predictedValues.get(0),predictedValues.get(1),predictedValues.get(2),timestep); // Cálculo de deltaR2

     List<Double> correctedValues = correct(predictedValues,timestep, getDeltaR2); // Corrección de los valores

     paramsList.add(correctedValues); // Añadimos los valores corregidos a la lista de parámetros

     State newState = new State(previousTime + timestep, new Particle(previousParticle.getId(),correctedValues.get(0), correctedValues.get(1), mass));
     stateList.add(newState);
     return newState;
    }

    private double getDeltaR2(double b, double k, double mass, double predictedPos , double predictedVel, double predictedAc, double timestep) {
        double a = (-k/mass) * predictedPos - (b/mass) * predictedVel;
        return (a - predictedAc) * Math.pow(timestep,2)/2;
    }

    private double getForce(Particle p) {
        double position = p.getPosition();
        double velocity = p.getVelocity();

        // Oscilación amortiguada: F = -kx - bv
        double elasticForce = position * (-k);  // Fuerza de Hooke
        double dampingForce = velocity * (-b);  // Fuerza de amortiguamiento

        return elasticForce + dampingForce;
    }

    private List<Double> predict (List<Double> params,double time){
        List<Double> predictedValues = new ArrayList<>();
        predictedValues.add(0, params.get(0) + params.get(1)*time + params.get(2)*Math.pow(time,2)/2 + params.get(3)*Math.pow(time,3)/6 + params.get(4)*Math.pow(time,4)/24 + params.get(5)*Math.pow(time,5)/120);
        predictedValues.add(1, params.get(1) + params.get(2)*time + params.get(3)*Math.pow(time,2)/2 + params.get(4)*Math.pow(time,3)/6 + params.get(5)*Math.pow(time,4)/24);
        predictedValues.add(2, params.get(2) + params.get(3)*time + params.get(4)*Math.pow(time,2)/2 + params.get(5)*Math.pow(time,3)/6);
        predictedValues.add(3, params.get(3) + params.get(4)*time + params.get(5)*Math.pow(time,2)/2);
        predictedValues.add(4, params.get(4) + params.get(5)*time);
        predictedValues.add(5, params.get(5));
        return predictedValues;
    }

    private List<Double> correct (List<Double> predictedValues, double timestep, double deltaR2){
        List<Double> correctedValues = new ArrayList<>();
        for (int i=0; i<6; i++){
            correctedValues.add(i, predictedValues.get(i) + alphas[i]*deltaR2/Math.pow(timestep,i));
        }
        return correctedValues;
    }
}
