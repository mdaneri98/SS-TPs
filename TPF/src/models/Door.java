package models;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class Door {

    private int number;
    private Position initial;
    private Position end;
    private boolean isVertical;

    public Door(int number, Position initial, Position end) {
        this.number = number;
        this.initial = initial;
        this.end = end;

        isVertical = initial.getX() == end.getX();
    }

    public boolean isInside(Position position) {
        if (isVertical) {
            return position.getX() == initial.getX() &&
                    Math.min(initial.getY(), end.getY()) <= position.getY() &&
                    position.getY() <= Math.max(initial.getY(), end.getY());
        } else {
            return position.getY() == initial.getY() &&
                    Math.min(initial.getX(), end.getX()) <= position.getX() &&
                    position.getX() <= Math.max(initial.getX(), end.getX());
        }
    }

    public Position getCenter() {
        return new Position((initial.getX() + end.getX()) / 2,
                (initial.getY() + end.getY()) / 2);
    }

    public Position getClosestPosition(Position position) {
        double x = position.getX();
        double y = position.getY();

        if (isVertical) {
            // Para puerta vertical: X es fija, Y se ajusta entre los límites
            return new Position(
                    initial.getX(),
                    Math.max(initial.getY(), Math.min(end.getY(), y))
            );
        } else {
            // Para puerta horizontal: Y es fija, X se ajusta entre los límites
            return new Position(
                    Math.max(initial.getX(), Math.min(end.getX(), x)),
                    initial.getY()
            );
        }
    }

    public double distanceFrom(Position position) {
        return position.distanceTo(new Position(
                (initial.getX() + end.getX()) / 2,
                (initial.getY() + end.getY()) / 2
        ));
    }

    public double density(Set<Particle> particles) {
        // Get center point of the door
        Position center = new Position(
                (initial.getX() + end.getX()) / 2,
                (initial.getY() + end.getY()) / 2
        );

        // Calculate distances to all particles
        List<Double> distances = particles.stream()
                .map(particle -> center.distanceTo(particle.getPosition()))
                .sorted()
                .toList();

        // If we don't have enough particles, return 0
        if (distances.isEmpty()) {
            return 0.0;
        }

        // k will be all particles we have up to a maximum of 3
        int k = Math.min(3, distances.size());

        // Get the radius (distance to the k-th particle)
        double r_k = distances.get(k - 1);

        // Apply the formula: k / (π * r_k^2) / 2
        return k / (Math.PI * Math.pow(r_k, 2)) / 2;
    }

    public Position getInitial() {
        return initial;
    }

    public Position getEnd() {
        return end;
    }

    public int getNumber() {
        return number;
    }
}
