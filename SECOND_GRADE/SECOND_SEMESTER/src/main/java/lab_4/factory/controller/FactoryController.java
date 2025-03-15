package lab_4.factory.controller;
import lab_4.factory.config.ConfigReader;
import lab_4.factory.logging.FactoryLogger;
import lab_4.factory.model.*;
import lab_4.factory.storage.Storage;
import lab_4.factory.suppliers.Supplier;
import lab_4.factory.workers.Worker;
import lab_4.factory.dealers.Dealer;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class FactoryController {
    private final Storage<Body> bodyStorage;
    private final Storage<Motor> motorStorage;
    private final Storage<Accessory> accessoryStorage;
    private final Storage<Car> carStorage;

    private final List<Thread> bodySuppliers = new ArrayList<>();
    private final List<Thread> motorSuppliers = new ArrayList<>();
    private final List<Thread> accessorySuppliers = new ArrayList<>();
    private final List<Thread> dealers = new ArrayList<>();
    private ExecutorService workerPool;

    private final AtomicInteger producedCars = new AtomicInteger(0);
    private volatile int supplierDelay;
    private volatile int dealerDelay;

    private final int numSuppliers;
    private final int numWorkers;
    private final int numDealers;

    public synchronized void setSupplierDelay(int delay) {
        this.supplierDelay = delay;
        System.out.println("Updated Supplier Delay: " + delay);
    }

    public synchronized void setDealerDelay(int delay) {
        this.dealerDelay = delay;
        System.out.println("Updated Dealer Delay: " + delay);
    }

    public int getSupplierDelay() {return supplierDelay; }

    public int getDealerDelay() {return dealerDelay; }

    public FactoryController(String configPath) {
        ConfigReader config = new ConfigReader(configPath);

        int bodyCapacity = config.getInt("StorageBodySize", 100);
        int motorCapacity = config.getInt("StorageMotorSize", 100);
        int accessoryCapacity = config.getInt("StorageAccessorySize", 100);
        int carCapacity = config.getInt("StorageAutoSize", 100);
        numSuppliers = config.getInt("AccessorySuppliers", 5);
        numWorkers = config.getInt("Workers", 10);
        numDealers = config.getInt("Dealers", 20);
        supplierDelay = config.getInt("SupplierDelay", 500);
        dealerDelay = config.getInt("DealerDelay", 1000);
        boolean logSale = config.getBoolean("LogSale", true);

        FactoryLogger.setLoggingEnabled(logSale);

        this.bodyStorage = new Storage<>(bodyCapacity);
        this.motorStorage = new Storage<>(motorCapacity);
        this.accessoryStorage = new Storage<>(accessoryCapacity);
        this.carStorage = new Storage<>(carCapacity);
    }

    public void start() {
        stop();

        bodySuppliers.clear();
        motorSuppliers.clear();
        accessorySuppliers.clear();
        dealers.clear();

        workerPool = Executors.newFixedThreadPool(numWorkers);

        for (int i = 0; i < numSuppliers; i++) {
            Supplier<Body> bodySupplier = new Supplier<>(bodyStorage, Body.class, this);
            Supplier<Motor> motorSupplier = new Supplier<>(motorStorage, Motor.class, this);
            Supplier<Accessory> accessorySupplier = new Supplier<>(accessoryStorage, Accessory.class, this);

            Thread bodyThread = new Thread(bodySupplier);
            Thread motorThread = new Thread(motorSupplier);
            Thread accessoryThread = new Thread(accessorySupplier);

            bodySuppliers.add(bodyThread);
            motorSuppliers.add(motorThread);
            accessorySuppliers.add(accessoryThread);

            bodyThread.start();
            motorThread.start();
            accessoryThread.start();
        }

        for (int i = 0; i < numWorkers; i++)
            workerPool.submit(new Worker(bodyStorage, motorStorage, accessoryStorage, carStorage, this));

        for (int i = 0; i < numDealers; i++) {
            Dealer dealer = new Dealer(carStorage, this);
            Thread dealerThread = new Thread(dealer);
            dealers.add(dealerThread);
            dealerThread.start();
        }
    }

    public void stop() {
        bodySuppliers.forEach(Thread::interrupt);
        motorSuppliers.forEach(Thread::interrupt);
        accessorySuppliers.forEach(Thread::interrupt);
        dealers.forEach(Thread::interrupt);

        if (workerPool != null) workerPool.shutdownNow();
    }

    public synchronized String getStorageStatus() {
        return String.format("Body: %d | Motor: %d | Accessory: %d | Cars: %d",
                bodyStorage.getSize(), motorStorage.getSize(), accessoryStorage.getSize(), carStorage.getSize());
    }

    public void incrementProducedCars() {producedCars.incrementAndGet(); }
    public int getProducedCars() {return producedCars.get(); }
}