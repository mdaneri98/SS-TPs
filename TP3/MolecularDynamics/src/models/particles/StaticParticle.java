package models.particles;

import java.util.ArrayList;
import java.util.List;

public class StaticParticle extends Particle {

	private static final List<Integer> collisionCount = new ArrayList<>();
	
    public StaticParticle(int id, Position position, double radius, double mass) {
        super(id, position, new Velocity(0,0), radius, mass);
    }

    @Override
    public StaticParticle clone() {
        return new StaticParticle(getId(), new Position(getPosition().getX(),getPosition().getY()), getRadius(), getMass());
    }

    public Double getMomentum(Particle particle) {
        // Diferencia de posición entre la pared y la partícula
        double deltaX = this.getPosition().getX() - particle.getPosition().getX();
        double deltaY = this.getPosition().getY() - particle.getPosition().getY();

        // Ángulo de la línea que conecta los centros de las partículas
        double normalAngle = Math.atan2(deltaY, deltaX);

        // Componentes de la velocidad tangencial
        double vX = particle.getVelocity().getX();
        double vY = particle.getVelocity().getY();

        // Velocidades tangencial y normal
        double velocityNormal = vX * Math.cos(normalAngle) + vY * Math.sin(normalAngle);
        double velocityTangential = -vX * Math.sin(normalAngle) + vY * Math.cos(normalAngle);

        // Incrementamos el momento usando la componente tangencial
        return 2 * particle.getMass() * Math.abs(velocityTangential);
    }
    
    public List<Integer> collisionCount() {
    	return collisionCount;
    }

}
