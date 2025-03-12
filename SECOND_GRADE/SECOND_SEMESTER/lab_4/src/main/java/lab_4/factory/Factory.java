package lab_4.factory;
import lab_4.factory.storage.*;
import lab_4.factory.supplier.*;
import lab_4.factory.threadpool.*;
import lab_4.factory.dealer.*;
import lab_4.factory.logger.*;
import lab_4.factory.controller.*;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Factory {
    private final Logger logger;
    private final FactoryController factoryController;
    private final List<Supplier<?>> suppliers = new ArrayList<>();
    private final List<Dealer> dealers = new ArrayList<>();
    private final ThreadPool threadPool;

    public Factory(int bodyCapacity, int motorCapacity, int accessoryCapacity, int carCapacity,
                   int bodySupplierDelay, int motorSupplierDelay, int accessorySupplierDelay,
                   int accessorySuppliers, int numWorkers, int numDealers, int dealerDelay,
                   String logFileName, boolean logEnabled, int minCarsThreshold, int checkInterval) throws IOException {
        BodyStorage bodyStorage = new BodyStorage(bodyCapacity);
        MotorStorage motorStorage = new MotorStorage(motorCapacity);
        AccessoryStorage accessoryStorage = new AccessoryStorage(accessoryCapacity);
        CarStorage carStorage = new CarStorage(carCapacity);
        this.logger = new Logger(logFileName, logEnabled);
        this.threadPool = new ThreadPool(numWorkers);
        this.factoryController = new FactoryController(carStorage, bodyStorage, motorStorage, accessoryStorage, threadPool, minCarsThreshold, checkInterval);

        suppliers.add(new BodySupplier(bodyStorage, bodySupplierDelay));
        suppliers.add(new MotorSupplier(motorStorage, motorSupplierDelay));

        for (int i = 0; i < accessorySuppliers; i++)
            suppliers.add(new AccessorySupplier(accessoryStorage, accessorySupplierDelay));

        for (int i = 0; i < numDealers; i++)
            dealers.add(new Dealer(carStorage, i + 1, dealerDelay, logger));
    }

    public void start() {
        System.out.println("Factory is starting...");

        for (Supplier<?> supplier : suppliers)
            supplier.start();

        factoryController.start();
        for (Dealer dealer : dealers)
            dealer.start();
    }

    public void stop() {
        for (Supplier<?> supplier : suppliers)
            supplier.stopSupplier();

        threadPool.shutdown();
        for (Dealer dealer : dealers)
            dealer.stopDealer();

        factoryController.stopController();
        logger.close();
    }

    public static void main(String[] args) {
        try {
            Factory factory = new Factory(100, 100, 100,
                    100, 500, 700,
                    1000, 3, 5,
                    3, 2000, "factory.log",
                    true, 5, 1000);
            factory.start();

            Thread.sleep(10000);

            factory.stop();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}