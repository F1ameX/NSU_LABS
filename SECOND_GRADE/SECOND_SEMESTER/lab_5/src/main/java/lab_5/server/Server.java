package lab_5.server;

import java.io.InputStream;
import java.io.PushbackInputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.*;
import org.w3c.dom.*;
import javax.xml.parsers.*;

public class Server {
    private static final int PORT = 12345;
    private static final List<ClientHandler> clients = new ArrayList<>();

    public static void main(String[] args) {
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Server started on port " + PORT);
            while (true) {
                Socket socket = serverSocket.accept();
                InputStream baseStream = socket.getInputStream();
                PushbackInputStream peekStream = new PushbackInputStream(baseStream, 5);

                int first = peekStream.read();
                peekStream.unread(first);

                ClientHandler handler;
                if (first == '{') {
                    handler = new ClientHandlerJSON(socket, peekStream);
                } else {
                    handler = new ClientHandlerXML(socket, peekStream);
                }

                clients.add(handler);
                new Thread(handler).start();
            }
        } catch (Exception e) {
            System.err.println("[ERROR] Server crashed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static List<ClientHandler> getClients() {
        return clients;
    }

    public static boolean isNameTaken(String name) {
        for (ClientHandler client : clients) {
            if (name.equalsIgnoreCase(client.clientName)) {
                return true;
            }
        }
        return false;
    }

    public static void broadcastUserMessage(String from, String text) {
        for (ClientHandler client : clients) {
            if (!client.clientName.equals(from)) {
                if (client instanceof ClientHandlerJSON jsonClient) {
                    jsonClient.sendJson(buildUserMessage(from, text));
                } else if (client instanceof ClientHandlerXML xmlClient) {
                    try {
                        xmlClient.sendXml(buildXmlMessage(from, text));
                    } catch (Exception e) {
                        System.err.println("[ERROR] Failed to send XML message: " + e.getMessage());
                    }
                }
            }
        }
    }

    public static void broadcastSystemMessage(String message) {
        for (ClientHandler client : clients) {
            if (client instanceof ClientHandlerJSON jsonClient) {
                jsonClient.sendJson(buildSystemJson(message));
            } else if (client instanceof ClientHandlerXML xmlClient) {
                try {
                    xmlClient.sendXml(buildXmlSystemEvent(message));
                } catch (Exception e) {
                    System.err.println("[ERROR] Failed to send XML system event: " + e.getMessage());
                }
            }
        }
    }

    public static JsonObject buildUserMessage(String name, String text) {
        JsonObject json = new JsonObject();
        json.addProperty("type", "message");
        json.addProperty("from", name);
        json.addProperty("text", text);
        return json;
    }

    public static JsonObject buildSystemJson(String message) {
        JsonObject json = new JsonObject();
        json.addProperty("type", "system");
        json.addProperty("text", message);
        return json;
    }

    public static Document buildXmlMessage(String from, String text) throws Exception {
        Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
        Element event = doc.createElement("event");
        event.setAttribute("name", "message");

        Element name = doc.createElement("name");
        name.setTextContent(from);
        Element message = doc.createElement("message");
        message.setTextContent(text);

        event.appendChild(message);
        event.appendChild(name);
        doc.appendChild(event);
        return doc;
    }

    public static Document buildXmlSystemEvent(String message) throws Exception {
        Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
        Element event = doc.createElement("event");
        event.setAttribute("name", "system");

        Element name = doc.createElement("name");
        name.setTextContent(message);
        event.appendChild(name);

        doc.appendChild(event);
        return doc;
    }

    public static Document buildUserListXml() throws Exception {
        Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
        Element success = doc.createElement("success");
        Element listusers = doc.createElement("listusers");

        for (ClientHandler client : clients) {
            Element user = doc.createElement("user");

            Element name = doc.createElement("name");
            name.setTextContent(client.clientName);
            Element type = doc.createElement("type");
            type.setTextContent(client.clientType);

            user.appendChild(name);
            user.appendChild(type);
            listusers.appendChild(user);
        }

        success.appendChild(listusers);
        doc.appendChild(success);
        return doc;
    }

    public static JsonObject buildUserListJson() {
        JsonObject result = new JsonObject();
        result.addProperty("type", "list");

        JsonArray users = new JsonArray();
        for (ClientHandler client : clients) {
            JsonObject user = new JsonObject();
            user.addProperty("name", client.clientName);
            user.addProperty("type", client.clientType);
            users.add(user);
        }

        result.add("users", users);
        return result;
    }
}