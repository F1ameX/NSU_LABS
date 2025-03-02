package lab_2.calculator.commands;
import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class SubtractCommandTest {
    private ExecutionContext context;
    private SubtractCommand subtractCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        subtractCommand = new SubtractCommand();
    }

    @Test
    void testSubtractTwoNumbers() throws StackUnderflowException {
        context.push(10.0);
        context.push(3.0);
        subtractCommand.execute(context, List.of());
        assertEquals(7.0, context.getTop(), "10 - 3 should equal 7.");
    }

    @Test
    void testSubtractNotEnoughOperands() {
        context.push(5.0);
        Exception exception = assertThrows(StackUnderflowException.class,
                () -> subtractCommand.execute(context, List.of()));
        assertTrue(exception.getMessage().contains("requires at least two elements"),
                "Should throw an exception for stack underflow.");
    }
}
