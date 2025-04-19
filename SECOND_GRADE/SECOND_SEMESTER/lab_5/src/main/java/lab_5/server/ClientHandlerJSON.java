package lab_5.server;

import java.io.*;
import java.util.List;
import java.net.Socket;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class ClientHandlerJSON extends ClientHandler {
    private static final Pattern COMMAND_PATTERN = Pattern.compile("\"command\"\\s*:\\s*\"(\\w+)\"");
    private static final Pattern NAME_PATTERN   = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]*)\"");
    private static final Pattern TYPE_PATTERN   = Pattern.compile("\"type\"\\s*:\\s*\"([^\"]*)\"");
    private static final Pattern MESSAGE_PATTERN = Pattern.compile("\"message\"\\s*:\\s*\"([^\"]*)\"");
    private static final Pattern SESSION_PATTERN = Pattern.compile("\"session\"\\s*:\\s*\"([^\"]*)\"");

    public ClientHandlerJSON(Socket socket, DataInputStream dis, DataOutputStream dos, Server server) {
        super(socket, dis, dos, server);
    }

    private String escapeJson(String text) {
        if (text == null) return "";
        return text.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    @Override
    public void run() {
        boolean normalLogout = false;
        try {
            label:
            while (true) {
                String request = dis.readUTF();
                Matcher cmdMatcher = COMMAND_PATTERN.matcher(request);
                if (!cmdMatcher.find()) continue;

                String command = cmdMatcher.group(1);
                switch (command) {
                    case "login" -> {
                        Matcher nameMatch = NAME_PATTERN.matcher(request);
                        Matcher typeMatch = TYPE_PATTERN.matcher(request);
                        String loginName = null;
                        String loginType = null;
                        if (nameMatch.find()) {
                            loginName = nameMatch.group(1);
                        }
                        if (typeMatch.find()) {
                            loginType = typeMatch.group(1);
                        }
                        if (loginName == null || loginName.isEmpty()) {
                            sendErrorResponse("Invalid name");
                            continue;
                        }
                        synchronized (server) {
                            if (server.isNameTaken(loginName)) {
                                sendErrorResponse("Name already taken");
                                continue;
                            }
                            this.userName = loginName;
                            this.clientType = (loginType != null && !loginType.isEmpty() ? loginType : "JSONClient");
                            this.sessionId = Server.generateSessionId();
                            this.loggedIn = true;
                            sendSuccessResponse("\"session\":\"" + sessionId + "\"");
                            server.broadcastUserLogin(this.userName, this.sessionId);
                            server.log("User logged in: " + this.userName + " (" + this.clientType + ")");
                        }
                    }
                    case "list" -> {
                        if (!loggedIn) {
                            sendErrorResponse("Not logged in");
                            continue;
                        }
                        Matcher sessionMatch = SESSION_PATTERN.matcher(request);
                        String sess = null;
                        if (sessionMatch.find()) {
                            sess = sessionMatch.group(1);
                        }
                        if (sess == null || !sess.equals(this.sessionId)) {
                            sendErrorResponse("Invalid session");
                            continue;
                        }
                        sendUserList(server.getLoggedInClients());
                    }
                    case "message" -> {
                        if (!loggedIn) {
                            sendErrorResponse("Not logged in");
                            continue;
                        }
                        Matcher sessionMatch = SESSION_PATTERN.matcher(request);
                        String sess = null;
                        if (sessionMatch.find()) {
                            sess = sessionMatch.group(1);
                        }
                        if (sess == null || !sess.equals(this.sessionId)) {
                            sendErrorResponse("Invalid session");
                            continue;
                        }
                        Matcher msgMatch = MESSAGE_PATTERN.matcher(request);
                        String msg = "";
                        if (msgMatch.find()) {
                            msg = msgMatch.group(1);
                        }
                        server.broadcastMessage(this.userName, msg, this.sessionId);
                        sendSuccessResponse("");
                    }
                    case "logout" -> {
                        if (!loggedIn) {
                            break label;
                        }
                        Matcher sessionMatch = SESSION_PATTERN.matcher(request);
                        String sess = null;
                        if (sessionMatch.find()) {
                            sess = sessionMatch.group(1);
                        }
                        if (sess == null || !sess.equals(this.sessionId)) {
                            sendErrorResponse("Invalid session");
                            continue;
                        }
                        sendSuccessResponse("");
                        normalLogout = true;
                        server.broadcastUserLogout(this.userName, this.sessionId);
                        server.log("User logged out: " + this.userName);
                        break label;
                    }
                }
            }
        } catch (IOException e) {
            if (loggedIn) {
                server.log("Connection lost with user: " + this.userName);
            }
        } finally {
            try {
                if (loggedIn && !normalLogout) {
                    server.broadcastUserLogout(this.userName, this.sessionId);
                    server.log("User disconnected: " + this.userName);
                }
                server.removeClient(this);
                if (socket != null && !socket.isClosed()) {
                    socket.close();
                }
            } catch (IOException _) {
            }
        }
    }

    @Override
    public void sendUserLoginEvent(String name) {
        String json = "{\"event\":\"userlogin\",\"name\":\"" + escapeJson(name) + "\"}";
        try {
            dos.writeUTF(json);
            dos.flush();
        } catch (IOException e) {
            server.log("Failed to send userlogin event to " + this.userName);
        }
    }

    @Override
    public void sendUserLogoutEvent(String name) {
        String json = "{\"event\":\"userlogout\",\"name\":\"" + escapeJson(name) + "\"}";
        try {
            dos.writeUTF(json);
            dos.flush();
        } catch (IOException e) {
            server.log("Failed to send userlogout event to " + this.userName);
        }
    }

    @Override
    public void sendMessageEvent(String fromUser, String message) {
        String json = "{\"event\":\"message\",\"name\":\"" + escapeJson(fromUser) + "\",\"message\":\"" + escapeJson(message) + "\"}";
        try {
            dos.writeUTF(json);
            dos.flush();
        } catch (IOException e) {
            server.log("Failed to send message event to " + this.userName);
        }
    }

    @Override
    public void sendSuccessResponse(String content) {
        String json;
        if (content != null && !content.isEmpty()) {
            json = "{\"success\":{" + content + "}}";
        } else {
            json = "{\"success\":{}}";
        }
        try {
            dos.writeUTF(json);
            dos.flush();
        } catch (IOException e) {
            server.log("Failed to send success response to " + this.userName);
        }
    }

    @Override
    public void sendErrorResponse(String reason) {
        String json = "{\"error\":{\"message\":\"" + escapeJson(reason) + "\"}}";
        try {
            dos.writeUTF(json);
            dos.flush();
        } catch (IOException e) {
            server.log("Failed to send error response to client " + this.userName);
        }
    }

    @Override
    public void sendUserList(List<ClientHandler> clients) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\"success\":{\"listusers\":[");
        boolean first = true;
        for (ClientHandler c : clients) {
            if (!c.isLoggedIn()) continue;
            if (!first) sb.append(",");
            sb.append("{\"name\":\"").append(escapeJson(c.getUserName())).append("\",");
            sb.append("\"type\":\"").append(escapeJson(c.clientType)).append("\"}");
            first = false;
        }
        sb.append("]}}");
        try {
            dos.writeUTF(sb.toString());
            dos.flush();
        } catch (IOException e) {
            server.log("Failed to send user list to " + this.userName);
        }
    }
}