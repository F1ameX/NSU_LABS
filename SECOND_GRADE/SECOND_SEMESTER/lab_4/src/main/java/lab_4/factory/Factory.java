package lab_4.factory;

import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import javax.swing.*;

import lab_4.factory.config.ConfigReader;
import lab_4.factory.controller.FactoryController;
import lab_4.factory.dealers.Dealer;
import lab_4.factory.gui.FactoryView;
import lab_4.factory.model.*;
import lab_4.factory.storage.Storage;
import lab_4.factory.suppliers.Supplier;
import lab_4.factory.workers.ThreadPool;

public class Factory {

    public static void startFactory() {
        Properties config = ConfigReader.loadConfig();

        int bodyStorageCapacity = Integer.parseInt(config.getProperty("StorageBodySize"));
        int motorStorageCapacity = Integer.parseInt(config.getProperty("StorageMotorSize"));
        int accessoryStorageCapacity = Integer.parseInt(config.getProperty("StorageAccessorySize"));
        int carStorageCapacity = Integer.parseInt(config.getProperty("StorageAutoSize"));
        int supplierBodyDelay = Integer.parseInt(config.getProperty("SupplierBodyDelay"));
        int supplierMotorDelay = Integer.parseInt(config.getProperty("SupplierMotorDelay"));
        int supplierAccessoryDelay = Integer.parseInt(config.getProperty("SupplierAccessoryDelay"));
        int dealerDelay = Integer.parseInt(config.getProperty("DealerDelay"));
        int threadPoolSize = Integer.parseInt(config.getProperty("Workers"));
        int dealerCount = Integer.parseInt(config.getProperty("Dealers"));

        Storage<Body> bodyStorage = new Storage<>(bodyStorageCapacity);
        Storage<Motor> motorStorage = new Storage<>(motorStorageCapacity);
        Storage<Accessory> accessoryStorage = new Storage<>(accessoryStorageCapacity);
        Storage<Car> carStorage = new Storage<>(carStorageCapacity);

        Supplier<Body> bodySupplier = new Supplier<>(bodyStorage, Body.class, supplierBodyDelay);
        Supplier<Motor> motorSupplier = new Supplier<>(motorStorage, Motor.class, supplierMotorDelay);
        Supplier<Accessory> accessorySupplier = new Supplier<>(accessoryStorage, Accessory.class, supplierAccessoryDelay);

        Thread bodySupplierThread = new Thread(bodySupplier);
        Thread motorSupplierThread = new Thread(motorSupplier);
        Thread accessorySupplierThread = new Thread(accessorySupplier);

        bodySupplierThread.start();
        motorSupplierThread.start();
        accessorySupplierThread.start();

        ThreadPool threadPool = new ThreadPool(threadPoolSize);

        FactoryController factoryController = new FactoryController(carStorage, bodyStorage, motorStorage, accessoryStorage, threadPool);
        Thread factoryControllerThread = new Thread(factoryController);
        factoryControllerThread.start();

        List<Dealer> dealers = new ArrayList<>();
        for (int i = 0; i < dealerCount; i++)
            dealers.add(new Dealer(carStorage, i + 1, dealerDelay, true, factoryController));

        for (Dealer dealer : dealers) {
            Thread dealerThread = new Thread(dealer);
            dealerThread.start();
        }

        SwingUtilities.invokeLater(() -> new FactoryView(bodyStorage, motorStorage, accessoryStorage, carStorage, bodySupplier, motorSupplier, accessorySupplier, dealers, threadPool, factoryController).setVisible(true));
    }
}