import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;






public class Main {


    public static Map<Integer, List<Particle>> findInteractionsBruteForce(double rc, List<Particle> particles) {
        Map<Integer, List<Particle>> interactions = new HashMap<>();

        for (Particle p1 : particles) {
            for (Particle p2 : particles) {
                if (p1 != p2) {
                    double dx = p1.getPosX() - p2.getPosX();
                    double dy = p1.getPosY() - p2.getPosY();
                    double centerDistance = Math.sqrt(dx * dx + dy * dy);

                    // Si el borde está dentro de rc => Verdadero.
                    double distance = centerDistance - p1.getRadius() - p2.getRadius();
                    if ( distance <= 0 || distance <= (rc - p1.getRadius()) ) {
                        interactions.putIfAbsent(p1.getId(), new ArrayList<>());
                        interactions.get(p1.getId()).add(p2);

                        // Se puede optimizar si no volvemos a recorrer las particulas que ya agregamos de p2.
                        interactions.putIfAbsent(p2.getId(), new ArrayList<>());
                        interactions.get(p2.getId()).add(p1);
                    }
                }
            }
        }
        return interactions;
    }

    private static List<Long> iterate_over_m(int N, int L, double pRadius, double rc) throws Exception {
        List<Long> times = new ArrayList<>();

        for (int M = 1; (double)(L/M) > rc + 2*pRadius; M++) {
            CIMImpl cim = new CIMImpl(M, N, L, pRadius, null);

            long start = System.currentTimeMillis();
            Map<Integer, List<Particle>> interactions = cim.findInteractions(rc, true);
            long finish = System.currentTimeMillis();

            // Obtener la ruta relativa al directorio del proyecto
            String projectPath = Paths.get("").toAbsolutePath().toString();
            Path directoryPath = Paths.get(projectPath, "test", "M" + M);
            Files.createDirectories(directoryPath);

            cim.save(directoryPath.toString(), interactions);

            times.add(finish-start);
        }
        return times;
    }

    private static void save_times(String directoryPath, List<Long> times) {
        // Crear la ruta para el archivo de tiempos dentro de la carpeta directoryPath.
        String timesPath = Paths.get(directoryPath, "times").toString();
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(timesPath))) {
            // M    time
            int m = 1;
            for (Long time : times) {
                writer.write(m + "\t" + time);
                writer.newLine();
                m++;
            }
            System.out.println("Tiempos guardados en el archivo: " + timesPath);
        } catch (Exception e) {
            System.out.println("Error escribiendo los tiempos. \n" + e.getMessage());
        }
    }

    public static void main(String[] args) {
        try {

            double rc = 20;
            int L = 100;
            int N = 1000;
            double pRadius = 2;

            // target =  81  => 781 verde pero debería ser gris

            /*
            int M = 3;
            CIMConfig config = CIMConfig.loadFromFile("/Users/matiasdaneri/Documents/ITBA/4to/Simulación de Sistemas/SS-TPs/TP1/test/M%d/static".formatted(M), "/Users/matiasdaneri/Documents/ITBA/4to/Simulación de Sistemas/SS-TPs/TP1/test/M%d/dynamic".formatted(M));
            System.out.println("Configuración utilizada: " + config);

            CIMImpl cim = new CIMImpl(M, config.getN(), config.getL(), config.getMaxParticleRadius(), config.getParticleList());
            Map<Integer, List<Particle>> interactions = cim.findInteractions(rc, true);
*/
            
            List<Long> times = Main.iterate_over_m(N, L, pRadius, rc);

            // Obtener la ruta relativa al directorio del proyecto
            String projectPath = Paths.get("").toAbsolutePath().toString();
            Path directoryPath = Paths.get(projectPath, "test");
            save_times(directoryPath.toString(), times);


        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}