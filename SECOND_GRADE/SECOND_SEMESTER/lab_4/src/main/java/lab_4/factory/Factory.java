package lab_4.factory;
import lab_4.factory.storage.*;
import lab_4.factory.supplier.*;
import java.util.ArrayList;
import java.util.List;

public class Factory {
    private final BodyStorage bodyStorage;
    private final MotorStorage motorStorage;
    private final AccessoryStorage accessoryStorage;
    private final CarStorage carStorage;

    private final List<Supplier<?>> suppliers = new ArrayList<>();

    public Factory(int bodyCapacity, int motorCapacity, int accessoryCapacity, int carCapacity,
                   int bodySupplierDelay, int motorSupplierDelay, int accessorySupplierDelay, int accessorySuppliers) {
        this.bodyStorage = new BodyStorage(bodyCapacity);
        this.motorStorage = new MotorStorage(motorCapacity);
        this.accessoryStorage = new AccessoryStorage(accessoryCapacity);
        this.carStorage = new CarStorage(carCapacity);

        suppliers.add(new BodySupplier(bodyStorage, bodySupplierDelay));
        suppliers.add(new MotorSupplier(motorStorage, motorSupplierDelay));

        for (int i = 0; i < accessorySuppliers; i++)
            suppliers.add(new AccessorySupplier(accessoryStorage, accessorySupplierDelay));
    }

    public void start() {
        System.out.println("Factory is starting...");
        for (Supplier<?> supplier : suppliers) supplier.start();
    }

    public void stop() {
        for (Supplier<?> supplier : suppliers) supplier.stopSupplier();
    }

    public static void main(String[] args) {
        Factory factory = new Factory(100, 100, 100, 100, 500, 700, 1000, 3);
        factory.start();

        try {
            Thread.sleep(5000); // Фабрика работает 5 секунд для теста
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        factory.stop();
    }
}