import java.util.*;

public class OffLattice {

    private Map<Integer, List<Particle>> particlesPerTime = new HashMap<>();

    private static double VELOCITY = 0.03;

    private int M; //Dimension de la matriz

    private int N; //Cantidad de particulas
    private int L; //Longitud de la matriz

    private double noiseAmplitude;
    private List<Particle> particlesList;

    public OffLattice(int m, int n, int l, double noiseAmplitude) {
        M = m;
        N = n;
        L = l;
        this.noiseAmplitude = noiseAmplitude;
        this.particlesList = new ArrayList<>();
    }

    private void generateRandomParticles() {
        Random random = new Random();

        for (int i = 0; i < N; i++) {
            // Posición x aleatoria dentro del área L x L
            double x = random.nextDouble() * L;
            double y = random.nextDouble() * L;
            double radius = 0;
            double angle = random.nextDouble() * Math.PI * 2;
            this.particlesList.add(new Particle(i, x, y, radius,VELOCITY,angle));
        }
        particlesPerTime.putIfAbsent(0,particlesList);
    }

    public double calculateAngle(List<Particle> neighbours){

        double sinSum = 0;
        double cosSum = 0;

        for ( Particle particle :neighbours) {
            sinSum += Math.sin(particle.getAngle());
            cosSum += Math.cos(particle.getAngle());
        }

        double avgSin = sinSum/neighbours.size();
        double avgCos = cosSum/neighbours.size();

        double minValue = -noiseAmplitude/2;
        double maxValue = noiseAmplitude/2;
        double noise = minValue + (maxValue - minValue) * Math.random();

        return ((Math.atan2(avgSin,avgCos) + noise) + (2 * Math.PI)) % (2 * Math.PI);
    }

    public Map<Integer,List<Particle>> run(int rc, int maxTime) throws Exception {
        int time = 0;

        generateRandomParticles();
        time++;
        for (; time < maxTime ; time++) {
            CIMImpl cim = new CIMImpl(M,N,L,0,particlesList);
            Map<Integer,List<Particle>> neighboursByParticle = cim.findInteractions(rc,true);
            List<Particle> newParticles = new ArrayList<>();
            for (Particle p : this.particlesPerTime.get(time-1)){
                List<Particle> neighbours = neighboursByParticle.getOrDefault(p.getId(), new ArrayList<>());
                neighbours.add(p);
                double newAngle = calculateAngle(neighbours);
                Pair<Double,Double> position = calculatePosition(p,newAngle,time);

                newParticles.add(new Particle(p.getId(), position.first, position.second, 0,VELOCITY,newAngle));
            }
            particlesPerTime.putIfAbsent(time,newParticles);
        }
        return particlesPerTime;
    }

    public Map<Integer, Double> orderPerTime(Map<Integer, List<Particle>> particlesPerTime) {
        Map<Integer, Double> map = new HashMap<>();
        for (int i = 0; i < particlesPerTime.keySet().size(); i++) {
            map.put(i, calculateOrderParameter(particlesPerTime.get(i)));
        }
        return map;
    }

    public double calculateOrderParameter(List<Particle> particles){
        double vxSum = 0;
        double vySum = 0;

        // Sumar las componentes x e y de todas las velocidades
        for (Particle p : particles) {
            vxSum += p.getVel() * Math.cos(p.getAngle());
            vySum += p.getVel() * Math.sin(p.getAngle());
        }

        double avgVx = vxSum / particles.size();
        double avgVy = vySum / particles.size();
        double va = Math.sqrt(Math.pow(avgVx, 2) + Math.pow(avgVy, 2));

        return va / VELOCITY;
    }
    private Pair<Double,Double> calculatePosition(Particle p , double newAngle, int time){
        double dt = 1;
        double vx = VELOCITY * Math.cos(newAngle);
        double vy = VELOCITY * Math.sin(newAngle);

        double newX = p.getPosX();
        double newY;

        if (p.getPosX() > L ){
            newX = 0;
        } else if (p.getPosX() < 0){
            newX = L;
        }

        if (p.getPosY() > L ){
            newY = 0;
        } else if (p.getPosY() < 0){
            newY = L;
        } else {
            newX += vx * dt;
            newY = p.getPosY() + vy * dt;
        }

        return new Pair<>(newX,newY);
    }

    class Pair<U,T> {
        private U first;
        private T second;

        public Pair(U first, T second){
            this.first = first;
            this.second = second;
        }

        public U getFirst() {
            return first;
        }

        public T getSecond() {
            return second;
        }
    }


}
