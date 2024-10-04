import damped_harmonic_oscillator.OscillatorSystem;
import forced_oscillator.CoupledOscillatorSystem;

import java.util.LinkedList;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {


        OscillatorSystem os = new OscillatorSystem(100, 10e4, 70, 5,  1);

        double[] timesteps = new double[]{0.00001, 0.00001, 0.0001, 0.001, 0.01, 0.1};
        for (Double timestep : timesteps) {
          //  os.analiticSolution(timestep);
          //  os.verletSolution(timestep);
          //  os.beemanSolution(timestep);
        }

        CoupledOscillatorSystem cos = new CoupledOscillatorSystem(100, 100, 0.001, 60, 10e-3, 10e-2);
        cos.verletSolution(10, 10e-3);
        double[] wfs = new double[15];
        for (int i = 5; i < wfs.length; i++) {
            wfs[i] = i;
            //cos.verletSolution(wfs[i],10e-3);
        }


    }
}