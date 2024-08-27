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
    private List<Particle>[][] virtualGrid;

    @SuppressWarnings("unchecked")
    public CIMImpl(int M, int N, int L, double maxR, List<Particle> particles) {
        this.M = M;
        this.N = N;
        this.L = L;
        this.maxR = maxR;
        cellSize = (double) L / M;

        /* Grilla real desde 1 a M */
        this.grid = new ArrayList[M][M];
        this.virtualGrid = new ArrayList[M+2][M+2];

        for (int i = 0; i < M; i++) {
            for (int j = 0; j < M; j++) {
                grid[i][j] = new ArrayList<>();
            }
        }

        for (int i = 0; i < M + 2; i++) {
            for (int j = 0; j < M + 2; j++) {
                virtualGrid[i][j] = new ArrayList<>();
            }
        }

        this.virtualList = new ArrayList<>();
        this.particlesList = particles;
        this.assignParticlesToCells();
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
            virtualGrid[cellY][cellX].add(p);
        }
    }

    private void generateVirtualParticles() {
        if (this.M < 2) {
            return;
        }

        // Recorremos las columnas intermedias, y calculamos para fila 0 y M-1.
        for (int column = 1; column < M-1; column++) {
            for (Particle p : grid[0][column]) {
                double distanceY = p.getPosY() - 0;
                double virtualY = L + distanceY;
                Particle newVirtual = new Particle(p.getId(), p.getPosX(), virtualY, p.getRadius(),p.getVel(),p.getAngle());
                virtualList.add(newVirtual);
            }

            for (Particle p : grid[M-1][column]) {
                double virtualY = L - p.getPosY();

                Particle newVirtual = new Particle(p.getId(), p.getPosX(), - virtualY, p.getRadius(),p.getVel(),p.getAngle());
                virtualList.add(newVirtual);
            }
        }

        // Recorremos las filas intermedias, y calculamos para columna 0 y M-1.
        for (int row = 1; row < M-1; row++) {
            for (Particle p : grid[row][0]) {
                double distanceX = p.getPosX() - 0;
                double virtualX = L + distanceX;

                Particle newVirtual = new Particle(p.getId(), virtualX, p.getPosY(), p.getRadius(),p.getVel(),p.getAngle());
                virtualList.add(newVirtual);
            }

            for (Particle p : grid[row][M-1]) {
                double virtualX = L - p.getPosX();

                Particle newVirtual = new Particle(p.getId(), - virtualX, p.getPosY(), p.getRadius(),p.getVel(),p.getAngle());
                virtualList.add(newVirtual);
            }
        }

        // Analizamos las esquinas individualmente.
        // chequeadisimo. OK. :)
        for (Particle p : grid[0][0]) {
            double distanceY = p.getPosY() - 0;
            double virtualY = L + distanceY;
            double distanceX = p.getPosX() - 0;
            double virtualX = L + distanceX;

            virtualList.add(new Particle(p.getId(), p.getPosX(), virtualY, p.getRadius(),p.getVel(),p.getAngle()));
            virtualList.add(new Particle(p.getId(), virtualX, p.getPosY(), p.getRadius(),p.getVel(),p.getAngle()));
            virtualList.add(new Particle(p.getId(), virtualX, virtualY, p.getRadius(),p.getVel(),p.getAngle()));
        }

        for (Particle p : grid[0][M-1]) {
            double distanceY = p.getPosY() - 0;
            double virtualY = L + distanceY;
            double distanceX = L - p.getPosX();
            double virtualX = - distanceX;

            // Tener en cuenta las tres esquinas.
            virtualList.add(new Particle(p.getId(), p.getPosX(), virtualY, p.getRadius(),p.getVel(),p.getAngle()));
            virtualList.add(new Particle(p.getId(), virtualX, p.getPosY(), p.getRadius(),p.getVel(),p.getAngle()));
            virtualList.add(new Particle(p.getId(), virtualX, virtualY, p.getRadius(),p.getVel(),p.getAngle()));
        }

        for (Particle p : grid[M-1][0]) {
            double distanceY = L - p.getPosY();
            double virtualY = distanceY;
            double distanceX = p.getPosX() - 0;
            double virtualX = L + distanceX;

            virtualList.add(new Particle(p.getId(), virtualX, p.getPosY(), p.getRadius(),p.getVel(),p.getAngle())); // Esquina derecha.
            virtualList.add(new Particle(p.getId(), p.getPosX(), - virtualY, p.getRadius(),p.getVel(),p.getAngle()));
            virtualList.add(new Particle(p.getId(), virtualX, - virtualY, p.getRadius(),p.getVel(),p.getAngle())); // Borde inferior derecho
        }

        // chequeadisimo. OK. :)
        for (Particle p : grid[M-1][M-1]) {
            double distanceY = L - p.getPosY() - 0;
            double virtualY = distanceY;
            double distanceX = L - p.getPosX();
            double virtualX = distanceX;

            virtualList.add(new Particle(p.getId(), p.getPosX(), - virtualY, p.getRadius(),p.getVel(),p.getAngle()));
            virtualList.add(new Particle(p.getId(), - virtualY, p.getPosY(), p.getRadius(),p.getVel(),p.getAngle()));
            virtualList.add(new Particle(p.getId(), - virtualX, - virtualY, p.getRadius(),p.getVel(),p.getAngle()));
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
                { 0, 1}, { 1, 1},
                { 0, 0}, { 1, 0},
                {1, -1}
            };
        for (int[] movePos : moveCoordinates) {
            int calculatedCellX = cellX + movePos[0];
            int calculatedCellY = cellY + movePos[1];

            if (calculatedCellX >= 0 && calculatedCellX <= M - 1 && calculatedCellY >= 0 && calculatedCellY <= M - 1) {
                neighborsParticles.addAll(grid[calculatedCellY][calculatedCellX]);
            }

            if (continious && (calculatedCellX < 0 || calculatedCellX > M - 1 || calculatedCellY < 0 || calculatedCellY > M - 1)) {
                neighborsParticles.addAll(virtualGrid[(calculatedCellY + (M+2)) % (M+2)][(calculatedCellX + (M+2)) % (M+2)]);
            }
        }
        return neighborsParticles;
    }

    public Map<Integer, List<Particle>> findInteractions(double rc, boolean continious) throws Exception {
        if ((double)(this.L / this.M) <= rc + 2 * maxR) {
            throw new Exception("L/M debe ser mayor o igual a (rc + 2 * maxR).");
        }

        if (continious) {
            this.generateVirtualParticles();
            this.assignVirtualParticlesToCells();
        }

        Map<Integer, List<Particle>> interactions = new HashMap<>();

        for (int cellY = 0; cellY < M; cellY++) {
            for (int cellX = 0; cellX < M; cellX++) {
                List<Particle> neighbors = getNeighboringParticles(cellX, cellY, continious);

                for (Particle p1 : this.grid[cellY][cellX]){
                    for (Particle p2 : neighbors) {
                        if (p1 != p2) {
                            Particle interactionParticle = new Particle(-1, p1.getPosX(), p1.getPosY(), rc,0,0);

                            if (p2.isPartiallyInside(interactionParticle)) {
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

    public void save(String directoryPath, Map<Integer, List<Particle>> interactions) {
        try {

            // Crear la ruta para el archivo de posiciones dentro de la carpeta "test"
            String dynamicPath = Paths.get(directoryPath, "dynamic").toString();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(dynamicPath))) {
                // Imprimimos el único t = 0.
                writer.write("" + 0);
                writer.newLine();

                for (Particle particle : this.particlesList) {
                    writer.write(particle.getId() + "\t" + particle.getPosX() + "\t" + particle.getPosY());
                    writer.newLine();
                }
                System.out.println("Posiciones guardadas en el archivo: " + dynamicPath);
            }

            // Crear la ruta para el archivo de interacciones dentro de la carpeta "test"
            String interactionsPath = Paths.get(directoryPath, "interactions").toString();
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

            String staticPath = Paths.get(directoryPath, "static").toString();
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