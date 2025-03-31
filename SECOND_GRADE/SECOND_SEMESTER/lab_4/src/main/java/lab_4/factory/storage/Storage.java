package lab_4.factory.storage;
import java.util.LinkedList;
import java.util.Queue;

public class Storage<T> {
    private final int capacity;
    private final Queue<T> storage = new LinkedList<>();

    public Storage(int capacity) {this.capacity = capacity; }
    public synchronized int getSize() {return storage.size(); }
    public synchronized boolean isFull() {return storage.size() >= capacity; }
    public synchronized boolean isEmpty() {return storage.isEmpty(); }

    public synchronized void put(T item) throws InterruptedException {
        while (storage.size() >= capacity) { wait(); }
        storage.add(item);
        notifyAll();
    }

    public synchronized T take() throws InterruptedException {
        while (storage.isEmpty()) { wait(); }
        T item = storage.poll();
        notifyAll();
        return item;
    }
}