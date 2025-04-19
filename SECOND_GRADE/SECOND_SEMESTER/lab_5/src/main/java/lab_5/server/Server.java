package lab_5.server;

import java.io.*;
import java.net.*;
import java.util.*;
import java.net.Socket;
import java.util.concurrent.atomic.AtomicInteger;

public class Server {
    private ServerSocket serverSocket;
    private final List<ClientHandler> clients = Collections.synchronizedList(new ArrayList<>());
    private static final AtomicInteger sessionCounter = new AtomicInteger(1);

    public Server(int port) {
        try {
            serverSocket = new ServerSocket(port);
            log("Server started on port " + port);
        } catch (IOException e) {
            System.err.println("Could not start server on port " + port);
            e.printStackTrace();
            System.exit(1);
        }
    }

    public void start() {
        try {
            while (true) {
                Socket socket = serverSocket.accept();
                DataInputStream dis = new DataInputStream(socket.getInputStream());
                DataOutputStream dos = new DataOutputStream(socket.getOutputStream());
                String protocol = "";
                try {
                    protocol = dis.readUTF();
                } catch (IOException ex) {
                    log("Failed to read protocol from new client: " + ex.getMessage());
                    socket.close();
                    continue;
                }
                ClientHandler handler;
                if (protocol.equalsIgnoreCase("JSON")) {
                    handler = new ClientHandlerJSON(socket, dis, dos, this);
                } else if (protocol.equalsIgnoreCase("XML")) {
                    handler = new ClientHandlerXML(socket, dis, dos, this);
                } else {
                    log("Unknown protocol identifier \"" + protocol + "\" from client. Closing connection.");
                    socket.close();
                    continue;
                }
                addClient(handler);
                handler.start();
            }
        } catch (IOException e) {
            log("Error accepting client connection: " + e.getMessage());
        } finally {
            try {
                if (serverSocket != null) serverSocket.close();
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
    }

    public synchronized void addClient(ClientHandler client) {
        clients.add(client);
        log("Client connected: " + client.socket.getInetAddress());
    }

    public synchronized void removeClient(ClientHandler client) {
        clients.remove(client);
        log("Client removed: " + client.getUserName());
    }

    public void broadcastUserLogin(String userName, String excludeSession) {
        synchronized (clients) {
            for (ClientHandler c : clients) {
                if (c.isLoggedIn() && !c.getSessionId().equals(excludeSession)) {
                    c.sendUserLoginEvent(userName);
                }
            }
        }
        log("Broadcast userlogin: " + userName);
    }

    public void broadcastUserLogout(String userName, String excludeSession) {
        synchronized (clients) {
            for (ClientHandler c : clients) {
                if (c.isLoggedIn() && !c.getSessionId().equals(excludeSession)) {
                    c.sendUserLogoutEvent(userName);
                }
            }
        }
        log("Broadcast userlogout: " + userName);
    }

    public void broadcastMessage(String fromUser, String message, String excludeSession) {
        synchronized (clients) {
            for (ClientHandler c : clients) {
                if (c.isLoggedIn() && !c.getSessionId().equals(excludeSession)) {
                    c.sendMessageEvent(fromUser, message);
                }
            }
        }
        log("Broadcast message from " + fromUser + ": " + message);
    }

    public synchronized boolean isNameTaken(String name) {
        for (ClientHandler c : clients) {
            if (c.isLoggedIn() && c.getUserName().equals(name)) {
                return true;
            }
        }
        return false;
    }

    public List<ClientHandler> getLoggedInClients() {
        List<ClientHandler> loggedClients = new ArrayList<>();
        synchronized (clients) {
            for (ClientHandler c : clients) {
                if (c.isLoggedIn()) {
                    loggedClients.add(c);
                }
            }
        }
        return loggedClients;
    }

    public static String generateSessionId() {
        return "session-" + sessionCounter.getAndIncrement();
    }

    public void log(String message) {
        System.out.println(message);
    }

    public static void main(String[] args) {
        int port = 12345;
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.out.println("Invalid port number, using default " + port);
            }
        }
        Server server = new Server(port);
        server.start();
    }
}