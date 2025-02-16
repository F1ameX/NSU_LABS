package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.InvalidArgumentException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class DefineCommandTest {
    private ExecutionContext context;
    private DefineCommand defineCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        defineCommand = new DefineCommand();
    }

    @Test
    void testDefineValidVariable() {
        defineCommand.execute(context, List.of("x", "10"));
        assertEquals(10.0, context.getVariable("x"),
                "Variable x should be defined as 10.");
    }

    @Test
    void testDefineNegativeValue() {
        defineCommand.execute(context, List.of("y", "-5.5"));
        assertEquals(-5.5, context.getVariable("y"),
                "Variable y should be defined as -5.5.");
    }

    @Test
    void testDefineRedefineVariable() {
        defineCommand.execute(context, List.of("a", "15"));
        defineCommand.execute(context, List.of("a", "20"));
        assertEquals(20.0, context.getVariable("a"),
                "Variable a should be updated to 20.");
    }

    @Test
    void testDefineInvalidVariableNameThrowsException() {
        Exception exception = assertThrows(InvalidArgumentException.class,
                () -> defineCommand.execute(context, List.of("123x", "10")));
        assertTrue(exception.getMessage().contains("Invalid variable name"),
                "Should throw an exception for invalid variable name.");
    }

    @Test
    void testDefineWithoutArgumentsThrowsException() {
        Exception exception = assertThrows(InvalidArgumentException.class,
                () -> defineCommand.execute(context, List.of()));
        assertTrue(exception.getMessage().contains("DEFINE command requires exactly two arguments"),
                "Should throw an exception for missing arguments.");
    }

    @Test
    void testDefineFloatingPointVariable() {
        defineCommand.execute(context, List.of("pi", "3.1415"));
        assertEquals(3.1415, context.getVariable("pi"), 0.0001,
                "Variable pi should be defined as 3.1415.");
    }

    @Test
    void testDefineWithExtraArgumentsThrowsException() {
        Exception exception = assertThrows(InvalidArgumentException.class,
                () -> defineCommand.execute(context, List.of("x", "10", "20")));
        assertTrue(exception.getMessage().contains("DEFINE command requires exactly two arguments"),
                "Should throw an exception for extra arguments.");
    }

    @Test
    void testDefineNonNumericValueThrowsException() {
        Exception exception = assertThrows(InvalidArgumentException.class,
                () -> defineCommand.execute(context, List.of("x", "hello")));
        assertTrue(exception.getMessage().contains("is not a valid number"),
                "Should throw an exception for non-numeric values.");
    }

    @Test
    void testDefineVariableWithSpecialCharactersThrowsException() {
        Exception exception = assertThrows(InvalidArgumentException.class,
                () -> defineCommand.execute(context, List.of("@var", "10")));
        assertTrue(exception.getMessage().contains("Invalid variable name"),
                "Should throw an exception for special characters in variable names.");
    }
}