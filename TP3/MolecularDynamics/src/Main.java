


public class Main {


    public static void main(String[] args) {
        double L = 0.1;
        double staticRadius = 0.005;
        int N = 10;
        double radius = 0.001;
        double velocity = 1;
        double mass = 1;
        double staticMass = Integer.MAX_VALUE;
        double dt = 0.01;

        MolecularDynamicSystem molecularDynamic = new MolecularDynamicSystem(N, L, dt);
        molecularDynamic.fixedSolution(velocity, mass, radius, staticRadius, staticMass, 5);
        

    }

}