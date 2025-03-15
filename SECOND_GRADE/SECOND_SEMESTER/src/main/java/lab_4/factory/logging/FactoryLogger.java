package lab_4.factory.logging;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
import java.util.Date;

public class FactoryLogger {
    private static final String LOG_FILE = "factory.log";
    private static boolean loggingEnabled = true;

    public static synchronized void logSale(int dealerId, int carId, int bodyId, int motorId, int accessoryId) {
        if (!loggingEnabled) return;

        String timestamp = new SimpleDateFormat("HH:mm:ss").format(new Date());
        String logEntry = String.format("%s: Dealer %d: Car %d (Body: %d, Motor: %d, Accessory: %d)",
                timestamp, dealerId, carId, bodyId, motorId, accessoryId);
        System.out.println(logEntry);

        try (PrintWriter writer = new PrintWriter(new FileWriter(LOG_FILE, true))) {
            writer.println(logEntry);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void setLoggingEnabled(boolean enabled) { loggingEnabled = enabled; }
}