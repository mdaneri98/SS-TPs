package models.particles;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class StaticParticle extends Particle {

	private static final List<Integer> collisionCount = new ArrayList<>();
	private static final List<Double> momentumCount = new ArrayList<>();

    private static final List<Integer> uniqueCollisionCount = new ArrayList<>();
    private static final Set<Integer> collidedParticles = new HashSet<>();

    public StaticParticle(int id, Position position, Velocity velocity, double radius, double mass) {
        super(id, position, velocity, radius, mass);
    }

    @Override
    public StaticParticle clone() {
        return new StaticParticle(getId(), new Position(getPosition().getX(),getPosition().getY()), new Velocity(getVelocity().getX(), getVelocity().getY()), getRadius(), getMass());
    }


    public List<Integer> collisionCount() {
    	return collisionCount;
    }

    public List<Integer> uniqueCollisionCount() {
        return uniqueCollisionCount;
    }
    
    public List<Double> momentumCount() {
    	return momentumCount;
    }

    public Set<Integer> getCollidedParticles() {
        return collidedParticles;
    }
}
