import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.*;

class Particle {

    private int id;
    private double posX;
    private double posY;
    private double radius;

    public Particle(int id, double posX, double posY, double radius) {
        this.id = id;
        this.posX = posX;
        this.posY = posY;
        this.radius = radius;
    }

    public boolean isInside(Particle other) {
        // Calcular la distancia entre los centros de las partículas
        double distance = Math.sqrt(Math.pow(other.posX - this.posX, 2) + Math.pow(other.posY - this.posY, 2));

        // Verificar si la partícula actual está completamente dentro de la otra
        return distance + this.radius <= other.radius;
    }

    @Override
    public String toString() {
        return "Particle(x: %f, y: %f, r: %f)".formatted(posX, posY, radius);
    }

    public int getId() {
        return id;
    }

    public double getPosX() {
        return posX;
    }

    public void setPosX(float posX) {
        this.posX = posX;
    }

    public double getPosY() {
        return posY;
    }

    public void setPosY(float posY) {
        this.posY = posY;
    }

    public double getRadius() {
        return radius;
    }

    public void setRadius(float radius) {
        this.radius = radius;
    }

}

class CIMImpl {
    private int M; //Dimension de la matriz

    private int N; //Cantidad de particulas
    private int L; //Longitud de la matriz
    private double rc;   //Radio sobre cual dos
    private double particleRadius;   //Radio de las particulas
    private double cellSize;

    private List<Particle> particlesList;
    private List<Particle>[][] grid;

    @SuppressWarnings("unchecked")
    public CIMImpl(int m, int n, int l, double radius, double particlesRadius, List<Particle> particles) throws Exception {
        if ((float)(l / m) <= radius) {
            throw new Exception("L/M debe ser mayor al radio de interacción.");
        }

        M = m;
        N = n;
        L = l;
        rc = radius;
        particleRadius = particlesRadius;
        cellSize = (double) L / M;

        this.grid = new ArrayList[M][M];

        for (int i = 0; i < M; i++) {
            for (int j = 0; j < M; j++) {
                grid[i][j] = new ArrayList<>();
            }
        }

        if (particles == null) {
            this.particlesList = new ArrayList<>();
            this.generateRandomParticles();
        } else {
            this.particlesList = particles;
        }
        this.assignParticlesToCells();
    }

    private void generateRandomParticles() {
        Random random = new Random();

        for (int i = 0; i < N; i++) {
            // Posición x aleatoria dentro del área L x L
            double x = random.nextDouble() * (L - particleRadius);
            double y = random.nextDouble() * (L - particleRadius);
            this.particlesList.add(new Particle(i, x, y, particleRadius));
        }
    }

    private void assignParticlesToCells() {
        for (Particle p : particlesList) {
            int cellX = (int) (p.getPosX() / cellSize);
            int cellY = (int) (p.getPosY() / cellSize);
            grid[cellY][cellX].add(p);
        }
    }

    private List<Particle> getNeighboringParticles(int cellX, int cellY, boolean continious) {
        List<Particle> neighborsParticles = new ArrayList<>();

        /*  Matriz completa, innecesaria.
                { 1, 0}, { 1, 1},
                { 0, 0}, { 0, 1},
                         {-1, 1},
         */
        int[][] moveCoordinates = {
                {-1, -1}, {-1, 0}, {-1, 1},
                { 0, -1}, { 0, 0}, { 0, 1},
                { 1, -1}, { 1, 0}, { 1, 1},
            };
        for (int[] movePos : moveCoordinates) {
            int calculatedCellX = cellX + movePos[0];
            int calculatedCellY = cellY + movePos[1];

            if (continious) {
                if (calculatedCellX < 0) {
                    calculatedCellX = M - 1;
                }
                if (calculatedCellY < 0) {
                    calculatedCellY = M - 1;
                }
                if (calculatedCellX > M - 1) {
                    calculatedCellX = 0;
                }
                if (calculatedCellY > M - 1) {
                    calculatedCellY = 0;
                }
            } else if (calculatedCellX < 0 || calculatedCellX > M - 1 || calculatedCellY < 0 || calculatedCellY > M - 1) {
                //!continous && ...
                continue;
            }

            neighborsParticles.addAll(grid[calculatedCellY][calculatedCellX]);
        }
        return neighborsParticles;
    }

    public Map<Integer, List<Particle>> findInteractions() {
        Map<Integer, List<Particle>> interactions = new HashMap<>();

        for (int cellY = 0; cellY < M; cellY++) {
            for (int cellX = 0; cellX < M; cellX++) {
                List<Particle> neighbors = getNeighboringParticles(cellX, cellY, false);

                for (Particle p1 : this.grid[cellY][cellX]){
                    for (Particle p2 : neighbors) {
                        if (p1 != p2) {
                            double dx = p1.getPosX() - p2.getPosX();
                            double dy = p1.getPosY() - p2.getPosY();
                            double centerDistance = Math.sqrt(dx * dx + dy * dy);

                            // Si el borde está dentro de rc => Verdadero.
                            double distance = centerDistance - p1.getRadius() - p2.getRadius();
                            if ( distance <= 0 || distance <= (rc - p1.getRadius()) ) {
                                interactions.putIfAbsent(p1.getId(), new ArrayList<>());
                                interactions.get(p1.getId()).add(p2);

                                // Se puede optimizar si no volvemos a recorrer las particulas que ya agregamos de p2.
                                //interactions.putIfAbsent(p2.getId(), new ArrayList<>());
                                //interactions.get(p2.getId()).add(p1);
                            }
                        }
                    }
                }
            }
        }

        return interactions;
    }

    public void run(String filename) {
        // Obtener las interacciones
        Map<Integer, List<Particle>> interactions = findInteractions();

        try {
            // Obtener la ruta relativa al directorio del proyecto
            String projectPath = Paths.get("").toAbsolutePath().toString();

            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String positionsPath = Paths.get(projectPath, "test", filename + "_positions").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(positionsPath))) {
                for (Particle particle : this.particlesList) {
                    writer.write(particle.getId() + "\t" + particle.getPosX() + "\t" + particle.getPosY());
                    writer.newLine();
                }
                System.out.println("Posiciones guardadas en el archivo: " + positionsPath);
            }

            // Crear la ruta para el archivo de interacciones dentro de la carpeta "test"
            String interactionsPath = Paths.get(projectPath, "test", filename + "_interactions").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(interactionsPath))) {
                for (Map.Entry<Integer, List<Particle>> entry : interactions.entrySet()) {
                    Integer particleId = entry.getKey();
                    List<Particle> neighbors = entry.getValue();

                    // Escribir el id de la partícula
                    writer.write(particleId.toString());

                    // Escribir los ids de las partículas vecinas
                    for (Particle neighbor : neighbors) {
                        writer.write("\t" + neighbor.getId());
                    }

                    writer.newLine();
                }
                System.out.println("Interacciones guardadas en el archivo: " + interactionsPath);
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }
    }


}