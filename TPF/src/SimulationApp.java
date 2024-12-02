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
        
        // Segundo análisis: variación del número de jugadores
        //runPlayersAnalysis(maxVelocity, tau, minRadius, maxRadius, numIteraciones);
    }
    
    private static void runHeuristicAnalysis(double maxVelocity, double tau, double minRadius, double maxRadius, int numIteraciones) {
        
        int N = 500;  // Número fijo de jugadores
        List<Double> aps = new ArrayList<>();
        List<Double> bps = new ArrayList<>();
        aps.add(6.0);
        bps.add(2.0);
        /*for (int i = 2; i < 24; i += 4) {
        	aps.add((double) i);
        }

        for (int i = 0; i < 50; i++) {
        	bps.add((double) i * 0.4);
        }*/

        
        for (double ap : aps) {
	        for (double bp : bps) {
	            for (int i = 0; i < numIteraciones; i++) {
	                String directory = String.format(Locale.US, "heuristic_analysis/ap_%.2f_bp_%.2f/sim_%03d", ap, bp, i);
	                
	                try {
	                    Path dirPath = Paths.get("python", "outputs", directory);
	                    Files.createDirectories(dirPath);
	                    
	                    SimulationRunner tm = new SimulationRunner(N, maxVelocity, tau, minRadius, maxRadius, ap, bp);
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
    
    private static void runPlayersAnalysis(double maxVelocity, double tau, double minRadius, double maxRadius, int numIteraciones) {
            
        List<Integer> playersCount = new ArrayList<>();
        for (int i = 5; i <= 100; i+= 5)
        	playersCount.add(i);
        
        
        double ap = 6.0;  // Usar el mejor parámetro encontrado en el análisis anterior
        double bp = 1.6;
        for (int j = 0; j < playersCount.size(); j++) {
        	int N = playersCount.get(j);
            for (int i = 0; i < numIteraciones; i++) {
                String directory = String.format(Locale.US, "players_analysis/N_%d/sim_%03d", N, i);
                
                try {
                    Path dirPath = Paths.get("python", "outputs", directory);
                    Files.createDirectories(dirPath);
                    
                    SimulationRunner tm = new SimulationRunner(N, maxVelocity, tau, minRadius, maxRadius, ap, bp);
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