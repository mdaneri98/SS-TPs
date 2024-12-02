package models;

public class Door {

    private Position initial;
    private Position end;
    private boolean isVertical;

    public Door(Position initial, Position end) {
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

    public Position getInitial() {
        return initial;
    }

    public Position getEnd() {
        return end;
    }
}
