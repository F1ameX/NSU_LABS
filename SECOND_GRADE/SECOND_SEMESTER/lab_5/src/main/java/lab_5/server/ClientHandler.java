package lab_5.server;

import java.net.Socket;

public abstract class ClientHandler implements Runnable {
    protected final Socket socket;
    public String clientName;
    public String clientType = "UNKNOWN";

    public ClientHandler(Socket socket) {
        this.socket = socket;
    }

    public abstract boolean isXml();
}