package lab_4.factory.config;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

public class ConfigReader {
    private final Properties properties = new Properties();

    public ConfigReader(String configFilePath) {
        try (FileInputStream fis = new FileInputStream(configFilePath)) {
            properties.load(fis);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public int getInt(String key, int defaultValue) {
        return properties.getProperty(key) != null ? Integer.parseInt(properties.getProperty(key)) : defaultValue;
    }

    public boolean getBoolean(String key, boolean defaultValue) {
        return properties.getProperty(key) != null ? Boolean.parseBoolean(properties.getProperty(key)) : defaultValue;
    }
}