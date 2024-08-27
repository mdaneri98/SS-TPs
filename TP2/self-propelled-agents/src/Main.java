import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

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
                }
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }
    }

    public static void save(String directoryPath, Map<Integer, Double> orderPerTime) {
        try {
            // Crear la ruta para el archivo de orders dentro de la carpeta "test"
            String staticPath = Paths.get(directoryPath, "orders").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                for (Integer time : orderPerTime.keySet()) {
                    writer.write(time + "\t" + orderPerTime.get(time) + "\n");
                }
            }
        } catch (Exception e) {
            System.err.println("Error al guardar el archivo orders: " + e.getMessage());
        }
    }

    public static void saveOrdersPerNoise(String directoryPath, Map<Double, Double> ordersPerNoise) {
        try {
            // Crear la ruta para el archivo de orders dentro de la carpeta "test"
            String staticPath = Paths.get(directoryPath, "orders_per_noise").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                for (Double noise : ordersPerNoise.keySet()) {
                    writer.write(noise + "\t" + ordersPerNoise.get(noise) + "\n");
                }
            }
        } catch (Exception e) {
            System.err.println("Error al guardar el archivo orders per noise: " + e.getMessage());
        }
    }

    public static Map<Double, Double> getOrdersPerNoise(int M, int N, int L, int maxTime, List<Double> noises) throws Exception {
        Map<Double, Double> ordersPerNoise = new TreeMap<>();
        for (double noise : noises) {
            OffLattice offLattice = new OffLattice(M,N,L,noise);
            Map<Integer, List<Particle>> particlesPerTime = offLattice.run(1, maxTime);
            Map<Integer, Double> orderPerTime = offLattice.orderPerTime(particlesPerTime);
            double prom = 0;
            for (Integer time : orderPerTime.keySet()) {
                prom += orderPerTime.get(time);
            }
            prom /= orderPerTime.keySet().size();
            ordersPerNoise.put(noise, prom);
        }
        return ordersPerNoise;
    }

    private static List<Particle> getParticles1(int L) {
        List<Particle> particles = new ArrayList<>();
        double velocity = 0.03;

        particles.add(new Particle(0, 0, 0, 0,velocity,Math.toRadians(45)));
        particles.add(new Particle(1, L /2.0, L/2.0, 0,velocity,Math.toRadians(135)));

        particles.add(new Particle(2, L/2.0, 0, 0,velocity,Math.toRadians(0)));
        particles.add(new Particle(3, L /2.0, 0, 0,velocity,Math.toRadians(180)));

        return particles;
    }

    public static void main(String[] args) throws Exception {
        int M = 2;
        int N = 40;
        int L = 7;
        int maxTime = 400;

        List<Double> noises = new ArrayList<>();
        for (double i = 0; i <= 5; i += 0.05) {
            noises.add(i);
        }

        int[] ms = new int[] { 1, 1, 4, 15, 25 };
        int[] ns = new int[] { 40, 100, 400, 4000, 10000 };
        int[] ls = new int[] { 3, 5, 10, 32, 50 };

        for (int i = 0; i < ms.length; i++) {
            for (int j = 0; j < noises.size(); j++) {
                OffLattice offLattice = new OffLattice(ms[i], ns[i], ls[i], noises.get(j));
                Map<Integer, List<Particle>> particlesPerTime = offLattice.run(1, maxTime);

                Map<Integer, Double> orderPerTime = offLattice.orderPerTime(particlesPerTime);
                Map<Double, Double> ordersPerNoise = Main.getOrdersPerNoise(ms[i], ns[i], ls[i], maxTime, noises);

                // --- Save ---
                String projectPath = Paths.get("").toAbsolutePath().toString();
                Path directoryPath = Paths.get(projectPath, String.format("/test/outputs/N%dL%d_n%.2f", ns[i], ls[i], noises.get(j)));

                // Crea los directorios si no existen
                Files.createDirectories(directoryPath);


                Main.save(offLattice.getN(), ls[i], directoryPath.toString(), particlesPerTime);
                Main.save(directoryPath.toString(), orderPerTime);
                Main.saveOrdersPerNoise(directoryPath.toString(), ordersPerNoise);
            }
        }
    }
}