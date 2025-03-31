package lab_4.factory.model;
import java.util.concurrent.atomic.AtomicInteger;

public abstract class Part {
    private static final AtomicInteger idCounter = new AtomicInteger(0);
    private final int id;

    public Part() { this.id = idCounter.incrementAndGet(); }
    public int getId() { return id;}
}