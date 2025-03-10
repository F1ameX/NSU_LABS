package lab_4.factory.supplier;
import lab_4.factory.model.Body;
import lab_4.factory.storage.BodyStorage;

public class BodySupplier extends Supplier<Body> {
    public BodySupplier(BodyStorage storage, int delay) { super(storage, delay); }

    @Override
    public Body createItem() { return new Body(); }
}