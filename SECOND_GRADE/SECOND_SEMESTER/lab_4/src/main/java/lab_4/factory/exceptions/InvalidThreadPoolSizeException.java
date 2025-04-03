package lab_4.factory.exceptions;

public class InvalidThreadPoolSizeException extends FactoryException {
    public InvalidThreadPoolSizeException(int size) {
        super("Error: Invalid thread pool size: " + size + ". The value must be greater than zero.");
    }
}