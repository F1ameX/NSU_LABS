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

    private final List<Supplier<Body>> bodySuppliers = new ArrayList<>();
    private final List<Supplier<Motor>> motorSuppliers = new ArrayList<>();
    private final List<Supplier<Accessory>> accessorySuppliers = new ArrayList<>();
    private final List<Dealer> dealers = new ArrayList<>();
    private ExecutorService workerPool;

    private final AtomicInteger producedCars = new AtomicInteger(0);
    private volatile int supplierBodyDelay;
    private volatile int supplierMotorDelay;
    private volatile int supplierAccessoryDelay;
    private volatile int dealerDelay;

    private final int numSuppliers;
    private final int numWorkers;
    private final int numDealers;

    public synchronized void setSupplierBodyDelay(int delay) {
        this.supplierBodyDelay = delay;
        System.out.println("Updated Supplier Body Delay: " + delay);
        updateSuppliers();
    }

    public synchronized void setSupplierMotorDelay(int delay) {
        this.supplierMotorDelay = delay;
        System.out.println("Updated Supplier Motor Delay: " + delay);
        updateSuppliers();
    }

    public synchronized void setSupplierAccessoryDelay(int delay) {
        this.supplierAccessoryDelay = delay;
        System.out.println("Updated Supplier Accessory Delay: " + delay);
        updateSuppliers();
    }

    public synchronized void setDealerDelay(int delay) {
        this.dealerDelay = delay;
        System.out.println("Updated Dealer Delay: " + delay);
        updateDealers();
    }

    public FactoryController(String configPath) {
        ConfigReader config = new ConfigReader(configPath);

        int bodyCapacity = config.getInt("StorageBodySize", 100);
        int motorCapacity = config.getInt("StorageMotorSize", 100);
        int accessoryCapacity = config.getInt("StorageAccessorySize", 100);
        int carCapacity = config.getInt("StorageAutoSize", 100);
        numSuppliers = config.getInt("AccessorySuppliers", 5);
        numWorkers = config.getInt("Workers", 10);
        numDealers = config.getInt("Dealers", 20);
        supplierBodyDelay = config.getInt("SupplierBodyDelay", 500);
        supplierMotorDelay = config.getInt("SupplierMotorDelay", 500);
        supplierAccessoryDelay = config.getInt("SupplierAccessoryDelay", 500);
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
            Supplier<Body> bodySupplier = new Supplier<>(bodyStorage, Body.class, supplierBodyDelay);
            Supplier<Motor> motorSupplier = new Supplier<>(motorStorage, Motor.class, supplierMotorDelay);
            Supplier<Accessory> accessorySupplier = new Supplier<>(accessoryStorage, Accessory.class, supplierAccessoryDelay);

            bodySuppliers.add(bodySupplier);
            motorSuppliers.add(motorSupplier);
            accessorySuppliers.add(accessorySupplier);

            new Thread(bodySupplier).start();
            new Thread(motorSupplier).start();
            new Thread(accessorySupplier).start();
        }

        for (int i = 0; i < numWorkers; i++) {
            workerPool.submit(new Worker(bodyStorage, motorStorage, accessoryStorage, carStorage, this));
        }

        for (int i = 0; i < numDealers; i++) {
            Dealer dealer = new Dealer(carStorage, this);
            dealers.add(dealer);
            new Thread(dealer).start();
        }
    }

    public void stop() {
        bodySuppliers.forEach(supplier -> supplier.stop());
        motorSuppliers.forEach(supplier -> supplier.stop());
        accessorySuppliers.forEach(supplier -> supplier.stop());
        dealers.forEach(Dealer::stop);

        if (workerPool != null) {
            workerPool.shutdownNow();
        }
    }

    public synchronized String getStorageStatus() {
        return String.format("Body: %d | Motor: %d | Accessory: %d | Cars: %d",
                bodyStorage.getSize(), motorStorage.getSize(), accessoryStorage.getSize(), carStorage.getSize());
    }

    public void incrementProducedCars() {
        producedCars.incrementAndGet();
    }

    public int getProducedCars() {
        return producedCars.get();
    }

    public int getSupplierBodyDelay() {
        return supplierBodyDelay;
    }

    public int getSupplierMotorDelay() {
        return supplierMotorDelay;
    }

    public int getSupplierAccessoryDelay() {
        return supplierAccessoryDelay;
    }

    public int getDealerDelay() {
        return dealerDelay;
    }

    private void updateSuppliers() {
        for (Supplier<Body> bodySupplier : bodySuppliers) {
            bodySupplier.setDelay(supplierBodyDelay);
        }
        for (Supplier<Motor> motorSupplier : motorSuppliers) {
            motorSupplier.setDelay(supplierMotorDelay);
        }
        for (Supplier<Accessory> accessorySupplier : accessorySuppliers) {
            accessorySupplier.setDelay(supplierAccessoryDelay);
        }
    }

    private void updateDealers() {
        for (Dealer dealer : dealers) {
            dealer.setDelay(dealerDelay);
        }
    }
}