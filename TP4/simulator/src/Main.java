import damped_harmonic_oscillator.OscillatorSystem;
import forced_oscillator.CoupledOscillatorSystem;

import java.util.LinkedList;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {
        double t2 = 5;

        OscillatorSystem os = new OscillatorSystem(100, 1e4, 70, 5,  1);

        double[] timesteps = new double[]{1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1};
        for (Double timestep : timesteps) {
            //os.analiticSolution(timestep, t2);
            //os.verletSolution(timestep, t2);
            //os.beemanSolution(timestep, t2);
            //os.gearPredictorCorrectorOrder5Solution(timestep, t2);
        }

        double[] ks = new double[] { 10*10, 20*20, 30*30, 40*40, 50*50 };
        for (Double k : ks) {
            CoupledOscillatorSystem cos = new CoupledOscillatorSystem(101, k, 0.001, 30, 1e-3, 1e-2);
            double[] wfs = new double[16];
            for (int i = 5; i < wfs.length; i += 1) {
                wfs[i] = i;
                cos.verletSolution(wfs[i], t2);
            }
        }
    }

}