import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) {
        try {
            // Parámetros de ejemplo
            int matrixSize = 10; // Número de celdas en una dimensión
            int numParticles = 100; // Número de partículas
            int areaSize = 40; // Tamaño del área L x L
            double interactionRadius = 3.0; // Radio de interacción entre partículas
            double particleRadius = 0.4; // Radio de las partículas

            // Crear una lista vacía para las partículas
            List<Particle> particles = new ArrayList<>();

            // Crear una instancia de CIMImpl
            CIMImpl cim = new CIMImpl(matrixSize, numParticles, areaSize, interactionRadius, particleRadius, particles);

            cim.run("ejemplo.txt");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}