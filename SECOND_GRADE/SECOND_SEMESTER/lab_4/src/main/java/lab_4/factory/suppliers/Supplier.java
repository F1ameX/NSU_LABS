package lab_4.factory.suppliers;

import lab_4.factory.storage.Storage;
import lab_4.factory.model.Part;

public class Supplier<T extends Part> implements Runnable {
    private final Storage<T> storage;
    private final Class<T> partType;
    private int delay;
    private int suppliedCount;

    public void setDelay(int delay) {this.delay = delay; }
    public int getDelay() {return delay; }
    public int getSuppliedCount() {return suppliedCount; }

    public Supplier(Storage<T> storage, Class<T> partType, int delay) {
        this.storage = storage;
        this.partType = partType;
        this.delay = delay;
        this.suppliedCount = 0;
    }

    @Override
    public void run() {
        try {
            while (!Thread.currentThread().isInterrupted()) {
                T part = partType.getDeclaredConstructor().newInstance();
                storage.put(part);
                suppliedCount++;
                Thread.sleep(delay);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}