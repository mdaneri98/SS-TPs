import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;



class ParticleLoader {

    public static List<Particle> loadParticlesFromFile(String filename, double radius) {
        List<Particle> particlesList = new ArrayList<>();
        try {
            // Obtener la ruta relativa al directorio del proyecto
            String projectPath = Paths.get("").toAbsolutePath().toString();

            // Crear la ruta para el archivo relativo a la raíz del proyecto
            String filePath = Paths.get(projectPath, filename).toString();

            try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
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
            }
        } catch (IOException e) {
            System.err.println("Error leyendo el archivo: " + e.getMessage());
        }
        return particlesList;
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

                List<Particle> particleList = ParticleLoader.loadParticlesFromFile("test/test_positions", particleRadius);

                // Crear una instancia de CIMImpl
                CIMImpl cim = new CIMImpl(M, N, L, interactionRadius, particleRadius, null);

                cim.run("./test");

            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}