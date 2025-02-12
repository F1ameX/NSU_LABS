package lab_2.calculator.context;

import java.util.HashMap;
import java.util.Map;
import java.util.Stack;

public class ExecutionContext {
    private final Stack<Double> stack;
    private final Map<String, Double> variables;


    public ExecutionContext() {
        this.stack = new Stack<>();
        this.variables = new HashMap<>();
    }


    public void push(double value) { stack.push(value);}
    public void defineVariable(String name, double value) { variables.put(name, value);}
    public boolean hasVariable(String name) { return variables.containsKey(name);}
    public int getStackSize() {return stack.size();}

    public double pop() {
        if (stack.isEmpty()) {
            throw new IllegalStateException("Error: stack is empty!");
        }
        return stack.pop();
    }


    public double getTop() {
        if (stack.isEmpty()) {
            throw new IllegalStateException("Error: stack is empty!");
        }
        return stack.peek();
    }


    public double getVariable(String name) {
        if (!variables.containsKey(name)) {
            throw new IllegalArgumentException("Error: variable " + name + " is not defined!");
        }
        return variables.get(name);
    }


    public void clear() {
        stack.clear();
        variables.clear();
    }
}