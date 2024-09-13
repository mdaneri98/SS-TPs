package models;

import java.util.ArrayList;
import java.util.List;

public class StaticParticle extends Particle implements Pressurable {

    private int index;
    private List<Double> momentums;


    public StaticParticle(int id, double posX, double posY, double velocity, double angle, double radius, double mass) {
        super(id, posX, posY, velocity, angle, radius, mass);
        this.momentums = new ArrayList<>();
        this.index = 0;
        this.momentums.addFirst(0.0);
    }

    @Override
    public Particle applyCollision(final Particle particle) {
        // Ángulo de la dirección relativa entre las partículas
        double deltaX = this.getPosX() - particle.getPosX();
        double deltaY = this.getPosY() - particle.getPosY();
        double angle = Math.atan2(deltaY, deltaX); // Ángulo entre las partículas

        // Obtener componentes de la velocidad de la partícula incidente
        double vX = particle.getVelX();
        double vY = particle.getVelY();

        // Coeficientes cn y ct
        double cn = -1;
        double ct = 1;

        double sin = Math.abs(this.getPosY() - particle.getPosY()) / (this.getRadius() + particle.getRadius());
        double cos = Math.abs(this.getPosX() - particle.getPosX()) / (this.getRadius() + particle.getRadius());

        // Aplicar la matriz de colisión (basado en la filmina)
/*        double newVX = (-cn * Math.pow(Math.cos(angle), 2) + ct * Math.pow(Math.sin(angle), 2)) * vX
                - (cn + ct) * Math.sin(angle) * Math.cos(angle) * vY;

        double newVY = (-(cn + ct) * Math.sin(angle) * Math.cos(angle)) * vX
                + (-cn * Math.pow(Math.sin(angle), 2) + ct * Math.pow(Math.cos(angle), 2)) * vY;*/

        double newVX = (-cn * Math.pow(cos, 2) + ct * Math.pow(sin, 2)) * vX
                - (cn + ct) * sin * cos * vY;

        double newVY = (-(cn + ct) * sin * cos) * vX
                + (-cn * Math.pow(sin, 2) + ct * Math.pow(cos, 2)) * vY;

        Particle newParticle = new Particle(particle.getId(), particle.getPosX(), particle.getPosY(), newVX, newVY, particle.getRadius(), particle.getMass());

        // Actualizar la velocidad de la partícula incidente después de la colisión
        //newParticle.setAngle(Math.atan2(newVY, newVX));

        //Incrementamos momento
        this.incrementMomentum(particle);

        return newParticle;
    }

    @Override
    public void incrementMomentum(Particle particle) {
        // Diferencia de posición entre la pared y la partícula
        double deltaX = this.getPosX() - particle.getPosX();
        double deltaY = this.getPosY() - particle.getPosY();

        // Ángulo de la línea que conecta los centros de las partículas
        double normalAngle = Math.atan2(deltaY, deltaX);

        // Componentes de la velocidad tangencial
        double vX = particle.getVelX();
        double vY = particle.getVelY();

        // Velocidades tangencial y normal
        double velocityNormal = vX * Math.cos(normalAngle) + vY * Math.sin(normalAngle);
        double velocityTangential = -vX * Math.sin(normalAngle) + vY * Math.cos(normalAngle);

        // Incrementamos el momento usando la componente tangencial
        double newMomentum = this.momentums.get(index) + 2 * particle.getMass() * Math.abs(velocityTangential);
        this.momentums.set(index, newMomentum);
    }

    @Override
    public List<Double> getMomentum() {
        return this.momentums;
    }

    @Override
    public void newInterval() {
        this.index += 1;
        this.momentums.add(index, 0.0);
    }

}
