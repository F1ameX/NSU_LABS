package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.exceptions.DivisionByZeroException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class DivideCommandTest {
    private ExecutionContext context;
    private DivideCommand divideCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        divideCommand = new DivideCommand();
    }

    @Test
    void testDivideTwoNumbers() {
        context.push(10.0);
        context.push(2.0);
        divideCommand.execute(context, List.of());
        assertEquals(5.0, context.getTop(), "10 / 2 should equal 5.");
    }

    @Test
    void testDivideByZero() {
        context.push(8.0);
        context.push(0.0);
        Exception exception = assertThrows(DivisionByZeroException.class,
                () -> divideCommand.execute(context, List.of()));
        System.out.println("Caught Exception: " + exception.getMessage());
        assertTrue(exception.getMessage().contains("Division by zero is not allowed"),
                "Should throw an exception for division by zero.");
    }

    @Test
    void testDivideWithOneOperandThrowsException() {
        context.push(10.0);
        Exception exception = assertThrows(StackUnderflowException.class,
                () -> divideCommand.execute(context, List.of()));
        assertTrue(exception.getMessage().contains("requires at least two elements"),
                "Should throw an exception when only one element is in the stack.");
    }

    @Test
    void testDivideWithEmptyStackThrowsException() {
        Exception exception = assertThrows(StackUnderflowException.class,
                () -> divideCommand.execute(context, List.of()));
        assertTrue(exception.getMessage().contains("requires at least two elements"),
                "Should throw an exception when the stack is empty.");
    }
}