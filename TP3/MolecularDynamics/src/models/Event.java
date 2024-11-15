package models;

import models.particles.Particle;
import models.particles.StaticParticle;
import models.particles.Velocity;
import models.walls.Wall;
import models.walls.WallType;

public class Event {

	private static final boolean DEBUG_MODE = false; // Variable para controlar los logs

	private static void log(String message, Object... args) {
		if (DEBUG_MODE) {
			System.out.printf(message, args);
		}
	}

	public static void applyCollision(Particle p1, Obstacle obstacle) {
		log("\n=== Collision Debug ===\n");
		log("Particle p1 (ID: %d) colliding with %s%n", p1.getId(), obstacle.getClass().getSimpleName());
		log("P1 before - Pos: (%.6f, %.6f), Vel: (%.6f, %.6f)%n", p1.getPosition().getX(), p1.getPosition().getY(),
				p1.getVelocity().getX(), p1.getVelocity().getY());

		if (obstacle instanceof StaticParticle sp) {
			applyCollision(p1, sp);
		} else if (obstacle instanceof Particle p2) {
			applyCollision(p1, p2);
		} else if (obstacle instanceof Wall w)
			applyCollision(p1, w.getType());

		log("P1 after - Pos: (%.6f, %.6f), Vel: (%.6f, %.6f)%n", p1.getPosition().getX(), p1.getPosition().getY(),
				p1.getVelocity().getX(), p1.getVelocity().getY());
	}

	public static void applyCollision(Particle p1, Particle p2) {
		System.out.printf("=== BEFORE === %n");
		System.out.printf("%d(%.2f) -> %d(%.2f) %n", p1.getId(), p1.getMass(), p2.getId(), p2.getMass());
		System.out.printf("P%d: %.6f %n", p1.getId(),
				Math.sqrt(Math.pow(p1.getVelocity().getX(), 2) + Math.pow(p1.getVelocity().getY(), 2)));
		System.out.printf("P%d: %.6f %n", p2.getId(),
				Math.sqrt(Math.pow(p2.getVelocity().getX(), 2) + Math.pow(p2.getVelocity().getY(), 2)));		
		
		// Calcular Δr y Δv
		double deltaX = p2.getPosition().getX() - p1.getPosition().getX();
		double deltaY = p2.getPosition().getY() - p1.getPosition().getY();
		double deltaVx = p2.getVelocity().getX() - p1.getVelocity().getX();
		double deltaVy = p2.getVelocity().getY() - p1.getVelocity().getY();

		// Calcular productos escalares
		double deltaVdeltaR = deltaVx * deltaX + deltaVy * deltaY; // Δv·Δr

		// Calcular σ (sigma)
		double sigma = p1.getRadius() + p2.getRadius();

		// Calcular J
		double J = (2 * p1.getMass() * p2.getMass() * deltaVdeltaR) / (sigma * (p1.getMass() + p2.getMass()));
		double Jx = (J * deltaX) / sigma;
		double Jy = (J * deltaY) / sigma;

		// Actualizar velocidades
		p1.setVelocity(
				new Velocity(p1.getVelocity().getX() + Jx / p1.getMass(), p1.getVelocity().getY() + Jy / p1.getMass()));

		p2.setVelocity(
				new Velocity(p2.getVelocity().getX() - Jx / p2.getMass(), p2.getVelocity().getY() - Jy / p2.getMass()));

		System.out.printf("=== AFTER === %n");
		System.out.printf("P%d: %.6f %n", p1.getId(),
				Math.sqrt(Math.pow(p1.getVelocity().getX(), 2) + Math.pow(p1.getVelocity().getY(), 2)));
		System.out.printf("P%d: %.6f %n", p2.getId(),
				Math.sqrt(Math.pow(p2.getVelocity().getX(), 2) + Math.pow(p2.getVelocity().getY(), 2)));
	}

	public static void applyCollision(Particle p1, WallType type) {
		Velocity newVelocity = switch (type) {
		case BOTTOM, TOP -> new Velocity(p1.getVelocity().getX(), -p1.getVelocity().getY());
		case RIGHT, LEFT -> new Velocity(-p1.getVelocity().getX(), p1.getVelocity().getY());
		};
		p1.setVelocity(newVelocity);
	}

}
