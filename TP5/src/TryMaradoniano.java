import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Locale;
import java.util.Random;
import java.util.Set;

import models.Field;
import models.Particle;
import models.Position;
import models.Velocity;

public class TryMaradoniano {

	
	private final int N;
	private final Field field;
	private final double blueVelocityMax;
	private final double redVelocityMax;
	private final double blueTau;
	private final double redTau;
	private final double minRadius; 
	private final double maxRadius;
	
	private State initial;
	
	public TryMaradoniano(int N, Field field, double blueVelocityMax, double redVelocityMax, double blueTau, double redTau, double minRadius, double maxRadius) {
		this.N = N;
		this.field = field;
		this.blueVelocityMax = blueVelocityMax;
		this.redVelocityMax = redVelocityMax;
		this.blueTau = blueTau;
		this.redTau = redTau;
		this.minRadius = minRadius;
		this.maxRadius = maxRadius;
		
		this.initial = bounceState();
	}
	
	public State twoState() {
		Set<Particle> particles = new HashSet<>();
			
		Particle player = new Particle(
			    0, 
			    new Position(field.getWidth() - 2 * maxRadius, field.getHeight()/2.0),
			    field,
			    new Velocity(new double[] {-1.0, 0}, redVelocityMax),
			    redVelocityMax,
			    minRadius,
			    maxRadius,
			    maxRadius,
			    redTau
			);
		
		Particle second = new Particle(
			    1,
			    new Position(2 * maxRadius, field.getHeight()/2.0),
			    player,
			    new Velocity(new double[] {1.0, 0}, redVelocityMax),
			    redVelocityMax,
			    minRadius,
			    maxRadius,
			    maxRadius,
			    redTau
			);
				
		particles.add(second);
		
	
		return new State(0.0, field, player, particles);
	}

	public State bounceState() {
		Set<Particle> particles = new HashSet<>();

		// Crear el jugador en el lado derecho
		Particle player = new Particle(
				0,
				new Position(field.getWidth() - 2 * maxRadius, field.getHeight()/2.0),
				field,
				new Velocity(new double[] {0, 0}, 0),
				redVelocityMax, // Cambiado de 0 a redVelocityMax para permitir movimiento
				minRadius,
				maxRadius,
				maxRadius,
				redTau
		);

		// Primera partícula cerca del eje y
		Particle p1 = new Particle(
				1,
				new Position(1, 3.5),  // A un tercio de la altura
				player,
				new Velocity(new double[] {0, 0}, blueVelocityMax),
				blueVelocityMax,
				minRadius,
				maxRadius,
				maxRadius,
				blueTau
		);

		// Segunda partícula cerca del eje y, separada de la primera
		Particle p2 = new Particle(
				2,
				new Position(1, 4.5),  // A dos tercios de la altura
				player,
				new Velocity(new double[] {0, 1}, blueVelocityMax),
				blueVelocityMax,
				minRadius,
				maxRadius,
				maxRadius,
				blueTau
		);

		// Agregar las partículas al conjunto
		particles.add(p1);
		particles.add(p2);

		return new State(0.0, field, player, particles);
	}
	
	public State initialState() {
		Random random = new Random();
		Set<Particle> particles = new HashSet<>();
			
		Particle player = new Particle(
			    0, 
			    new Position(field.getWidth() - 2 * maxRadius, field.getHeight()/2.0),
			    field,
			    new Velocity(new double[] {-1.0, 0}, redVelocityMax), // Vector dirección hacia la izquierda
			    redVelocityMax,
			    minRadius,
			    maxRadius,
			    maxRadius,
			    redTau
			);
		
		while (particles.size() < N) {
			// Posición x aleatoria dentro del área L x L
            double x = maxRadius + random.nextDouble() * (field.getWidth() - 2 * maxRadius);
            double y = maxRadius + random.nextDouble() * (field.getHeight() - 2 * maxRadius);
            
            Particle blue = new Particle(particles.size() + 1, new Position(x, y), player, new Velocity(new double[] {0,0}, blueVelocityMax), blueVelocityMax, minRadius, maxRadius, maxRadius, blueTau);
            
            boolean match = false;
            for (Particle particle : particles) {
                match = blue.isInsidePersonalSpace(particle);
                if (match)
                    break;
            }
            if (!match)
            	particles.add(blue);
		}
		
	
		return new State(0.0, field, player, particles);
	}
	
	public void run() {
		String directory = String.format(Locale.US, "try_maradoniano");

		Path staticPath = getFilePath(directory, "static.txt");
		saveStatic(staticPath);

		Path filepath = getFilePath(directory, "dynamic.txt");
	        
		TryMaradonianoSystem tms = new TryMaradonianoSystem(N, field, blueVelocityMax, redVelocityMax, blueTau, redTau, minRadius, maxRadius, this.initial);
		runSolution(tms, filepath);
		
		System.out.println("Finished");
	}
	
	private void runSolution(Iterator<State> iterator, Path filepath) {
        LinkedList<State> statesToSave = new LinkedList<>();

        int stateCounter = 0;
        int saveFrequency = 40; // Guarda cada 100 estados
        int maxStatesToSave = 100; // Máximo número de estados a guardar antes de escribir en archivo

        while (iterator.hasNext()) {
            State currentState = iterator.next();
            stateCounter++;

            if (stateCounter % saveFrequency == 0) {
                statesToSave.add(currentState);
            }

            if (statesToSave.size() >= maxStatesToSave) {
                save(statesToSave, filepath);
                statesToSave.clear();
            }
        }

        // Si quedan estados por guardar después de salir del bucle
        if (!statesToSave.isEmpty()) {
            save(statesToSave, filepath);
            statesToSave.clear();
        }
    }
	
	  private void saveStatic(Path filePath) {
	        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE)) {
	        	// Parámetros generales
	        	writer.write(String.format(Locale.US, 
	        			"blueVelocityMax: %.6f"
	        			+ "\n"
	        			+ "redVelocityMax: %.6f"
	        			+ "\n"
	        			+ "blueTau: %.6f"
	        			+ "\n"
	        			+ "redTau: %.6f"
	        			+ "\nrMin: %.6f"
	        			+ "\n"
	        			+ "rMax: %.6f"
	        			+ "\n"
	        			+ "width: %d"
	        			+ "\n"
	        			+ "height: %d"
	        			+ "\n",
	        			blueVelocityMax, redVelocityMax, blueTau, redTau, minRadius, maxRadius, field.getWidth(), field.getHeight()));	                
	        } catch (IOException e) {
	            System.out.println("Error al escribir la información estática: " + e.getMessage());
	            e.printStackTrace();
	        }
	    }

	    private Path getFilePath(String directory, String filename) {
	        try {
	            String projectPath = Paths.get("").toAbsolutePath().toString();
	            Path directoryPath = Paths.get(projectPath, "python", "outputs", directory);
	            Path filePath = directoryPath.resolve(filename);

	            // Crea los directorios si no existen
	            Files.createDirectories(directoryPath);

	            if (Files.deleteIfExists(filePath))
	                System.out.println("Archivo borrado: " + filePath);

	            return filePath;
	        } catch (IOException e) {
	            System.out.println("Error al crear data files: " + e.getMessage());
	            e.printStackTrace();
	        }
	        return null;
	    }

	    // Save method
	    public void save(List<State> states, Path filePath) {
	        boolean fileExists = Files.exists(filePath);

	        try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
	            // Escribir encabezados solo si el archivo no existe
	            if (!fileExists) {
	            	// Nothing
	            }
	            for (State state : states) {
	            	writer.write(String.format(Locale.US, "%.6f\n", state.getTime()));
	            	
	            	Particle p = state.getPlayer();
	            	double velX = p.getVelocity().getDirection()[0] * p.getVelocity().getMod();
                	double velY = p.getVelocity().getDirection()[1] * p.getVelocity().getMod();
                    writer.write(String.format(Locale.US, "%d,%.6f,%.6f,%.6f,%.6f,%.6f\n", p.getId(), p.getPosition().getX(), p.getPosition().getY(), velX, velY, p.getActualRadius()));
	            	
	                for (Particle red : state.getParticles()) {
						velX = red.getVelocity().getDirection()[0] * red.getVelocity().getMod();
						velY = red.getVelocity().getDirection()[1] * red.getVelocity().getMod();
						writer.write(String.format(Locale.US, "%d,%.6f,%.6f,%.6f,%.6f,%.6f\n", red.getId(), red.getPosition().getX(), red.getPosition().getY(), velX, velY, red.getActualRadius()));
					}
	            }
	        } catch (IOException e) {
	            System.out.println("Error al escribir un estado: " + e.getMessage());
	            e.printStackTrace();
	        }
	    }
	
	
}
