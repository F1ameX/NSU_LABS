package lab_5.server;

import com.google.gson.*;
import java.io.*;
import java.net.Socket;

public class ClientHandlerJSON extends ClientHandler {
    private final DataInputStream in;
    private final DataOutputStream out;
    private long lastPingTime = System.currentTimeMillis();

    public ClientHandlerJSON(Socket socket, InputStream input, OutputStream output, Server server) throws IOException {
        super(socket, server);
        this.in = new DataInputStream(input);
        this.out = new DataOutputStream(output);
    }

    @Override
    public void start() {new Thread(this).start();}

    @Override
    public void updatePingTime() {lastPingTime = System.currentTimeMillis();}

    @Override
    public long getLastPingTime() {return lastPingTime;}

    @Override
    public void run() {
        try {
            while (true) {
                String msg = in.readUTF();
                JsonObject json;
                try {
                    json = JsonParser.parseString(msg).getAsJsonObject();
                } catch (Exception e) {
                    sendError("Invalid JSON format");
                    continue;
                }

                if (!json.has("command")) {
                    sendError("Missing 'command' field");
                    continue;
                }

                String command = json.get("command").getAsString();

                switch (command) {
                    case "ping":
                        updatePingTime();
                        break;

                    case "login":
                        if (!json.has("name") || !json.has("type")) {
                            sendError("Missing fields for login");
                            continue;
                        }

                        String name = json.get("name").getAsString();
                        String type = json.get("type").getAsString();

                        synchronized (server) {
                            if (server.isNameTaken(name)) {
                                sendError("Name already taken");
                                continue;
                            }

                            this.userName = name;
                            this.sessionId = Server.generateSessionId();
                            this.clientType = type;
                        }

                        sendSuccess("login OK", sessionId);
                        server.sendHistoryTo(this);
                        server.broadcastUserLogin(userName, sessionId);
                        break;

                    case "message":
                        if (!json.has("message")) {
                            sendError("Missing 'message' field");
                            continue;
                        }

                        String text = json.get("message").getAsString();
                        server.enqueueMessage(new ChatMessage(userName, text, sessionId));
                        break;

                    case "list":
                        sendUserList();
                        break;

                    case "logout":
                        sendSuccess("bye");
                        return;

                    default:
                        sendError("Unknown command: " + command);
                }
            }
        } catch (IOException e) {
            server.log("[ERROR] JSON client crashed: " + e.getMessage());
        } finally {
            server.removeClient(this);
            if (userName != null)
                server.broadcastUserLogout(userName, sessionId);
        }
    }

    @Override
    public void sendUserLoginEvent(String name) {
        JsonObject json = new JsonObject();
        json.addProperty("type", "event");
        json.addProperty("event", "userlogin");
        json.addProperty("name", name);
        sendJson(json);
    }

    @Override
    public void sendUserLogoutEvent(String name) {
        JsonObject json = new JsonObject();
        json.addProperty("type", "event");
        json.addProperty("event", "userlogout");
        json.addProperty("name", name);
        sendJson(json);
    }

    @Override
    public void sendMessageEvent(String from, String message) {
        JsonObject json = new JsonObject();
        json.addProperty("type", "event");
        json.addProperty("event", "message");
        json.addProperty("name", from);
        json.addProperty("message", message);
        sendJson(json);
    }

    @Override
    public void sendError(String errorText) {
        JsonObject json = new JsonObject();
        json.addProperty("type", "error");
        json.addProperty("message", errorText);
        sendJson(json);
    }

    @Override
    public void sendSuccess(String message) {
        JsonObject json = new JsonObject();
        json.addProperty("type", "success");
        json.addProperty("message", message);
        sendJson(json);
    }

    @Override
    public void sendSuccess(String message, String sessionId) {
        JsonObject json = new JsonObject();
        json.addProperty("type", "success");
        json.addProperty("message", message);
        json.addProperty("session", sessionId);
        sendJson(json);
    }

    private void sendUserList() {
        JsonObject json = new JsonObject();
        json.addProperty("type", "success");
        JsonArray users = new JsonArray();
        for (ClientHandler c : server.getLoggedInClients()) {
            JsonObject user = new JsonObject();
            user.addProperty("name", c.getUserName());
            user.addProperty("type", c.getClientType());
            users.add(user);
        }
        json.add("listusers", users);
        sendJson(json);
    }

    private void sendJson(JsonObject json) {
        try {
            out.writeUTF(json.toString());
            out.flush();
        } catch (IOException e) {
            server.log("[ERROR] Failed to send JSON: " + e.getMessage());
        }
    }
}