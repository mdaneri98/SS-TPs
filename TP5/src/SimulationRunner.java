import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import models.Field;

public class SimulationRunner {
    public static void main(String[] args) {
        // Parámetros constantes
        int width = 100;
        int height = 70;
        double blueVelocityMax = 3.8;
        double redVelocityMax = 4.0;
        double blueTau = 0.5;
        double redTau = 0.3;
        double minRadius = 0.15;
        double maxRadius = 0.35;
        Field field = new Field(width, height);
        
        // Parámetros configurables
        int numIteraciones = 1000;
        
        // Primer análisis: variación del parámetro de heurística
        //runHeuristicAnalysis(field, blueVelocityMax, redVelocityMax, blueTau, redTau, minRadius, maxRadius, numIteraciones);
        
        // Segundo análisis: variación del número de jugadores
        runPlayersAnalysis(field, blueVelocityMax, redVelocityMax, blueTau, redTau, minRadius, maxRadius, numIteraciones);
    }
    
    private static void runHeuristicAnalysis(Field field, double blueVelocityMax, double redVelocityMax, 
            double blueTau, double redTau, double minRadius, double maxRadius, int numIteraciones) {
        
        int N = 15;  // Número fijo de jugadores
        List<Double> aps = new ArrayList<>();
        for (int i = 2; i < 24; i += 4) {
        	aps.add((double) i);
        }
        
        List<Double> bps = new ArrayList<>();
        for (int i = 0; i < 50; i++) {
        	bps.add((double) i * 0.4);
        }
        
        for (double ap : aps) {
	        for (double bp : bps) {
	            for (int i = 0; i < numIteraciones; i++) {
	                String directory = String.format(Locale.US, "heuristic_analysis/ap_%.2f_bp_%.2f/sim_%03d", ap, bp, i);
	                
	                try {
	                    Path dirPath = Paths.get("python", "outputs", directory);
	                    Files.createDirectories(dirPath);
	                    
	                    TryMaradoniano tm = new TryMaradoniano(N, field, blueVelocityMax, redVelocityMax,
	                            blueTau, redTau, minRadius, maxRadius, ap, bp);
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
    
    private static void runPlayersAnalysis(Field field, double blueVelocityMax, double redVelocityMax,
            double blueTau, double redTau, double minRadius, double maxRadius, int numIteraciones) {
            
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
                    
                    TryMaradoniano tm = new TryMaradoniano(N, field, blueVelocityMax, redVelocityMax,
                            blueTau, redTau, minRadius, maxRadius, ap, bp);
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