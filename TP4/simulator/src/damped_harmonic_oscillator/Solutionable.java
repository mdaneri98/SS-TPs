package damped_harmonic_oscillator;

import damped_harmonic_oscillator.models.State;

import java.util.List;

public interface Solutionable {

    boolean hasNext();
    State next();

}
