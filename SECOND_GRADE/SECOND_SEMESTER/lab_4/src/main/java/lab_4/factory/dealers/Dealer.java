package lab_4.factory.dealers;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

import lab_4.factory.controller.FactoryController;
import lab_4.factory.model.Car;
import lab_4.factory.storage.Storage;

public class Dealer implements Runnable {
    private static final String LOG_DIR = "logs";
    private static final String LOG_FILE = LOG_DIR + "/factory.log";

    private final Storage<Car> carStorage;
    private final int dealerId;
    private int delay;
    private final boolean logEnabled;
    private final FactoryController controller;
    private int soldCars = 0;

    public void setDelay(int delay) {this.delay = delay; }
    public int getDelay() {return delay; }
    public int getSoldCarsCount() {return soldCars; }

    public Dealer(Storage<Car> carStorage, int dealerId, int delay, boolean logEnabled, FactoryController controller) {
        this.carStorage = carStorage;
        this.dealerId = dealerId;
        this.delay = delay;
        this.logEnabled = logEnabled;
        this.controller = controller;

        File logDir = new File(LOG_DIR);
        if (!logDir.exists())
            logDir.mkdir();
    }

    @Override
    public void run() {
        try {
            while (!Thread.currentThread().isInterrupted()) {
                Car car = carStorage.take();
                soldCars++;

                if (logEnabled)
                    logSale(car);

                controller.notifySale();
                Thread.sleep(delay);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private void logSale(Car car) {
        String time = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
        String logEntry = String.format("%s: Dealer %d: Car %d (Body: %d, Motor: %d, Accessory: %d)%n",
                time, dealerId, car.getId(), car.getBody().getId(), car.getMotor().getId(), car.getAccessory().getId());

        try (FileWriter writer = new FileWriter(LOG_FILE, true)) {
            writer.write(logEntry);
        } catch (IOException e) {
            System.err.println("Error writing to log file: " + e.getMessage());
        }
    }
}