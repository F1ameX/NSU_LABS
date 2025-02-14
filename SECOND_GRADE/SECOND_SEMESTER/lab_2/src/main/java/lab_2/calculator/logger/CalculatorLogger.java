package lab_2.calculator.logger;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class CalculatorLogger {
    private static final Logger logger = LogManager.getLogger("CalculatorLogger");

    public static Logger getLogger() { return logger; }
}
