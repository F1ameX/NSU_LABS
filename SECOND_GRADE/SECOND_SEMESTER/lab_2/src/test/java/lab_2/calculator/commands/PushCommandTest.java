package lab_2.calculator.commands;
import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.InvalidArgumentException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class PushCommandTest {
    private ExecutionContext context;
    private PushCommand pushCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        pushCommand = new PushCommand();
    }

    @Test
    void testPushNumber() throws InvalidArgumentException {
        pushCommand.execute(context, List.of("42.5"));
        assertEquals(42.5, context.getTop(), "Stack should contain pushed number.");
    }

    @Test
    void testPushVariable() throws InvalidArgumentException {
        context.defineVariable("a", 10.0);
        pushCommand.execute(context, List.of("a"));
        assertEquals(10.0, context.getTop(), "Stack should contain value of variable 'a'.");
    }

    @Test
    void testPushInvalidArgument() {
        Exception exception = assertThrows(InvalidArgumentException.class,
                () -> pushCommand.execute(context, List.of("abc")));
        assertNotNull(exception, "Exception should not be null.");
        assertTrue(exception.getMessage().contains("is not a number or a defined variable"),
                "Should throw an exception for invalid input.");
    }

    @Test
    void testPushWithoutArgumentThrowsException() {
        Exception exception = assertThrows(InvalidArgumentException.class,
                () -> pushCommand.execute(context, List.of()));
        assertTrue(exception.getMessage().contains("Push command requires exactly one argument"),
                "Should throw an exception if push is called with no arguments.");
    }
}
