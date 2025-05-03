package lab_5.server;
import java.net.Socket;

public abstract class ClientHandler implements Runnable {
    protected final Socket socket;
    protected final Server server;
    protected String userName;
    protected String sessionId;
    protected String clientType;

    public ClientHandler(Socket socket, Server server) {
        this.socket = socket;
        this.server = server;
    }

    public boolean isLoggedIn() { return userName != null; }
    public String getUserName() { return userName; }
    public String getSessionId() { return sessionId; }
    public String getClientType() { return clientType; }

    public abstract void start();
    public abstract void sendUserLoginEvent(String name);
    public abstract void sendUserLogoutEvent(String name);
    public abstract void sendMessageEvent(String from, String message);
    public abstract void sendError(String msg);
    public abstract void sendSuccess(String msg);
    public abstract void sendSuccess(String msg, String sessionId);
    public abstract void updatePingTime();
    public abstract long getLastPingTime();
}