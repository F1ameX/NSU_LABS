package lab_2.calculator.exceptions;

public class DivisionByZeroException extends RuntimeException {
    public DivisionByZeroException(String message) { super(message); }
}