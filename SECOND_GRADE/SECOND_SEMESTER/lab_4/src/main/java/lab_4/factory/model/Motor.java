package lab_4.factory.model;
import java.util.concurrent.atomic.AtomicInteger;

public class Motor {
    private static final AtomicInteger counter = new AtomicInteger(0);
    private final int id;

    public Motor() { this.id = counter.incrementAndGet(); }
    public int getId() { return id; }

    @Override
    public String toString() { return "Motor " + id; }
}