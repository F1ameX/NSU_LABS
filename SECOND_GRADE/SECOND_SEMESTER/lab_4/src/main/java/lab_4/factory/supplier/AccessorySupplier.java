package lab_4.factory.supplier;
import lab_4.factory.model.Accessory;
import lab_4.factory.storage.AccessoryStorage;

public class AccessorySupplier extends Supplier<Accessory> {
    public AccessorySupplier(AccessoryStorage storage, int delay) { super(storage, delay); }

    @Override
    public Accessory createItem() { return new Accessory(); }
}