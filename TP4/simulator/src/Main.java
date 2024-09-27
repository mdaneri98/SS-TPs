import damped_harmonic_oscillator.OscillatorSystem;
import forced_oscillator.CoupledOscillatorSystem;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {

/*
        OscillatorSystem os = new OscillatorSystem(100, 10e4, 70, 5,  1);

        os.analiticSolution(0.001);
        os.verletSolution(0.001);
        os.beemanSolution(0.001);
*/
        CoupledOscillatorSystem cos = new CoupledOscillatorSystem(1000, 100, 100, 1, 10, 10e-3, 10e-2);

        cos.verletSolution(10e-2);

    }
}