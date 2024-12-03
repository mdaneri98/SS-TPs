package models;

import java.util.Random;

public class Target {

    private Door door;
    private int doorNumber;
    private double secondsMustTry;
    private double secondsTrying;

    private boolean isFirst;

    public Target(int doorNumber, double secondsMustTry) {
        this.doorNumber = doorNumber;
        this.secondsMustTry = secondsMustTry;
        this.isFirst = true;
        door = Field.getInstance().getDoors().get(doorNumber);
    }

    public void step(double secondsElapsed) {
        secondsTrying -= secondsElapsed;
    }

    public boolean needsChange() {
        return secondsTrying <= 0 || isFirst;
    }

    public void change(int bestPossibleDoorNumber) {
        isFirst = false;
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
