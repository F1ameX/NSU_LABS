package lab_5.server;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

public class Server {
    private final List<ClientHandler> clients = new ArrayList<>();
    private final Queue<ChatMessage> messageQueue = new ConcurrentLinkedQueue<>();
    private final List<ChatMessage> messageHistory = new ArrayList<>();
    private final Object clientLock = new Object();
    private final Object historyLock = new Object();
    private ServerSocket serverSocket;

    public static void main(String[] args) {
        int port = 12345;
        new Server(port).start();
    }

    public static String generateSessionId() {return "session-" + new Random().nextInt(999999);}
    public void log(String message) {System.out.println(message);}
    public void addClient(ClientHandler client) {synchronized (clientLock) {clients.add(client);}}

    public void removeClient(ClientHandler client) {
        synchronized (clientLock) {clients.remove(client);}
        log("Client removed: " + client.getUserName());
    }

    public boolean isNameTaken(String name) {
        synchronized (clientLock) {
            for (ClientHandler c : clients) if (c.isLoggedIn() && c.getUserName().equalsIgnoreCase(name)) return true;
            return false;
        }
    }

    public List<ClientHandler> getLoggedInClients() {
        synchronized (clientLock) {
            List<ClientHandler> result = new ArrayList<>();
            for (ClientHandler c : clients) if (c.isLoggedIn()) result.add(c);
            return result;
        }
    }

    public void broadcastUserLogin(String userName, String excludeSession) {
        for (ClientHandler c : getLoggedInClients()) if (!c.getSessionId().equals(excludeSession)) c.sendUserLoginEvent(userName);
        log("Broadcast userlogin: " + userName);
    }

    public void broadcastUserLogout(String userName, String excludeSession) {
        for (ClientHandler c : getLoggedInClients()) if (!c.getSessionId().equals(excludeSession)) c.sendUserLogoutEvent(userName);
        log("Broadcast userlogout: " + userName);
    }

    public void broadcastMessage(String from, String message, String senderSessionId) {
        for (ClientHandler c : getLoggedInClients()) {
            if (c.getSessionId().equals(senderSessionId)) c.sendMessageEvent("You", message);
            else c.sendMessageEvent(from, message);
        }
        log("Broadcast message from " + from + ": " + message);
    }

    public void enqueueMessage(ChatMessage msg) {
        messageQueue.add(msg);
        synchronized (historyLock) {
            messageHistory.add(msg);
            if (messageHistory.size() > 10) messageHistory.removeFirst();
        }
    }

    public void sendHistoryTo(ClientHandler client) {
        synchronized (historyLock) {for (ChatMessage msg : messageHistory) client.sendMessageEvent(msg.from(), msg.message()); }
    }

    private void startMessageDispatcher() {
        Thread dispatcher = new Thread(() -> {
            while (true) {
                ChatMessage msg = messageQueue.poll();
                if (msg != null)
                    broadcastMessage(msg.from(), msg.message(), msg.sessionId());
                else {
                    try {
                        Thread.sleep(50);
                    } catch (InterruptedException ignored) {}
                }
            }
        });
        dispatcher.setDaemon(true);
        dispatcher.start();
    }

    private void startPingMonitor() {
        Thread monitor = new Thread(() -> {
            while (true) {
                long now = System.currentTimeMillis();
                List<ClientHandler> snapshot;
                synchronized (clientLock) {snapshot = new ArrayList<>(clients);}
                for (ClientHandler client : snapshot) {
                    if (now - client.getLastPingTime() > 10_000) {
                        log("[TIMEOUT] " + client.getUserName() + " timed out.");
                        client.sendError("Disconnected due to inactivity");
                        removeClient(client);
                        broadcastUserLogout(client.getUserName(), client.getSessionId());
                        try {
                            client.socket.close();
                        } catch (IOException ignored) {}
                    }
                }
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException ignored) {}
            }
        });
        monitor.setDaemon(true);
        monitor.start();
    }

    public Server(int port) {
        try {
            serverSocket = new ServerSocket(port);
            log("Server started on port " + port);
        } catch (IOException e) {
            log("Could not start server: " + e.getMessage());
            System.exit(1);
        }
    }

    public void start() {
        startMessageDispatcher();
        startPingMonitor();

        while (true) {
            try {
                Socket socket = serverSocket.accept();
                log("Client connected: " + socket.getInetAddress());

                DataInputStream dis = new DataInputStream(socket.getInputStream());
                DataOutputStream dos = new DataOutputStream(socket.getOutputStream());
                String protocol = dis.readUTF();

                ClientHandler handler;
                if (protocol.equalsIgnoreCase("JSON"))
                    handler = new ClientHandlerJSON(socket, dis, dos, this);
                else if (protocol.equalsIgnoreCase("XML"))
                    handler = new ClientHandlerXML(socket, dis, dos, this);
                else {
                    log("Unknown protocol: " + protocol);
                    socket.close();
                    continue;
                }

                addClient(handler);
                handler.start();

            } catch (IOException e) {log("[ERROR] Connection error: " + e.getMessage());}
        }
    }
}