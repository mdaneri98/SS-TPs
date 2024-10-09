import damped_harmonic_oscillator.OscillatorSystem;
import forced_oscillator.CoupledOscillatorSystem;

import java.util.LinkedList;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {


        OscillatorSystem os = new OscillatorSystem(100, 1e4, 70, 5,  1);

/*        double[] timesteps = new double[]{1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1};
        for (Double timestep : timesteps) {
            os.analiticSolution(timestep);
            os.verletSolution(timestep);
            os.beemanSolution(timestep);
        }*/

/*        CoupledOscillatorSystem cos = new CoupledOscillatorSystem(100, 100, 0.001, 60, 1e-3, 1e-2);
        cos.verletSolution(10, 1e-3);
        double[] wfs = new double[15];
        for (int i = 5; i < wfs.length; i++) {
            wfs[i] = i;
            cos.verletSolution(wfs[i],1e-3);
        }*/
        os.analiticSolution(1e-3);
        os.gearPredictorCorrectorOrder5Solution(1e-3);
        //os.verletSolution(1e-3);

    }
}