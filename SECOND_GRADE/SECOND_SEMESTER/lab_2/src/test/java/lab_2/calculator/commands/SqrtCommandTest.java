package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.InvalidArgumentException;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class SqrtCommandTest {
    private ExecutionContext context;
    private SqrtCommand sqrtCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        sqrtCommand = new SqrtCommand();
    }

    @Test
    void testSqrtValidNumber() {
        context.push(9.0);
        sqrtCommand.execute(context, List.of());
        assertEquals(3.0, context.pop(), 0.0001, "SQRT of 9 should be 3");
    }

    @Test
    void testSqrtZero() {
        context.push(0.0);
        sqrtCommand.execute(context, List.of());
        assertEquals(0.0, context.pop(), 0.0001, "SQRT of 0 should be 0");
    }

    @Test
    void testSqrtNegativeNumberThrowsException() {
        context.push(-4.0);
        Exception exception = assertThrows(InvalidArgumentException.class,
                () -> sqrtCommand.execute(context, List.of()));
        assertTrue(exception.getMessage().contains("Cannot calculate the square root of a negative number"),
                "Should throw an exception for negative input.");
    }

    @Test
    void testSqrtEmptyStackThrowsException() {
        Exception exception = assertThrows(StackUnderflowException.class,
                () -> sqrtCommand.execute(context, List.of()));
        assertNotNull(exception, "Exception should not be null.");
        assertTrue(exception.getMessage().contains("Stack is empty"),
                "Should throw an exception when stack is empty.");
    }
}
