package lab_4.factory.worker;
import lab_4.factory.model.Body;
import lab_4.factory.model.Motor;
import lab_4.factory.model.Accessory;
import lab_4.factory.model.Car;
import lab_4.factory.storage.BodyStorage;
import lab_4.factory.storage.MotorStorage;
import lab_4.factory.storage.AccessoryStorage;
import lab_4.factory.storage.CarStorage;

public class Worker implements Runnable {
    private final BodyStorage bodyStorage;
    private final MotorStorage motorStorage;
    private final AccessoryStorage accessoryStorage;
    private final CarStorage carStorage;

    public Worker(BodyStorage bodyStorage, MotorStorage motorStorage, AccessoryStorage accessoryStorage, CarStorage carStorage) {
        this.bodyStorage = bodyStorage;
        this.motorStorage = motorStorage;
        this.accessoryStorage = accessoryStorage;
        this.carStorage = carStorage;
    }

    @Override
    public void run() {
        try {
            while (!Thread.currentThread().isInterrupted()) {
                Body body = bodyStorage.take();
                Motor motor = motorStorage.take();
                Accessory accessory = accessoryStorage.take();

                Car car = new Car(body, motor, accessory);
                carStorage.put(car);

                System.out.println("Worker assembled: " + car);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}