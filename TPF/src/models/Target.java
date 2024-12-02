package models;

import java.util.Random;

public class Target {

    private Door door;
    private int doorNumber;
    private double secondsMustTry;
    private double secondsTrying;

    public Target(int doorNumber, double secondsMustTry) {
        this.doorNumber = doorNumber;
        this.secondsMustTry = secondsMustTry;

        door = Field.getInstance().getDoors().get(doorNumber);
    }

    public void step(double secondsElapsed) {
        secondsTrying -= secondsElapsed;
    }

    public boolean needsRecalculate() {
        return secondsTrying <= 0;
    }

    public void recalculate(double secondsElapsed, int bestPossibleDoorNumber) {
        if (secondsTrying <= 0) {
            secondsTrying = secondsMustTry;
            doorNumber = bestPossibleDoorNumber;
            door = Field.getInstance().getDoors().get(doorNumber);
        }
    }

    public Door getDoor() {
        return door;
    }

}
