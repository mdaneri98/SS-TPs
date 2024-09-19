//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.

import models.*;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

public class Main {

    public static Set<Particle> loadFromFile(String filePathStatic, String fileDynamicPath) {
        List<Particle> particlesList = new ArrayList<>();
        int N = 0;
        double L = 0;

        try {
            BufferedReader br = new BufferedReader(new FileReader(filePathStatic));
            String linea;

            // Leer las primeras 3 líneas y guardarlas en variables especiales
            L = Double.parseDouble(br.readLine().trim());
            N = Integer.parseInt(br.readLine().trim());

            // Leer y retornar solo el primer valor de cada par de valores
            int i = 0;
            while ((linea = br.readLine()) != null) {
                String[] valores = linea.trim().split("\t");
                double radius = Double.parseDouble(valores[0]);
                double mass = Double.parseDouble(valores[0]);

                Particle particle = new Particle(i, 0 , 0 , 0, 0, radius, mass);
                particlesList.add(particle);
                i++;
            }

            br.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        try (BufferedReader reader = new BufferedReader(new FileReader(fileDynamicPath))) {
            //Salteamos la primer linea.
            reader.readLine();
            int i = 0;
            String line;
            while ((line = reader.readLine()) != null && i < N) {
                String[] parts = line.trim().split("\t");

                int idx = Integer.parseInt(parts[0]);
                double posX = Double.parseDouble(parts[1]);
                double posY = Double.parseDouble(parts[2]);
                double velX = Double.parseDouble(parts[3]);
                double velY = Double.parseDouble(parts[4]);

                Particle p = particlesList.get(idx);
                p.setPosX(posX);
                p.setPosY(posY);
                p.setVelX(velX);
                p.setVelY(velY);
                i++;
            }
        } catch (IOException e) {
            System.err.println("Error leyendo el archivo: " + e.getMessage());
        }

        return new HashSet<>(particlesList);
    }

    public static void save(int N, double L, String directoryPath, Map<Integer, State> states) {
        try {
            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String staticPath = Paths.get(directoryPath, "static.txt").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                writer.write("" + L + "\n");
                writer.write("" + N + "\n");
                for (Particle particle : states.get(0).getParticles()) {
                    writer.write(particle.getRadius() + "\t" + particle.getMass() + "\t" + 1 + "\n");
                }
            }

            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String dynamicPath = Paths.get(directoryPath, "dynamic.txt").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(dynamicPath))) {
                for (Integer index : states.keySet()) {
                    writer.write("" + states.get(index).getTime());
                    writer.newLine();

                    for (Particle particle : states.get(index).getParticles()) {
                        writer.write(particle.getId() + "\t" + particle.getPosX() + "\t" + particle.getPosY() + "\t" + particle.getVelX() + "\t" + particle.getVelY());
                        writer.newLine();
                    }
                }
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }
    }

    public static Map<Double, Double> calculatePressureByTime(Wall wall, double collisionDelta) {
        Map<Double, Double> pressureByTime = new TreeMap<>();
        List<Double> momentums = wall.getMomentum();
        double timeInterval = 0;
        for (int i = 0; i < momentums.size(); timeInterval += collisionDelta, i++) {
            double pressure = momentums.get(i) / (timeInterval * wall.getL());
            pressureByTime.put(timeInterval, pressure);
        }
        return pressureByTime;
    }

    public static Map<Double, Double> calculatePressureByTime(StaticParticle staticParticle, double collisionDelta) {
        Map<Double, Double> pressureByTime = new TreeMap<>();
        List<Double> momentums = staticParticle.getMomentum();
        double timeInterval = 0;
        for (int i = 0; i < momentums.size(); timeInterval += collisionDelta, i++) {
            // Área de contacto (aproximación simplificada, puede ser ajustada según el contexto)
            double contactArea = 4 * Math.PI * Math.pow(staticParticle.getRadius(), 2); // Área total de la esfera (ajustar según el contacto real)

            double pressure = momentums.get(i) / (timeInterval * contactArea);
            pressureByTime.put(timeInterval, pressure);
        }
        return pressureByTime;
    }


    public static void main2(String[] args) throws Exception {
        int maxEpoch = 500;

        double L = 0.1;
        double staticRadius = 0.05;
        int N = 250;
        double collisionDelta = 1;

        String projectPath = Paths.get("").toAbsolutePath().toString();
        Path directoryPath = Paths.get(projectPath, String.format("test/output"));

        Set<Particle> particleSet = Main.loadFromFile(directoryPath + "/static.txt", directoryPath + "/dynamic.txt");
        MDImpl molecularDynamic = MDImpl.newInstance(N, L, staticRadius, particleSet);
        molecularDynamic.run(maxEpoch, collisionDelta);

        Map<Integer,State> states = molecularDynamic.getStates();
        Map<WallType, Wall> walls = molecularDynamic.getWalls();


        // --- Save ---
        Files.createDirectories(directoryPath);
        save(N, L, directoryPath.toString(), states);

    }


    public static void main(String[] args) throws Exception {
        int maxEpoch = 500;

        double L = 0.1;
        double staticRadius = 0.005;
        int N = 250;
        double collisionDelta = 1;

        MDImpl molecularDynamic = new MDImpl(N, L, staticRadius);
        molecularDynamic.run(maxEpoch, collisionDelta);

        Map<Integer,State> states = molecularDynamic.getStates();
        Map<WallType, Wall> walls = molecularDynamic.getWalls();

/*        Map<Double, Double> pressureByTime = Main.calculatePressureByTime(molecularDynamic.getStaticParticle(), collisionDelta);
        for (Double time : pressureByTime.keySet()) {
            System.out.println(time + ": " + pressureByTime.get(time));
        }*/



        // --- Save ---
        String projectPath = Paths.get("").toAbsolutePath().toString();
        Path directoryPath = Paths.get(projectPath, String.format("test/output"));
        Files.createDirectories(directoryPath);
        save(N, L, directoryPath.toString(), states);

    }
}