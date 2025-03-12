package lab_4.factory.logger;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
import java.util.Date;

public class Logger {
    private final PrintWriter writer;
    private final boolean isEnabled;

    public Logger(String fileName, boolean isEnabled) throws IOException {
        this.isEnabled = isEnabled;
        if (isEnabled) this.writer = new PrintWriter(new FileWriter(fileName, true), true);
        else this.writer = null;
    }

    public synchronized void log(int dealerId, int carId, int bodyId, int motorId, int accessoryId) {
        if (!isEnabled) return;

        String timeStamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
        String logEntry = timeStamp + ": Dealer " + dealerId + " sold Auto " + carId +
                " (Body: " + bodyId + ", Motor: " + motorId + ", Accessory: " + accessoryId + ")";

        assert writer != null;
        writer.println(logEntry);
    }

    public void close() { if (writer != null) writer.close(); }
}