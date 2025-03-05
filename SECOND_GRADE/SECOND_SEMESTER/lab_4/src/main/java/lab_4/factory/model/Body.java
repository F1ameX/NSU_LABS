package lab_4.factory.model;
import java.util.concurrent.atomic.AtomicInteger;

public class Body {
    private static final AtomicInteger counter = new AtomicInteger(0);
    private final int id;

    public Body() { this.id = counter.incrementAndGet(); }
    public int getId() { return id; }

    @Override
    public String toString() { return "Body " + id; }
}