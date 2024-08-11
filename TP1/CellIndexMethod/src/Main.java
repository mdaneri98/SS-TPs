import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;



class ParticleLoader {

    public static List<Particle> loadParticlesFromFile(String filename, double radius) {
        List<Particle> particlesList = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("\t");
                if (parts.length == 3) {
                    int id = Integer.parseInt(parts[0]);
                    double posX = Double.parseDouble(parts[1]);
                    double posY = Double.parseDouble(parts[2]);

                    Particle particle = new Particle(id, posX, posY, radius);
                    particlesList.add(particle);
                }
            }
        } catch (IOException e) {
            System.err.println("Error leyendo el archivo: " + e.getMessage());
        }
        return particlesList;
    }
}

public class Main {
    public static void main(String[] args) {
        try {
            // Parámetros de ejemplo
            int L = 10; //   L: Longitud del lado de la grilla
            int M = 5; //       M: Número de celdas en una dimensión
            int N = 20; //      N: Número de partículas
            double interactionRadius = 1.5; // Radio de interacción entre partículas
            double particleRadius = 0.5; // Radio de las partículas

            List<Particle> particleList = ParticleLoader.loadParticlesFromFile("/Users/matiasdaneri/Documents/ITBA/4to/Simulación de Sistemas/SS-TPs/TP1/test/test_positions", particleRadius);

            // Crear una instancia de CIMImpl
            CIMImpl cim = new CIMImpl(M, N, L, interactionRadius, particleRadius, particleList);

            cim.run("./test");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}