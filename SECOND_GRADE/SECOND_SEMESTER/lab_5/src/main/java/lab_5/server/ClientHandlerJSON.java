package lab_5.server;

import com.google.gson.*;
import java.io.*;
import java.net.Socket;

public class ClientHandlerJSON extends ClientHandler {
    private final BufferedReader in;
    private final PrintWriter out;

    public ClientHandlerJSON(Socket socket, InputStream inStream) throws IOException {
        super(socket);
        this.in = new BufferedReader(new InputStreamReader(inStream));
        this.out = new PrintWriter(socket.getOutputStream(), true);
    }

    @Override
    public void run() {
        try {
            String msg;
            while ((msg = in.readLine()) != null) {
                JsonObject json;
                try {
                    json = JsonParser.parseString(msg).getAsJsonObject();
                } catch (Exception e) {
                    out.println(buildErrorJson("Invalid JSON format"));
                    System.err.println("[ERROR] Invalid JSON: " + msg);
                    continue;
                }

                if (!json.has("command")) {
                    out.println(buildErrorJson("Missing 'command' field"));
                    continue;
                }

                String command = json.get("command").getAsString();

                switch (command) {
                    case "login":
                        if (!json.has("name")) {
                            out.println(buildErrorJson("Missing 'name' field for login"));
                            continue;
                        }

                        String name = json.get("name").getAsString();
                        if (Server.isNameTaken(name)) {
                            out.println(buildErrorJson("Name already taken"));
                            continue;
                        }

                        clientName = name;
                        clientType = json.has("type") ? json.get("type").getAsString() : "UNKNOWN";
                        System.out.println("[LOGIN] " + clientName + " (" + clientType + ")");

                        JsonObject success = new JsonObject();
                        success.addProperty("type", "success");
                        success.addProperty("message", "login OK");
                        out.println(success.toString());

                        Server.broadcastSystemMessage(clientName + " joined the chat");
                        break;

                    case "message":
                        if (!json.has("message")) {
                            out.println(buildErrorJson("Missing 'message' field"));
                            continue;
                        }
                        String text = json.get("message").getAsString();
                        Server.broadcastUserMessage(clientName, text);
                        break;

                    case "list":
                        JsonObject list = Server.buildUserListJson();
                        out.println(list.toString());
                        break;

                    case "logout":
                        return;

                    default:
                        out.println(buildErrorJson("Unknown command: " + command));
                }
            }
        } catch (Exception e) {
            System.err.println("[ERROR] JSON client crashed: " + e.getMessage());
        } finally {
            Server.getClients().remove(this);
            Server.broadcastSystemMessage(clientName + " left the chat");
        }
    }

    private JsonObject buildErrorJson(String errorText) {
        JsonObject o = new JsonObject();
        o.addProperty("type", "error");
        o.addProperty("message", errorText);
        return o;
    }

    public void sendJson(JsonObject msg) {
        out.println(msg.toString());
    }

    public boolean isXml() {
        return false;
    }
}
