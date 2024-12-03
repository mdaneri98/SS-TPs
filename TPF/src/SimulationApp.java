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
        int numIteraciones = 1;
        
        // Primer análisis: variación del parámetro de heurística
        runHeuristicAnalysis(maxVelocity, tau, minRadius, maxRadius, numIteraciones);
        
        // Segundo análisis: variación de la velocidad de los jugadores
        runVelocityAnalysis(tau, minRadius, maxRadius, numIteraciones);

        // Tercer análisis: variación de p
        runProbabilityAnalysis(3.0, tau, minRadius, maxRadius, numIteraciones);

    }
    
    private static void runHeuristicAnalysis(double maxVelocity, double tau, double minRadius, double maxRadius, int numIteraciones) {
        
        int N = 1000;  // Número fijo de jugadores
        List<Double> aps = new ArrayList<>();
        List<Double> bps = new ArrayList<>();
        for (int i = 8; i < 14; i += 2) {
        	aps.add((double) i);
        }

        for (int i = 1; i < 5; i++) {
        	bps.add((double) i * 0.4);
        }

        double p = 0.5;
        
        for (double ap : aps) {
	        for (double bp : bps) {
	            for (int i = 0; i < numIteraciones; i++) {
	                String directory = String.format(Locale.US, "heuristic_analysis/ap_%.2f_bp_%.2f/sim_%03d", ap, bp, i);
	                
	                try {
	                    Path dirPath = Paths.get("python", "outputs", directory);
	                    Files.createDirectories(dirPath);
	                    
	                    SimulationRunner tm = new SimulationRunner(N, p, maxVelocity, tau, minRadius, maxRadius, ap, bp);
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
        int N = 1000;  // Número fijo de jugadores

        List<Double> ps = new ArrayList<>();
        for (int i = 0; i <= 10; i += 1) {
            ps.add((double) i * 0.1);
        }

        double ap = 1.0;
        double bp = 0.8;

        for (double p : ps) {
                for (int i = 0; i < numIteraciones; i++) {
                    String directory = String.format(Locale.US, "probabilistic_analysis/p_%.2f/sim_%03d", p, i);

                    try {
                        Path dirPath = Paths.get("python", "outputs", directory);
                        Files.createDirectories(dirPath);

                        SimulationRunner tm = new SimulationRunner(N, p, maxVelocity, tau, minRadius, maxRadius, ap, bp);
                        tm.setOutputDirectory(directory);
                        tm.run();

                    } catch (Exception e) {
                        System.err.printf("Error en simulación parámetro %.2f, realización %d: %s%n",
                                ap, i, e.getMessage());
                    }
                }
        }
    }
    
    private static void runVelocityAnalysis(double tau, double minRadius, double maxRadius, int numIteraciones) {
        int N = 1000;  // Número fijo de jugadores

        List<Integer> velocities = new ArrayList<>();
        for (int i = 1; i <= 5; i += 1)
            velocities.add(i);
        
        double p = 0.5;

        double ap = 10.0;  // Usar el mejor parámetro encontrado en el análisis anterior
        double bp = 1.0;
        for (int j = 0; j < velocities.size(); j++) {
        	int velocity = velocities.get(j);
            for (int i = 0; i < numIteraciones; i++) {
                String directory = String.format(Locale.US, "velocity_analysis/v_%d/sim_%03d", velocity, i);

                try {
                    Path dirPath = Paths.get("python", "outputs", directory);
                    Files.createDirectories(dirPath);

                    SimulationRunner tm = new SimulationRunner(N, p, velocity, tau, minRadius, maxRadius, ap, bp);
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