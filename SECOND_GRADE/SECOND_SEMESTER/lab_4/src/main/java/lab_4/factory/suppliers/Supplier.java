package lab_4.factory.suppliers;

import lab_4.factory.storage.Storage;
import lab_4.factory.model.Part;

public class Supplier<T extends Part> implements Runnable {
    private final Storage<T> storage;
    private final Class<T> partClass;
    private volatile int delay;
    private boolean running = true;

    public Supplier(Storage<T> storage, Class<T> partClass, int delay) {
        this.storage = storage;
        this.partClass = partClass;
        this.delay = delay;
    }

    public synchronized void setDelay(int delay) {
        this.delay = delay;
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
                Thread.sleep(delay); // Используем динамическую задержку
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}