import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Main {


    public static void save(int N, int L, String directoryPath, Map<Integer, List<Particle>> particlesPerTime) {
        try {
            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String staticPath = Paths.get(directoryPath, "static").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                writer.write("" + L + "\n");
                writer.write("" + N + "\n");
                for (Particle particle : particlesPerTime.get(0)) {
                    writer.write(particle.getRadius() + "\t" + 1 + "\n");
                }
                System.out.println("Datos estáticos guardadas en el archivo: " + staticPath);
            }

            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String dynamicPath = Paths.get(directoryPath, "dynamic").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(dynamicPath))) {
                for (int t = 0; t < particlesPerTime.keySet().size(); t++) {
                    writer.write("" + t);
                    writer.newLine();

                    for (Particle particle : particlesPerTime.get(t)) {
                        writer.write(particle.getId() + "\t" + particle.getPosX() + "\t" + particle.getPosY() + "\t" + particle.getVel() + "\t" + particle.getAngle() );
                        writer.newLine();
                    }
                    System.out.println("Posiciones guardadas en el archivo: " + dynamicPath);
                }
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }
    }



    public static void main(String[] args) throws Exception {
        int M = 300;
        int N = 600;
        int L = 600;
        Map<Integer, List<Particle>> particlesPerTime;
        OffLattice offLattice = new OffLattice(M,N,L);
        particlesPerTime = offLattice.run(10000);

        // --- Save ---
        String projectPath = Paths.get("").toAbsolutePath().toString();
        Path directoryPath = Paths.get(projectPath, "test");

        Main.save(N, L, directoryPath.toString(), particlesPerTime);

    }
}