import models.particles.StaticParticle;

public class Main {


    public static void main(String[] args) {
        double L = 0.1;
        double staticRadius = 0.005;
        int N = 200;
        double radius = 0.001;
        double velocity = 1;
        double mass = 1;
        double staticMass;
        double dt = 0.05;

        int time = 10;

        MolecularDynamicSystem molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.fixedSolution(velocity, mass, radius, staticRadius, time);
        
        // === Ej. 1.2 ===
        
        velocity = 3;
        molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.fixedSolution(velocity, mass, radius, staticRadius, time);

        velocity = 6;
        molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.fixedSolution(velocity, mass, radius, staticRadius, time);
        
        velocity = 10;
        molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.fixedSolution(velocity, mass, radius, staticRadius, time);

        // === Ej 1.4 ===

        velocity = 1;
        staticMass = 3;
        molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.commonSolution(velocity, mass, radius, staticRadius, staticMass, time);



    }

}