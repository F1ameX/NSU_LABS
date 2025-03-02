package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class MultiplyCommandTest {
    private ExecutionContext context;
    private MultiplyCommand multiplyCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        multiplyCommand = new MultiplyCommand();
    }

    @Test
    void testMultiplyTwoNumbers() throws StackUnderflowException {
        context.push(6.0);
        context.push(4.0);
        multiplyCommand.execute(context, List.of());
        assertEquals(24.0, context.getTop(), "6 * 4 should equal 24.");
    }

    @Test
    void testMultiplyNotEnoughOperands() {
        context.push(7.0);
        Exception exception = assertThrows(StackUnderflowException.class,
                () -> multiplyCommand.execute(context, List.of()));
        assertTrue(exception.getMessage().contains("requires at least two elements"),
                "Should throw an exception for stack underflow.");
    }
}
