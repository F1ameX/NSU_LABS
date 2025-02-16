package lab_2.calculator.context;

import java.util.HashMap;
import java.util.Map;
import java.util.Stack;

public class ExecutionContext {
    private final Stack<Double> stack;
    private final Map<String, Double> variables;

    public ExecutionContext() {
        stack = new Stack<>();
        variables = new HashMap<>();
    }

    public void push(double value) { stack.push(value);}
    public boolean hasVariable(String name) { return variables.containsKey(name); }
    public int getStackSize() { return stack.size(); }

    public double pop() {
        if (stack.isEmpty()) {
            throw new IllegalStateException("Error: Cannot pop from an empty stack.");
        }
        return stack.pop();
    }

    public double getTop() {
        if (stack.isEmpty()) {
            throw new IllegalStateException("Error: Stack is empty, cannot retrieve top element.");
        }
        return stack.peek();
    }

    public void defineVariable(String name, double value) {
        if (!name.matches("[a-zA-Z_][a-zA-Z0-9_]*")) {
            throw new IllegalArgumentException("Error: Invalid variable name '" + name +
                    "'. Variable names must start with a letter or underscore and contain only letters, digits, or underscores.");
        }
        variables.put(name, value);
    }

    public double getVariable(String name) {
        if (!variables.containsKey(name)) {
            throw new IllegalArgumentException("Error: Variable '" + name + "' is not defined.");
        }
        return variables.get(name);
    }

    public void clear() {
        stack.clear();
        variables.clear();
    }
}