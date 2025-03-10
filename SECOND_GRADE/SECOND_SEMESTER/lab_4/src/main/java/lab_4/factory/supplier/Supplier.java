package lab_4.factory.supplier;
import lab_4.factory.storage.Storage;

public abstract class Supplier<T> extends Thread {
    private final Storage<T> storage;
    private final int delay;
    private boolean running = true;

    public Supplier(Storage<T> storage, int delay) {
        this.storage = storage;
        this.delay = delay;
    }

    public abstract T createItem();

    @Override
    public void run() {
        try {
            while (running) {
                T item = createItem();
                storage.put(item);
                Thread.sleep(delay);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public void stopSupplier() {
        running = false;
        this.interrupt();
    }
}