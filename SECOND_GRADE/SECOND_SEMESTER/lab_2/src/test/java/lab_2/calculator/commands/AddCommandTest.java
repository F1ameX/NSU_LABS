package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class AddCommandTest {
    private ExecutionContext context;
    private AddCommand addCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        addCommand = new AddCommand();
    }

    @Test
    void testAddTwoNumbers() {
        context.push(10.0);
        context.push(5.0);
        addCommand.execute(context, List.of());
        assertEquals(15.0, context.getTop(), "10 + 5 should equal 15.");
    }

    @Test
    void testAddNotEnoughOperands() {
        context.push(10.0);
        Exception exception = assertThrows(StackUnderflowException.class, () -> addCommand.execute(context, List.of()));
        assertTrue(exception.getMessage().contains("requires at least two elements"), "Should throw an exception for stack underflow.");
    }
}