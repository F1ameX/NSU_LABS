package lab_4.factory;
import lab_4.factory.storage.*;

public class Factory {
    private final BodyStorage bodyStorage;
    private final MotorStorage motorStorage;
    private final AccessoryStorage accessoryStorage;
    private final CarStorage carStorage;

    public Factory(int bodyCapacity, int motorCapacity, int accessoryCapacity, int carCapacity) {
        this.bodyStorage = new BodyStorage(bodyCapacity);
        this.motorStorage = new MotorStorage(motorCapacity);
        this.accessoryStorage = new AccessoryStorage(accessoryCapacity);
        this.carStorage = new CarStorage(carCapacity);
    }

    public void start() {
        System.out.println("Factory is starting...");
        System.out.println("Body Storage Capacity: " + bodyStorage.getCapacity());
        System.out.println("Motor Storage Capacity: " + motorStorage.getCapacity());
        System.out.println("Accessory Storage Capacity: " + accessoryStorage.getCapacity());
        System.out.println("Car Storage Capacity: " + carStorage.getCapacity());
    }

    public static void main(String[] args) {
        Factory factory = new Factory(100, 100, 100, 100);
        factory.start();
    }
}