import damped_harmonic_oscillator.OscillatorSystem;
import forced_oscillator.CoupledOscillatorSystem;

import java.util.LinkedList;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {
        double t2 = 5;

        OscillatorSystem os = new OscillatorSystem(100, 1e4, 70, 5,  1);

        double[] timesteps = new double[]{0.010000, 0.001000, 0.000100, 0.000010, 0.000001};
        for (Double timestep : timesteps) {
            //os.analiticSolution(timestep, t2);
            //os.verletSolution(timestep, t2);
            //os.beemanSolution(timestep, t2);
            //os.gearPredictorCorrectorOrder5Solution(timestep, t2);
        }

        double[] ks = new double[] { 10*10, 20*20, 30*30, 40*40, 50*50 };
        int[] wfs = new int[] { 10, 20, 30, 40, 50 };
        //double[] ks = new double[] { 50*50 };
        //int[] wfs = new int[] { 50 };
        for (int i = 0; i < ks.length; i++) {
            CoupledOscillatorSystem cos = new CoupledOscillatorSystem(101, ks[i], 0.001, 15, 1e-3, 1e-2);
            for (int j = -10; j <= 10; j++) {
                cos.verletSolution(wfs[i] + j, t2);
            }
        }
    }

}