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
import java.util.Vector;

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
	private final double ap;
	private final double bp;
	
	private String outputDirectory = "try_maradoniano";
	
	private State initial;
	
	public TryMaradoniano(int N, Field field, double blueVelocityMax, double redVelocityMax, double blueTau, double redTau, double minRadius, double maxRadius, double ap, double bp) {
		this.N = N;
		this.field = field;
		this.blueVelocityMax = blueVelocityMax;
		this.redVelocityMax = redVelocityMax;
		this.blueTau = blueTau;
		this.redTau = redTau;
		this.minRadius = minRadius;
		this.maxRadius = maxRadius;
		this.ap = ap;
		this.bp = bp;
		
		this.initial = initialState();
	}
	
	public State twoState() {
		Set<Particle> particles = new HashSet<>();
			
		Particle player = new Particle(
			    0, 
			    new Position(field.getWidth() - 2 * maxRadius, field.getHeight()/2.0),
			    field.getLeftCenter(),
			    new Velocity(new Vector<Double>(List.of(-1.0, 0.0)), redVelocityMax),
			    redVelocityMax,
			    minRadius,
			    maxRadius,
			    maxRadius,
			    redTau
			);
		
		Particle second = new Particle(
			    1,
			    new Position(2 * maxRadius, field.getHeight()/2.0),
			    player.getPosition(),
			    new Velocity(new Vector<Double>(List.of(1.0, 0.0)), blueVelocityMax),
			    blueVelocityMax,
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
				field.getLeftCenter(),
				new Velocity(new Vector<Double>(List.of(-1.0, 0.0)), redVelocityMax),
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
				player.getPosition(),
				new Velocity(new Vector<Double>(List.of(0.0, 0.0)), blueVelocityMax),
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
				player.getPosition(),
				new Velocity(new Vector<Double>(List.of(0.0, -1.0)), blueVelocityMax),
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
		new Position(field.getWidth() - 2*maxRadius, field.getHeight()/2.0),
		field.getLeftCenter(),
		new Velocity(new Vector<Double>(List.of(-1.0, 0.0)), redVelocityMax), // Vector dirección hacia la izquierda
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

		Particle blue = new Particle(particles.size() + 1, new Position(x, y), player.getPosition(), new Velocity(new Vector<Double>(List.of(0.0, 0.0)), blueVelocityMax), blueVelocityMax, minRadius, maxRadius, maxRadius, blueTau);

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
        // Modificar el método run para usar el outputDirectory
        Path staticPath = getFilePath(outputDirectory, "static.txt");
        saveStatic(staticPath);

        Path filepath = getFilePath(outputDirectory, "dynamic.txt");
            
        TryMaradonianoSystem tms = new TryMaradonianoSystem(N, field, blueVelocityMax, redVelocityMax, 
                blueTau, redTau, minRadius, maxRadius, ap, bp, this.initial);
        runSolution(tms, filepath);
        
      
    }
	
	private void runSolution(Iterator<State> iterator, Path filepath) {
	    LinkedList<State> statesToSave = new LinkedList<>();
	    State initialState = this.initial;
	    statesToSave.add(initialState);  // Guardamos el estado inicial
	    
	    int stateCounter = 0;
	    int saveFrequency = 10;
	    int maxStatesToSave = 100;
	    
	    State lastState = initialState;  // Guardamos referencia al último estado
	    
	    while (iterator.hasNext()) {
	        State currentState = iterator.next();
	        stateCounter++;
	        lastState = currentState;  // Actualizamos el último estado
	        
	        if (stateCounter % saveFrequency == 0) {
	            statesToSave.add(currentState);
	        }
	        
	        if (statesToSave.size() >= maxStatesToSave) {
	            save(statesToSave, filepath);
	            statesToSave.clear();
	            // Después de limpiar, volvemos a agregar el último estado guardado
	            // para mantener continuidad en el archivo
	            statesToSave.add(currentState);
	        }
	    }
	    
	    // Si el último estado no fue guardado por la frecuencia, lo agregamos
	    if (lastState != initialState && 
	        (statesToSave.isEmpty() || !statesToSave.getLast().equals(lastState))) {
	        statesToSave.add(lastState);
	    }
	    
	    // Guardamos los estados restantes (incluyendo el último si corresponde)
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
	            	double velX = p.getVelocity().getDirection().getFirst() * p.getVelocity().getMod();
                	double velY = p.getVelocity().getDirection().getLast() * p.getVelocity().getMod();
                    writer.write(String.format(Locale.US, "%d,%.6f,%.6f,%.6f,%.6f,%.6f\n", p.getId(), p.getPosition().getX(), p.getPosition().getY(), velX, velY, p.getActualRadius()));
	            	
	                for (Particle blue : state.getParticles()) {
						velX = blue.getVelocity().getDirection().getFirst() * blue.getVelocity().getMod();
						velY = blue.getVelocity().getDirection().getLast() * blue.getVelocity().getMod();
						writer.write(String.format(Locale.US, "%d,%.6f,%.6f,%.6f,%.6f,%.6f\n", blue.getId(), blue.getPosition().getX(), blue.getPosition().getY(), velX, velY, blue.getActualRadius()));
					}
	            }
	        } catch (IOException e) {
	            System.out.println("Error al escribir un estado: " + e.getMessage());
	            e.printStackTrace();
	        }
	    }
	
	    public void setOutputDirectory(String directory) {
	        this.outputDirectory = directory;
	    }
	
}
