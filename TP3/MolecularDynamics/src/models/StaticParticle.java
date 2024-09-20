package models;

import java.util.ArrayList;
import java.util.List;

public class StaticParticle extends Particle {

    private int index;

    public StaticParticle(int id, double posX, double posY, double velocity, double angle, double radius, double mass) {
        super(id, posX, posY, velocity, angle, radius, mass);
    }

    public Double getMomentum(Particle particle) {
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
        return 2 * particle.getMass() * Math.abs(velocityTangential);
    }

}
