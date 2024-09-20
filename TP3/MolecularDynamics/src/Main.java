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

    public static void save(String directoryPath, String filename, Map<Double, Double> pressuresByDelta) {
        try {
            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String staticPath = Paths.get(directoryPath, filename).toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                for (Double time : pressuresByDelta.keySet()) {
                    writer.write(time + "\t" + pressuresByDelta.get(time) + "\n");
                }
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }
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
        double L = 0.1;
        double staticRadius = 0.005;
        int N = 20;
        double collisionDelta = 0.2;

        MDImpl molecularDynamic = new MDImpl(N, L, staticRadius);
        molecularDynamic.run(180000/10, collisionDelta);

        Map<Integer,State> states = molecularDynamic.getStates();
        Map<WallType, Wall> walls = molecularDynamic.getWalls();


        //Map<Double, Double> wall_pressureByTime = molecularDynamic.calculatePressureForWalls(0.2);
        //Map<Double, Double> static_pressureByTime = molecularDynamic.calculatePressureForStatic(0.2);


        // --- Save ---
        String projectPath = Paths.get("").toAbsolutePath().toString();
        Path directoryPath = Paths.get(projectPath, String.format("test/output"));
        Files.createDirectories(directoryPath);
        save(N, L, directoryPath.toString(), states);
        //save(directoryPath.toString(), "wall_pressures.txt", wall_pressureByTime);
        //save(directoryPath.toString(), "static_pressures.txt", static_pressureByTime);

    }
}