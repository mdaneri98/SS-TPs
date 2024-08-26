import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
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

    public static void save(String directoryPath, Map<Integer, Double> orderPerTime) {
        try {
            // Crear la ruta para el archivo de orders dentro de la carpeta "test"
            String staticPath = Paths.get(directoryPath, "orders").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                for (Integer time : orderPerTime.keySet()) {
                    writer.write(time + "\t" + orderPerTime.get(time) + "\n");
                }
                System.out.println("Orders según t guardados en el archivo: " + staticPath);
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
                System.out.println("Orders según ruido guardados en el archivo: " + staticPath);
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


    public static void main(String[] args) throws Exception {

        int M = 1;
        int N = 100;
        int L = 5;
        int maxTime = 4001;

        List<Double> noises = new ArrayList<>();
        for (double i = 0; i <= 5; i += 0.25) {
            noises.add(i);
        }

        OffLattice offLattice = new OffLattice(M,N,L,noises.getFirst());
        Map<Integer, List<Particle>> particlesPerTime = offLattice.run(1, maxTime);
        Map<Integer, Double> orderPerTime = offLattice.orderPerTime(particlesPerTime);
        Map<Double, Double> ordersPerNoise = Main.getOrdersPerNoise(M, N, L, maxTime, noises);


        // --- Save ---
        String projectPath = Paths.get("").toAbsolutePath().toString();
        Path directoryPath = Paths.get(projectPath, "/test");

        Main.save(N, L, directoryPath.toString(), particlesPerTime);
        Main.save(directoryPath.toString(), orderPerTime);
        Main.saveOrdersPerNoise(directoryPath.toString(), ordersPerNoise);

    }
}