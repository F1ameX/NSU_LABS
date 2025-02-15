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
    void testGetTopWithoutRemoving() {
        context.push(5.0);
        assertEquals(5.0, context.getTop(), "GetTop should return correct value.");
        assertEquals(5.0, context.getTop(), "GetTop should not remove value from stack.");
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
        Exception exception = assertThrows(IllegalStateException.class, context::pop);
        assertTrue(exception.getMessage().contains("stack empty"), "Should throw an exception on empty stack pop.");
    }

    @Test
    void testGetTopFromEmptyStackThrowsException() {
        Exception exception = assertThrows(IllegalStateException.class, context::getTop);
        assertTrue(exception.getMessage().contains("stack empty"), "Should throw an exception when stack is empty.");
    }
}