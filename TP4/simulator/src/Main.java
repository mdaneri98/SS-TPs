import damped_harmonic_oscillator.OscillatorSystem;

import java.io.IOException;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {


        OscillatorSystem os = new OscillatorSystem(100, 10e4, 70, 15, 0, 1000);

        os.analiticSolution(0.0001);



    }
}