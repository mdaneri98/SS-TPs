package models;

public class StaticParticle extends Particle {

    public StaticParticle(int id, double posX, double posY, double velocity, double angle, double radius, double mass) {
        super(id, posX, posY, velocity, angle, radius, mass);
    }

    @Override
    public Particle applyCollision(final Particle particle) {
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

        Particle newParticle = new Particle(particle.getId(), particle.getPosX(), particle.getPosY(), particle.getVelocity(), particle.getAngle(), particle.getRadius(), particle.getMass());

        // Actualizar la velocidad de la partícula incidente después de la colisión
        newParticle.setVelocity(Math.sqrt(newVX * newVX + newVY * newVY));
        newParticle.setAngle(Math.atan2(newVY, newVX));

        return newParticle;
    }


}
