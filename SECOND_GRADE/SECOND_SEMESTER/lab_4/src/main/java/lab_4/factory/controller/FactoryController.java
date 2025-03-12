package lab_4.factory.controller;
import lab_4.factory.storage.CarStorage;
import lab_4.factory.threadpool.ThreadPool;
import lab_4.factory.worker.Worker;
import lab_4.factory.storage.BodyStorage;
import lab_4.factory.storage.MotorStorage;
import lab_4.factory.storage.AccessoryStorage;

public class FactoryController extends Thread {
    private final CarStorage carStorage;
    private final BodyStorage bodyStorage;
    private final MotorStorage motorStorage;
    private final AccessoryStorage accessoryStorage;
    private final ThreadPool threadPool;
    private final int minCarsThreshold;
    private final int checkInterval;
    private boolean running = true;

    public FactoryController(CarStorage carStorage, BodyStorage bodyStorage, MotorStorage motorStorage,
                             AccessoryStorage accessoryStorage, ThreadPool threadPool, int minCarsThreshold, int checkInterval) {
        this.carStorage = carStorage;
        this.bodyStorage = bodyStorage;
        this.motorStorage = motorStorage;
        this.accessoryStorage = accessoryStorage;
        this.threadPool = threadPool;
        this.minCarsThreshold = minCarsThreshold;
        this.checkInterval = checkInterval;
    }

    @Override
    public void run() {
        try {
            while (running) {
                if (carStorage.getSize() < minCarsThreshold)
                    threadPool.execute(new Worker(bodyStorage, motorStorage, accessoryStorage, carStorage));
                Thread.sleep(checkInterval);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public void stopController() {
        running = false;
        this.interrupt();
    }
}