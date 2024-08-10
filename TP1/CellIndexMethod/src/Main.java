import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) {
        try {
            // Parámetros de ejemplo
            int matrixSize = 10; // M: Número de celdas en una dimensión
            int numParticles = 10; // N: Número de partículas
            int areaSize = 5*5; // L: Tamaño del área L x L
            double interactionRadius = 0.8; // Radio de interacción entre partículas
            double particleRadius = 0.5; // Radio de las partículas

            // Crear una lista vacía para las partículas
            List<Particle> particles = new ArrayList<>();

            // Crear una instancia de CIMImpl
            CIMImpl cim = new CIMImpl(matrixSize, numParticles, areaSize, interactionRadius, particleRadius, particles);

            cim.run("./test");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}