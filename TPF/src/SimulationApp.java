import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import models.Field;

public class SimulationApp {


    public static void main(String[] args) {
        // Parámetros constantes
        double maxVelocity = 1.0;
        double tau = 0.5;
        double minRadius = 0.15;
        double maxRadius = 0.35;

        // Parámetros configurables
        int numIteraciones = 5;

        // Primer análisis: variación de la velocidad de los jugadores
        //runTAnalysis(maxVelocity, tau, minRadius, maxRadius, numIteraciones);

        // Tercer análisis: variación de p
        runProbabilityAnalysis(maxVelocity, tau, minRadius, maxRadius, numIteraciones);

        // Segundo análisis: variación del parámetro de heurística
        //runHeuristicAnalysis(maxVelocity, tau, minRadius, maxRadius, numIteraciones);



    }
    
    private static void runHeuristicAnalysis(double maxVelocity, double tau, double minRadius, double maxRadius, int numIteraciones) {
        int N = 500;  // Número fijo de jugadores
        int ct = 60;

        List<Double> aps = new ArrayList<>();
        List<Double> bps = new ArrayList<>();
        aps.add(1.0);
        bps.add(0.8);

        double p = 0.5;
        
        for (double ap : aps) {
	        for (double bp : bps) {
	            for (int i = 0; i < numIteraciones; i++) {
	                String directory = String.format(Locale.US, "heuristic_analysis/ap_%.2f_bp_%.2f/sim_%03d", ap, bp, i);
	                
	                try {
	                    Path dirPath = Paths.get("python", "outputs", directory);
	                    Files.createDirectories(dirPath);
	                    
	                    SimulationRunner tm = new SimulationRunner(N, p, maxVelocity, tau, minRadius, maxRadius, ap, bp, ct);
	                    tm.setOutputDirectory(directory);
	                    tm.run();
	                    
	                } catch (Exception e) {
	                    System.err.printf("Error en simulación parámetro %.2f, realización %d: %s%n", 
	                            ap, i, e.getMessage());
	                }
	            }
	        }
        }
    }

    private static void runProbabilityAnalysis(double maxVelocity, double tau, double minRadius, double maxRadius, int numIteraciones) {
        int N = 500;  // Número fijo de jugadores

        List<Double> ps = new ArrayList<>();
        for (int i = 0; i <= 10; i += 1) {
            ps.add((double) i * 0.1);
        }

        List<Integer> cts = new ArrayList<>();
        for (int i = 5; i <= 250; i += 5)
            cts.add(i);

        double ap = 1.0;
        double bp = 0.8;

        for (int ct : cts) {
            for (double p : ps) {
                for (int i = 0; i < numIteraciones; i++) {
                    String directory = String.format(Locale.US, "probabilistic_analysis/t_%d_&_p_%.2f/sim_%03d", ct, p, i);

                    try {
                        Path dirPath = Paths.get("python", "outputs", directory);
                        Files.createDirectories(dirPath);

                        SimulationRunner tm = new SimulationRunner(N, p, maxVelocity, tau, minRadius, maxRadius, ap, bp, ct);
                        tm.setOutputDirectory(directory);
                        tm.run();

                    } catch (Exception e) {
                        System.err.printf("Error en simulación parámetro %.2f, realización %d: %s%n",
                                ap, i, e.getMessage());
                    }
                }
            }
        }
    }
    
    private static void runTAnalysis(double maxVelocity, double tau, double minRadius, double maxRadius, int numIteraciones) {
        int N = 500;  // Número fijo de jugadores

        List<Integer> cts = new ArrayList<>();
        for (int i = 20; i <= 600; i += 10)
            cts.add(i);
        
        double p = 0.5;

        double ap = 1.0;
        double bp = 0.8;
        for (int j = 0; j < cts.size(); j++) {
        	int ct = cts.get(j);
            for (int i = 0; i < numIteraciones; i++) {
                String directory = String.format(Locale.US, "times_analysis/t_%d/sim_%03d", ct, i);

                try {
                    Path dirPath = Paths.get("python", "outputs", directory);
                    Files.createDirectories(dirPath);

                    SimulationRunner tm = new SimulationRunner(N, p, maxVelocity, tau, minRadius, maxRadius, ap, bp, ct);
                    tm.setOutputDirectory(directory);
                    tm.run();

                } catch (Exception e) {
                    System.err.printf("Error en simulación %d jugadores, realización %d: %s%n",
                            N, i, e.getMessage());
                }
            }
        }
    }
}