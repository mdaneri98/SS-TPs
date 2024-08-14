import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.*;


class CIMImpl {
    private int M; //Dimension de la matriz

    private int N; //Cantidad de particulas
    private int L; //Longitud de la matriz
    private double maxR;   //Radio de las particulas
    private double cellSize;

    private List<Particle> particlesList;
    private List<Particle> virtualList;
    private List<Particle>[][] grid;

    @SuppressWarnings("unchecked")
    public CIMImpl(int M, int N, int L, double maxR, List<Particle> particles) {
        this.M = M;
        this.N = N;
        this.L = L;
        this.maxR = maxR;
        cellSize = (double) L / M;

        /* Grilla real desde 1 a M */
        this.grid = new ArrayList[M+2][M+2];

        for (int i = 0; i < M + 2; i++) {
            for (int j = 0; j < M + 2; j++) {
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
            double x = random.nextDouble() * (L - maxR);
            double y = random.nextDouble() * (L - maxR);
            double radius = this.maxR;
            this.particlesList.add(new Particle(i, x, y, radius));
        }
    }

    private void assignParticlesToCells() {
        for (Particle p : particlesList) {
            int cellX = (int) (p.getPosX() / cellSize);
            int cellY = (int) (p.getPosY() / cellSize);
            grid[cellY][cellX].add(p);
        }
    }

    private void assignVirtualParticlesToCells() {
        for (Particle p : virtualList) {
            int cellX = (int) (p.getPosX() / cellSize);
            int cellY = (int) (p.getPosY() / cellSize);
            grid[cellY][cellX].add(p);
        }
    }

    private void generateVirtualParticles() {
        this.virtualList = new ArrayList<>();

        // Recorremos las columnas, y calculamos para fila 0 y M-1.
        for (int column = 0; column < M; column++) {
            for (Particle p : grid[0][column]) {
                double distanceY = p.getPosY() - 0;
                double virtualY = L + distanceY;

                Particle newVirtual = new Particle(p.getId(), p.getPosX(), virtualY, p.getRadius());
                virtualList.add(newVirtual);
            }

            for (Particle p : grid[M-1][column]) {
                double distanceY = L - p.getPosY();
                double virtualY =  - distanceY;

                Particle newVirtual = new Particle(p.getId(), p.getPosX(), virtualY, p.getRadius());
                virtualList.add(newVirtual);
            }
        }

        // Recorremos las filas, y calculamos para columna 0 y M-1.
        for (int row = 0; row < M; row++) {
            for (Particle p : grid[row][0]) {
                double distanceX = p.getPosX() - 0;
                double virtualX = L + distanceX;

                Particle newVirtual = new Particle(p.getId(), virtualX, p.getPosY(), p.getRadius());
                virtualList.add(newVirtual);
            }

            for (Particle p : grid[row][M-1]) {
                double distanceX = L - p.getPosX();
                double virtualX =  - distanceX;

                Particle newVirtual = new Particle(p.getId(), virtualX, p.getPosY(), p.getRadius());
                virtualList.add(newVirtual);
            }
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
                { 1, 0}, { 1, 1},
                { 0, 0}, { 0, 1},
                {-1, 1},
            };
        for (int[] movePos : moveCoordinates) {
            int calculatedCellX = cellX + movePos[0];
            int calculatedCellY = cellY + movePos[1];

            if (continious) {
                //Lista de virtuales
            } else if (calculatedCellX < 0 || calculatedCellX > M - 1 || calculatedCellY < 0 || calculatedCellY > M - 1) {
                //!continous && ...
                continue;
            }

            neighborsParticles.addAll(grid[calculatedCellY][calculatedCellX]);
        }
        return neighborsParticles;
    }

    public Map<Integer, List<Particle>> findInteractions(double rc, boolean continious) throws Exception {
        if ((double)(this.L / this.M) <= rc - 2*maxR) {
            throw new Exception("L/M debe ser mayor al (rc - 2*maxR).");
        }

        if (continious) {
            this.generateVirtualParticles();
            this.assignVirtualParticlesToCells();
        }

        Map<Integer, List<Particle>> interactions = new HashMap<>();

        for (int cellY = 1; cellY < M + 1; cellY++) {
            for (int cellX = 1; cellX < M + 1; cellX++) {
                List<Particle> neighbors = getNeighboringParticles(cellX, cellY, continious);

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
                                interactions.putIfAbsent(p2.getId(), new ArrayList<>());
                                interactions.get(p2.getId()).add(p1);
                            }
                        }
                    }
                }
            }
        }

        return interactions;
    }

    public void save(String filename, Map<Integer, List<Particle>> interactions) {
        try {
            // Obtener la ruta relativa al directorio del proyecto
            String projectPath = Paths.get("").toAbsolutePath().toString();

            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String positionsPath = Paths.get(projectPath, "test", filename + "_dynamic").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(positionsPath))) {
                // Imprimimos el único t = 0.
                writer.write("" + 0);
                writer.newLine();

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

            String staticPath = Paths.get(projectPath, "test", filename + "_static").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(staticPath))) {
                writer.write("" + particlesList.size());
                writer.newLine();
                writer.write("" + this.L);
                writer.newLine();

                for (Particle p : particlesList) {
                    // Escribir el radio de la partícula, y color negro.
                    writer.write(p.getRadius() + "\t" + 1);
                    writer.newLine();
                }
                System.out.println("Datos estáticos guardados en el archivo: " + staticPath);
            }
        } catch (IOException e) {
            System.err.println("Error al guardar los archivos: " + e.getMessage());
        }

    }

    public List<Particle> getParticlesList() {
        return this.particlesList;
    }

}