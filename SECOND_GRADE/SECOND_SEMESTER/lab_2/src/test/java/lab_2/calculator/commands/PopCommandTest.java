package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class PopCommandTest {
    private ExecutionContext context;
    private PopCommand popCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        popCommand = new PopCommand();
    }

    @Test
    void testPopValue() throws StackUnderflowException {
        context.push(99.0);
        popCommand.execute(context, List.of());
        assertEquals(0, context.getStackSize(), "Stack should be empty after popping.");
    }

    @Test
    void testPopFromEmptyStack() {
        Exception exception = assertThrows(StackUnderflowException.class,
                () -> popCommand.execute(context, List.of()));
        System.out.println("Caught Exception: " + exception.getMessage());
        assertTrue(exception.getMessage().contains("Cannot pop from an empty stack"),
                "Should throw an exception on pop from empty stack.");
    }
}
