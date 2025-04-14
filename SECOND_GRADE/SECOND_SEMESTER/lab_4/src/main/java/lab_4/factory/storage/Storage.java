package lab_4.factory.storage;

import java.util.LinkedList;
import java.util.Queue;

public class Storage<T> {
    private int capacity;
    private final Queue<T> items = new LinkedList<>();

    public Storage(int capacity) {this.capacity = capacity; }
    public int getCapacity() {return capacity; }
    public synchronized int getSize() {return items.size(); }

    public synchronized void put(T item) throws InterruptedException {
            while (items.size() >= capacity)
                wait();

            items.add(item);
            notifyAll();
    }

    public synchronized T take() throws InterruptedException {
            while (items.isEmpty())
                wait();

            T item = items.poll();
            notifyAll();
            return item;
    }

    public synchronized void setCapacity(int newCapacity) {
            this.capacity = newCapacity;
            notifyAll();
    }
}