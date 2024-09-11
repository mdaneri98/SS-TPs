//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.

import models.*;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

public class Main {


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
                        writer.write(particle.getId() + "\t" + particle.getPosX() + "\t" + particle.getPosY() + "\t" + particle.getVelocityX() + "\t" + particle.getVelocityY());
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



    public static void main(String[] args) throws Exception {
        int maxEpoch = 1000000;

        double L = 0.01;
        double staticRadius = 0.5;
        int N = 200;
        double collisionDelta = 1;

        MDImpl molecularDynamic = new MDImpl(N, L, staticRadius);
        molecularDynamic.run(maxEpoch, collisionDelta);

        Map<Integer,State> states = molecularDynamic.getStates();
        Map<WallType, Wall> walls = molecularDynamic.getWalls();

        Map<Double, Double> pressureByTime = Main.calculatePressureByTime(molecularDynamic.getStaticParticle(), collisionDelta);
        for (Double time : pressureByTime.keySet()) {
            System.out.println(time + ": " + pressureByTime.get(time));
        }



        // --- Save ---
        String projectPath = Paths.get("").toAbsolutePath().toString();
        Path directoryPath = Paths.get(projectPath, String.format("test/output"));
        Files.createDirectories(directoryPath);
        save(N, L, directoryPath.toString(), states);

    }
}