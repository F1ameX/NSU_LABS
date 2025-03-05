package lab_4.factory.model;
import java.util.concurrent.atomic.AtomicInteger;

public class Car {
    private static final AtomicInteger counter = new AtomicInteger(0);
    private final int id;
    private final Body body;
    private final Motor motor;
    private final Accessory accessory;

    public Car(Body body, Motor motor, Accessory accessory) {
        this.id = counter.incrementAndGet();
        this.body = body;
        this.motor = motor;
        this.accessory = accessory;
    }

    public int getId() {return id; }
    public Body getBody() {return body; }
    public Motor getMotor() {return motor; }
    public Accessory getAccessory() {return accessory; }

    @Override
    public String toString() { return "Car " + id +
            " (Body: " + body.getId() +
            ", Motor: " + motor.getId() +
            ", Accessory: " + accessory.getId() + ")";}
}