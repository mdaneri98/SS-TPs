import models.Field;
import models.Position;

public class Main {

	public static void main(String args[]) {
		
		double blueVelocityMax = 3.8;
		double redVelocityMax = 4.0;
		
		double blueTau = 0.3;
		double redTau = 0.5;
		
		double rMin = 0.15;
		double rMax = 0.32;
		
		int N = 1;
		
		Field field = new Field(10, 7, new Position(0, 7/2.0));
		
		TryMaradoniano tm = new TryMaradoniano(N, field, blueVelocityMax, redVelocityMax, blueTau, redTau, rMin, rMax);
		
		tm.run();
		
		
	}
	
}
