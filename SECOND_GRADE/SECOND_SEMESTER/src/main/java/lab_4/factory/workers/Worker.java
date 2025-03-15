package lab_4.factory.workers;
import lab_4.factory.model.Body;
import lab_4.factory.model.Motor;
import lab_4.factory.model.Accessory;
import lab_4.factory.model.Car;
import lab_4.factory.storage.Storage;
import lab_4.factory.controller.FactoryController;

public class Worker implements Runnable {
    private final Storage<Body> bodyStorage;
    private final Storage<Motor> motorStorage;
    private final Storage<Accessory> accessoryStorage;
    private final Storage<Car> carStorage;
    private final FactoryController controller;

    public Worker(Storage<Body> bodyStorage, Storage<Motor> motorStorage,
                  Storage<Accessory> accessoryStorage, Storage<Car> carStorage,
                  FactoryController controller) {
        this.bodyStorage = bodyStorage;
        this.motorStorage = motorStorage;
        this.accessoryStorage = accessoryStorage;
        this.carStorage = carStorage;
        this.controller = controller;
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
                controller.incrementProducedCars();

                System.out.println("Worker assembled a car! " +
                        "Body: " + body.getId() + ", Motor: " + motor.getId() + ", Accessory: " + accessory.getId() +
                        " | Cars in storage: " + carStorage.getSize());
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}