//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.

import models.MolecularDynamic;
import models.Particle;
import models.State;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import java.util.Set;

public class Main {


    public static void save(int N, double L, String directoryPath, Map<Integer, State> states) {
        try {
            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String staticPath = Paths.get(directoryPath, "static").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                writer.write("" + L + "\n");
                writer.write("" + N + "\n");
                for (Particle particle : states.get(0).getParticles()) {
                    writer.write(particle.getRadius() + "\t" + particle.getMass() + "\t" + 1 + "\n");
                }
            }

            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String dynamicPath = Paths.get(directoryPath, "dynamic").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(dynamicPath))) {
                for (Integer time : states.keySet()) {
                    writer.write("" + time);
                    writer.newLine();

                    for (Particle particle : states.get(time).getParticles()) {
                        writer.write(particle.getId() + "\t" + particle.getPosX() + "\t" + particle.getPosY() + "\t" + particle.getVelocityX() + "\t" + particle.getVelocityY());
                        writer.newLine();
                    }
                }
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }
    }

    public static void main(String[] args) throws Exception {
        int maxEpoch = 800;

        double L = 0.1;
        double staticRadius = 0.005;
        int N = 300;

        MolecularDynamic molecularDynamic = new MolecularDynamic(N, L, staticRadius);
        molecularDynamic.run(maxEpoch);

        Map<Integer,State> states = molecularDynamic.getStates();


        // --- Save ---
        String projectPath = Paths.get("").toAbsolutePath().toString();
        Path directoryPath = Paths.get(projectPath, String.format("/output"));
        Files.createDirectories(directoryPath);
        save(N, L, directoryPath.toString(), states);

    }
}