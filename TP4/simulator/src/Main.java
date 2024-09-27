import damped_harmonic_oscillator.OscillatorSystem;
import damped_harmonic_oscillator.coupled_oscillators.CoupledOscillatorSystem;

import java.io.IOException;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {


        OscillatorSystem os = new OscillatorSystem(100, 10e4, 70, 5,  1);

        os.analiticSolution(0.001);
        os.verletSolution(0.001);
        os.beemanSolution(0.001);

       // CoupledOscillatorSystem cos = new CoupledOscillatorSystem(10, 100, 10e4, 70, 10, 10);

        //cos.analiticSolution(0.001);

    }
}