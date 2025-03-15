package lab_4.factory.dealers;
import lab_4.factory.storage.Storage;
import lab_4.factory.model.Car;
import lab_4.factory.logging.FactoryLogger;
import lab_4.factory.controller.FactoryController;

public class Dealer implements Runnable {
    private final Storage<Car> carStorage;
    private final FactoryController controller;
    private static int dealerCounter = 0;
    private final int dealerId;
    private boolean running = true;

    public Dealer(Storage<Car> carStorage, FactoryController controller) {
        this.carStorage = carStorage;
        this.controller = controller;
        this.dealerId = ++dealerCounter;
    }

    public void stop() {running = false; }

    @Override
    public void run() {
        try {
            while (running) {
                Car car = carStorage.take();
                FactoryLogger.logSale(dealerId, car.getId(),
                        car.getBody().getId(), car.getMotor().getId(), car.getAccessory().getId());

                controller.incrementProducedCars();
                Thread.sleep(controller.getDealerDelay());
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}