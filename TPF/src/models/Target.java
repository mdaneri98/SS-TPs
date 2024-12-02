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

    public void addSecondsElapsed(double secondsElapsed) {
        this.secondsTrying -= secondsElapsed;

        if (secondsTrying <= 0) {
            secondsTrying = secondsMustTry;
            lookForAnotherDoor();
        }
    }

    private void lookForAnotherDoor() {
        Random random = new Random();
        doorNumber = random.nextInt(3);
        door = Field.getInstance().getDoors().get(doorNumber);
        secondsTrying = secondsMustTry;
    }

    public Door getDoor() {
        return door;
    }

}
