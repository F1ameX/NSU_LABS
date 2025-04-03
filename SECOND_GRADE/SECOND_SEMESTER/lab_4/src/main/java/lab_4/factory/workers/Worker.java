package lab_4.factory.workers;

import lab_4.factory.storage.Storage;
import lab_4.factory.model.*;

public class Worker implements Runnable {
    private final Storage<Body> bodyStorage;
    private final Storage<Motor> motorStorage;
    private final Storage<Accessory> accessoryStorage;
    private final Storage<Car> carStorage;

    public Worker(Storage<Body> bodyStorage, Storage<Motor> motorStorage, Storage<Accessory> accessoryStorage, Storage<Car> carStorage) {
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
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}