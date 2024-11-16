


public class Main {


    public static void main(String[] args) {
        double L = 0.1;
        double staticRadius = 0.005;
        int N = 50;
        double radius = 0.001;
        double velocity = 1;
        double mass = 1;
        double staticMass = Integer.MAX_VALUE;
        double dt = 0.01;

        MolecularDynamicSystem molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.fixedSolution(velocity, mass, radius, staticRadius, 10);
        
        // === Ej. 1.2 ===
        
        velocity = 3.6;
        molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.fixedSolution(velocity, mass, radius, staticRadius, 10);
        
        velocity = 10;
        molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.fixedSolution(velocity, mass, radius, staticRadius, 10);

        // === Ej 1.4 ===

        velocity = 1;
        staticMass = 3;
        molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.commonSolution(velocity, mass, radius, staticRadius, staticMass, 10);



    }

}