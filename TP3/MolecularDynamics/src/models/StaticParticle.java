package models;

public class StaticParticle extends Particle {

    public StaticParticle(int id, double posX, double posY, double velocity, double angle, double radius, double mass) {
        super(id, posX, posY, velocity, angle, radius, mass);
    }

    @Override
    public void update(Particle particle) {
        // Ángulo de la dirección relativa entre las partículas
        double deltaX = this.getPosX() - particle.getPosX();
        double deltaY = this.getPosY() - particle.getPosY();
        double angle = Math.atan2(deltaY, deltaX); // Ángulo entre las partículas

        // Obtener componentes de la velocidad de la partícula incidente
        double vX = particle.getVelocityX();
        double vY = particle.getVelocityY();

        // Coeficientes cn y ct
        double cn = -1;
        double ct = 1;

        // Aplicar la matriz de colisión (basado en la filmina)
        double newVX = (-cn * Math.pow(Math.cos(angle), 2) + ct * Math.pow(Math.sin(angle), 2)) * vX
                - (cn + ct) * Math.sin(angle) * Math.cos(angle) * vY;

        double newVY = (-(cn + ct) * Math.sin(angle) * Math.cos(angle)) * vX
                + (-cn * Math.pow(Math.sin(angle), 2) + ct * Math.pow(Math.cos(angle), 2)) * vY;

        // Actualizar la velocidad de la partícula incidente después de la colisión
        particle.setVelocity(Math.sqrt(newVX * newVX + newVY * newVY));
        particle.setAngle(Math.atan2(newVY, newVX));
    }


}
