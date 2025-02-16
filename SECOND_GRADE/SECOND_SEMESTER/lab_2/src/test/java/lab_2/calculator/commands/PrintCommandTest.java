package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class PrintCommandTest {
    private ExecutionContext context;
    private PrintCommand printCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        printCommand = new PrintCommand();
    }

    @Test
    void testPrintValidTopValue() {
        context.push(10.0);
        assertDoesNotThrow(() -> printCommand.execute(context, List.of()));
    }

    @Test
    void testPrintEmptyStackThrowsException() {
        Exception exception = assertThrows(StackUnderflowException.class,
                () -> printCommand.execute(context, List.of()));
        assertNotNull(exception, "Exception should not be null.");
        assertTrue(exception.getMessage().contains("Stack is empty"),
                "Should throw an exception when stack is empty.");
    }
}
