

public class Particle {

    private int id;
    private double posX;
    private double posY;
    private double radius;

    private double vel;

    private double angle;


    public Particle(int id, double posX, double posY, double radius, double vel, double angle) {
        this.id = id;
        this.posX = posX;
        this.posY = posY;
        this.radius = radius;
        this.vel = vel;
        this.angle = angle;
    }

    public boolean isInside(Particle other) {
        // Calcular la distancia entre los centros de las partículas
        double distance = Math.sqrt(Math.pow(other.posX - this.posX, 2) + Math.pow(other.posY - this.posY, 2));

        // Verificar si la partícula actual está completamente dentro de la otra
        return distance + this.radius <= other.radius;
    }

    public void setXY(double x, double y) {
        this.setPosX(x);
        this.setPosY(y);
    }

    public double getVel() {
        return vel;
    }

    public double getAngle() {
        return angle;
    }

    public void setAngle(double angle) {
        this.angle = angle;
    }

    public boolean isPartiallyInside(Particle p2) {
        // Calcula la distancia entre los centros de las circunferencias
        double distance = Math.sqrt(Math.pow(p2.getPosX() - this.getPosX(), 2) + Math.pow(p2.getPosY() - this.getPosY(), 2));

        // Verifica si la circunferencia 2 está parcialmente dentro de la circunferencia 1
        return distance - this.getRadius() - p2.getRadius() <= 0;
    }


    @Override
    public String toString() {
        return "Particle(x: %f, y: %f, r: %f)".formatted(posX, posY, radius);
    }

    public int getId() {
        return id;
    }

    public double getPosX() {
        return posX;
    }

    public void setPosX(double posX) {
        this.posX = posX;
    }

    public double getPosY() {
        return posY;
    }

    public void setPosY(double posY) {
        this.posY = posY;
    }

    public double getRadius() {
        return radius;
    }

    public void setRadius(double radius) {
        this.radius = radius;
    }

}

