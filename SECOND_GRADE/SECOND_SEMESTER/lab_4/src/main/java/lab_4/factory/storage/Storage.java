package lab_4.factory.storage;

import java.util.LinkedList;
import java.util.Queue;

public abstract class Storage<T> {
    private final Queue<T> storage;
    private final int capacity;

    public Storage(int capacity) {
        this.capacity = capacity;
        this.storage = new LinkedList<>();
    }

    public synchronized void put(T item) throws InterruptedException {
        while (storage.size() >= capacity) wait();

        storage.add(item);
        notifyAll();
    }

    public synchronized T take() throws InterruptedException {
        while (storage.isEmpty()) wait();

        T item = storage.poll();
        notifyAll();
        return item;
    }

    public synchronized int getSize() { return storage.size(); }
    public int getCapacity() { return capacity; }
}