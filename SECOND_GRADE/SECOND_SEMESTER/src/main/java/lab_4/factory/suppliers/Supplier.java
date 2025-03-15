package lab_4.factory.suppliers;
import lab_4.factory.storage.Storage;
import lab_4.factory.model.Part;
import lab_4.factory.controller.FactoryController;

public class Supplier<T extends Part> implements Runnable {
    private final Storage<T> storage;
    private final Class<T> partClass;
    private final FactoryController controller;
    private boolean running = true;

    public Supplier(Storage<T> storage, Class<T> partClass, FactoryController controller) {
        this.storage = storage;
        this.partClass = partClass;
        this.controller = controller;
    }

    public void stop() {
        running = false;
    }

    @Override
    public void run() {
        try {
            while (running) {
                T part = partClass.getDeclaredConstructor().newInstance();
                storage.put(part);
                System.out.println("Supplier added: " + part.getClass().getSimpleName() +
                        " | Storage size: " + storage.getSize());
                Thread.sleep(controller.getSupplierDelay()); // Теперь читаем актуальную задержку
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}