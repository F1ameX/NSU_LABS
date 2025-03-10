package lab_4.factory.supplier;
import lab_4.factory.model.Motor;
import lab_4.factory.storage.MotorStorage;

public class MotorSupplier extends Supplier<Motor> {
    public MotorSupplier(MotorStorage storage, int delay) { super(storage, delay); }

    @Override
    public Motor createItem() { return new Motor(); }
}