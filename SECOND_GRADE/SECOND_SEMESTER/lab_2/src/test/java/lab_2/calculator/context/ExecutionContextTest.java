package lab_2.calculator.context;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ExecutionContextTest {
    private ExecutionContext context;

    @BeforeEach
    void setUp() { context = new ExecutionContext(); }

    @Test
    void testPushAndPop() {
        context.push(10.0);
        context.push(20.5);
        assertEquals(20.5, context.pop(), "Last pushed value should be popped first.");
        assertEquals(10.0, context.pop(), "Remaining value should be correct.");
    }

    @Test
    void testGetTop() {
        context.push(50.0);
        assertEquals(50.0, context.getTop(), "Top should return the last pushed value.");
        context.push(100.0);
        assertEquals(100.0, context.getTop(), "Top should return the latest pushed value.");
    }

    @Test
    void testStackSize() {
        assertEquals(0, context.getStackSize(), "New stack should be empty.");
        context.push(1.0);
        context.push(2.0);
        assertEquals(2, context.getStackSize(), "Stack size should be 2.");
    }

    @Test
    void testClearStack() {
        context.push(30.0);
        context.push(40.0);
        context.clear();
        assertEquals(0, context.getStackSize(), "Stack should be empty after clear.");
    }

    @Test
    void testPopFromEmptyStackThrowsException() {
        Exception exception = assertThrows(IllegalStateException.class, () -> context.pop());
        assertTrue(exception.getMessage().contains("Cannot pop from an empty stack"),
                "Should throw an exception on empty stack pop.");
    }

    @Test
    void testGetTopFromEmptyStackThrowsException() {
        Exception exception = assertThrows(IllegalStateException.class, () -> context.getTop());
        assertTrue(exception.getMessage().contains("Stack is empty, cannot retrieve top element"),
                "Should throw an exception when stack is empty.");
    }

    @Test
    void testDefineAndRetrieveVariable() {
        context.defineVariable("x", 10.0);
        assertEquals(10.0, context.getVariable("x"), "Variable x should return the correct value.");
    }

    @Test
    void testUpdateVariable() {
        context.defineVariable("a", 5.0);
        assertEquals(5.0, context.getVariable("a"), "Initial variable value should be correct.");
        context.defineVariable("a", 20.0);
        assertEquals(20.0, context.getVariable("a"), "Updated variable should have the new value.");
    }

    @Test
    void testMultipleVariables() {
        context.defineVariable("x", 3.0);
        context.defineVariable("y", 7.5);
        assertEquals(3.0, context.getVariable("x"), "Variable x should return correct value.");
        assertEquals(7.5, context.getVariable("y"), "Variable y should return correct value.");
    }

    @Test
    void testGetUndefinedVariableThrowsException() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> context.getVariable("unknownVar"));
        assertTrue(exception.getMessage().contains("not defined"), "Should throw exception for undefined variable.");
    }

    @Test
    void testHasVariable() {
        context.defineVariable("b", 15.0);
        assertTrue(context.hasVariable("b"), "hasVariable should return true for defined variable.");
        assertFalse(context.hasVariable("c"), "hasVariable should return false for undefined variable.");
    }

    @Test
    void testClearVariables() {
        context.defineVariable("p", 99.0);
        context.clear();
        assertFalse(context.hasVariable("p"), "Variables should be removed after clear.");
    }

    @Test
    void testDefineVariableWithSpecialCharacters() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> context.defineVariable("var@", 5.0));
        assertTrue(exception.getMessage().contains("Invalid variable name"), "Should throw exception for special character variable names.");
    }

    @Test
    void testDefineVariableWithNumbers() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> context.defineVariable("123abc", 5.0));
        assertTrue(exception.getMessage().contains("Invalid variable name"), "Should throw exception for variable names starting with numbers.");
    }
}