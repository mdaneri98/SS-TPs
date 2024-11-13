package models;

import models.particles.Particle;
import models.particles.StaticParticle;
import models.particles.Velocity;
import models.walls.Wall;
import models.walls.WallType;

public class Event {

    public static void applyCollision(Particle p1, Obstacle obstacle) {
        if (obstacle instanceof StaticParticle sp)
            applyCollision(p1, sp);
        else if (obstacle instanceof Particle p2)
            applyCollision(p1, p2);
        else if (obstacle instanceof Wall w)
            applyCollision(p1, w.getType());
    }

    public static void applyCollision_(Particle p1, Particle p2) {
        double deltaX = p2.getPosition().getX() - p1.getPosition().getX();
        double deltaY = p2.getPosition().getY() - p1.getPosition().getY();
        double sigma = p2.getRadius() + p1.getRadius();
        
        // Velocidades relativas
        double deltaVX = p2.getVelocity().getX() - p1.getVelocity().getX();
        double deltaVY = p2.getVelocity().getY() - p1.getVelocity().getY();
        
        // Producto escalar de velocidad relativa y posición relativa
        double deltas = deltaVX * deltaX + deltaVY * deltaY;
        
        // ¡IMPORTANTE! Solo aplicar el impulso si las partículas se están acercando
        if (deltas < 0) {  // Esta condición es clave
            double m1 = p1.getMass();
            double m2 = p2.getMass();
            
            double J = (2 * m1 * m2 * deltas) / (sigma * (m1 + m2));
            double Jx = (J * deltaX) / sigma;
            double Jy = (J * deltaY) / sigma;
            
            p1.setVelocity(new Velocity(
                p1.getVelocity().getX() + Jx / m1,
                p1.getVelocity().getY() + Jy / m1));
            
            p2.setVelocity(new Velocity(
                p2.getVelocity().getX() - Jx / m2,
                p2.getVelocity().getY() - Jy / m2));
        }
    }

    public static void applyCollision(Particle p1, StaticParticle p2) {
        double deltaX = p2.getPosition().getX() - p1.getPosition().getX();
        double deltaY = p2.getPosition().getY() - p1.getPosition().getY();
        double sigma = p2.getRadius() + p1.getRadius();
        
        double deltaVX = -p1.getVelocity().getX();
        double deltaVY = -p1.getVelocity().getY();
        
        double deltas = deltaVX * deltaX + deltaVY * deltaY;
        
        // Solo aplicar si la partícula se está acercando a la estática
        if (deltas < 0) {
            // Usar el enfoque simplificado para partícula estática
            double nx = deltaX / sigma;
            double ny = deltaY / sigma;
            
            double vn = p1.getVelocity().getX() * nx + p1.getVelocity().getY() * ny;
            
            p1.setVelocity(new Velocity(
                p1.getVelocity().getX() - 2 * vn * nx,
                p1.getVelocity().getY() - 2 * vn * ny
            ));
        }
    }

    public static void applyCollision(Particle p1, Particle p2) {
        // Calcular posiciones relativas
        double DeltaX = p1.getPosition().getX() - p2.getPosition().getX();
        double DeltaY = p1.getPosition().getY() - p2.getPosition().getY();

        double sigma = p1.getRadius() + p2.getRadius();
        double sin = DeltaY/sigma;
        double cos = DeltaX/sigma;

        double cn = 1;
        double ct = 1;

        // Velocidades de p1
        double[] velocity1 = {
            p1.getVelocity().getX(),
            p1.getVelocity().getY()
        };
        
        // Velocidades de p2
        double[] velocity2 = {
            p2.getVelocity().getX(),
            p2.getVelocity().getY()
        };

        // Coeficientes de la matriz de colisión
        double[] VelocityCoef = new double[4];
        VelocityCoef[0] = -cn * Math.pow(cos,2) + ct * Math.pow(sin,2);
        VelocityCoef[1] = -cn * cos * sin + ct * cos * sin;
        VelocityCoef[2] = -cn * cos * sin + ct * cos * sin;
        VelocityCoef[3] = -cn * Math.pow(sin,2) + ct * Math.pow(cos,2);

        // Nuevas velocidades para p1
        double[] newVelocity1 = new double[2];
        newVelocity1[0] = VelocityCoef[0] * velocity1[0] + VelocityCoef[1] * velocity1[1];
        newVelocity1[1] = VelocityCoef[2] * velocity1[0] + VelocityCoef[3] * velocity1[1];

        // Nuevas velocidades para p2 (usando la misma matriz pero con las velocidades de p2)
        double[] newVelocity2 = new double[2];
        newVelocity2[0] = VelocityCoef[0] * velocity2[0] + VelocityCoef[1] * velocity2[1];
        newVelocity2[1] = VelocityCoef[2] * velocity2[0] + VelocityCoef[3] * velocity2[1];

        // Actualizar velocidades
        p1.setVelocity(new Velocity(newVelocity1[0], newVelocity1[1]));
        p2.setVelocity(new Velocity(newVelocity2[0], newVelocity2[1]));
    }

    public static void applyCollision(Particle p1, WallType type) {
        Velocity newVelocity = switch (type) {
            case BOTTOM, TOP -> new Velocity(p1.getVelocity().getX(), -p1.getVelocity().getY());
            case RIGHT, LEFT -> new Velocity(-p1.getVelocity().getX(), p1.getVelocity().getY());
        };
        p1.setVelocity(newVelocity);
    }


}
