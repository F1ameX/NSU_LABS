package lab_4.factory.exceptions;

public class StorageEmptyException extends FactoryException {
    public StorageEmptyException(String storageName) {
        super("Storage " + storageName + " is empty.");
    }
}