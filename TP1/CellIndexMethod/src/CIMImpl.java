import java.util.ArrayList;
import java.util.List;
import java.util.Random;

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
    private double cellSize;

    private List<Particle> particlesList;
    private List<Particle>[] grid;

    @SuppressWarnings("unchecked")
    public CIMImpl(int m, int n, int l, double radius, double particlesRadius, List<Particle> particleList) throws Exception {
        if ((float)(l / m) > radius) {
            throw new Exception("L/M debe ser mayor al radio de interacción.");
        }

        M = m;
        N = n;
        L = l;
        rc = radius;
        cellSize = (double) L / M;

        this.particlesList = new ArrayList<>();
        this.grid = new ArrayList[M * M];

        for (int i = 0; i < M * M; i++) {
            grid[i] = new ArrayList<>();
        }

        this.generateRandomParticles(this.N, particlesRadius);
        this.assignParticlesToCells();
    }

    private void generateRandomParticles(int N, double particleRadius) {
        Random random = new Random();

        for (int i = 0; i < N; i++) {
            // Posición x aleatoria dentro del área L x L
            double x = random.nextDouble() * L;
            double y = random.nextDouble() * L;
            this.particlesList.add(new Particle(i, x, y, particleRadius));
        }
    }

    private void assignParticlesToCells() {
        for (Particle p : particlesList) {
            int cellX = (int) (p.getPosX() / cellSize);
            int cellY = (int) (p.getPosY() / cellSize);
            int cellIndex = cellY * M + cellX;
            grid[cellIndex].add(p);
        }
    }

    private List<Particle> getNeighboringParticles(int cellX, int cellY, boolean continious) {
        List<Particle> neighborsParticles = new ArrayList<>();

        /*  Matriz completa, innecesaria.
                {-1, -1}, {-1, 0}, {-1, 1},
                { 0, -1}, { 0, 0}, { 0, 1},
                { 1, -1}, { 1, 0}, { 1, 1},
         */
        int[][] moveCoordinates = {
                { 1, 0}, { 1, 1},
                { 0, 0}, { 0, 1},
                         {-1, 1},
            };
        for (int[] movePos : moveCoordinates) {
            int calculatedCellX = cellX + movePos[0];
            int calculatedCellY = cellY + movePos[1];

            if ((!continious) && (calculatedCellX < 0 || calculatedCellX > M - 1) && (calculatedCellY < 0 || calculatedCellY > M - 1) ) {
                continue;
            }

            for (Particle particle : grid[M * calculatedCellY + calculatedCellX]) {
                neighborsParticles.add(particle);
            }
        }
        return neighborsParticles;
    }

    public void findInteractions() {
        for (int i = 0; i < grid.length; i++) {
            int cellX = i / M;
            int cellY = i % this.M;
            List<Particle> neighbors = getNeighboringParticles(cellX, cellY, false);

            for (Particle p1 : this.grid[i]) {
                for (Particle p2 : neighbors) {
                    if (p1 != p2) {
                        double dx = p1.getPosX() - p2.getPosX();
                        double dy = p1.getPosY() - p2.getPosY();
                        double centerDistance = Math.sqrt(dx * dy + dy * dy);

                        if (0 >= centerDistance - p1.getRadius() - p2.getRadius()) {
                            System.out.println("Interaction found between particles at " + p1 + "and" + p2);
                        }
                    }
                }
            }
        }
    }


}