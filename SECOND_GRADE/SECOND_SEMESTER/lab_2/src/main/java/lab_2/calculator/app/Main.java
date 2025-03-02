package lab_2.calculator.app;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;

import java.io.*;

public class Main {
    private static final Logger logger = CalculatorLogger.getLogger();

    public static void main(String[] args) {
        logger.info("Starting calculator...");

        Calculator calculator = new Calculator();

        BufferedReader reader;
        if (args.length > 0) {
            try {
                reader = new BufferedReader(new FileReader(args[0]));
                logger.info("Reading commands from file: {}", args[0]);
            } catch (FileNotFoundException e) {
                logger.error("Error: File not found - {}", args[0]);
                return;
            }
        }
        else {
            reader = new BufferedReader(new InputStreamReader(System.in));
            logger.info("Reading commands from standard input...");
        }

        calculator.start(reader);
    }
}