package lab_4.factory.dealer;
import lab_4.factory.model.Car;
import lab_4.factory.storage.CarStorage;
import lab_4.factory.logger.Logger;

public class Dealer extends Thread {
    private final CarStorage carStorage;
    private final Logger logger;
    private final int dealerId;
    private final int delay;
    private boolean running = true;

    public Dealer(CarStorage carStorage, int dealerId, int delay, Logger logger) {
        this.carStorage = carStorage;
        this.dealerId = dealerId;
        this.delay = delay;
        this.logger = logger;
    }

    @Override
    public void run() {
        try {
            while (running) {
                Car car = carStorage.take();
                long timestamp = System.currentTimeMillis();
                System.out.println(timestamp + ": Dealer " + dealerId + " sold Car " + car.getId());
                logger.log(dealerId, car.getId(), car.getBody().getId(), car.getMotor().getId(), car.getAccessory().getId());
                Thread.sleep(delay);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public void stopDealer() {
        running = false;
        this.interrupt();
    }
}