package lab_5.server;

import java.io.*;
import java.net.Socket;
import java.util.List;

public abstract class ClientHandler extends Thread {
    protected Socket socket;
    protected DataInputStream dis;
    protected DataOutputStream dos;
    protected Server server;
    protected String userName = "";
    protected String clientType = "";
    protected String sessionId = "";
    protected boolean loggedIn = false;

    public ClientHandler(Socket socket, DataInputStream dis, DataOutputStream dos, Server server) {
        this.socket = socket;
        this.dis = dis;
        this.dos = dos;
        this.server = server;
    }

    public abstract void run();

    public abstract void sendUserLoginEvent(String name);
    public abstract void sendUserLogoutEvent(String name);
    public abstract void sendMessageEvent(String fromUser, String message);
    public abstract void sendSuccessResponse(String content);
    public abstract void sendErrorResponse(String reason);
    public abstract void sendUserList(List<ClientHandler> clients);

    public String getUserName() {return userName; }
    public String getSessionId() {return sessionId; }
    public boolean isLoggedIn() {return loggedIn; }
}