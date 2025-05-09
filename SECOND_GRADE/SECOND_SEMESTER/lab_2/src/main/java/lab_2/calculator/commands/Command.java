package lab_2.calculator.commands;
import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.CalculatorException;
import java.util.List;

public interface Command {
    void execute(ExecutionContext context, List<String> args) throws CalculatorException;
}
