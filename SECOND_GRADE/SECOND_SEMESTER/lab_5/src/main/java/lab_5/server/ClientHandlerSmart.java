package lab_5.server;

import com.google.gson.*;
import org.w3c.dom.*;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.*;
import java.net.Socket;

public class ClientHandlerSmart implements Runnable {
    private final Socket socket;
    private PrintWriter jsonOut;
    private DataOutputStream xmlOut;
    public String clientName;
    public String clientType = "UNKNOWN";
    public boolean isXml = false;

    public ClientHandlerSmart(Socket socket) {
        this.socket = socket;
    }

    @Override
    public void run() {
        try {
            InputStream raw = socket.getInputStream();
            PushbackInputStream peekIn = new PushbackInputStream(raw, 5);

            int b1 = peekIn.read();
            if (b1 == -1) return;
            peekIn.unread(b1);

            if (b1 == '{') {
                handleJson(peekIn);
            } else {
                handleXml(peekIn);
            }

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            Server.getClients().remove(this);
            if (clientName != null) {
                broadcastXml(buildEvent("userlogout", clientName));
                broadcastJson(buildSystemMessage(clientName + " left the chat."));
            }
            try {
                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private void handleJson(InputStream in) throws IOException {
        this.isXml = false;
        BufferedReader reader = new BufferedReader(new InputStreamReader(in));
        jsonOut = new PrintWriter(socket.getOutputStream(), true);

        String msg;
        while ((msg = reader.readLine()) != null) {
            JsonObject json = JsonParser.parseString(msg).getAsJsonObject();
            String cmd = json.get("command").getAsString();

            switch (cmd) {
                case "login":
                    clientName = json.get("name").getAsString();
                    clientType = json.has("type") ? json.get("type").getAsString() : "UNKNOWN";
                    System.out.println("[LOGIN] " + clientName + " (" + clientType + ")");
                    broadcastJson(buildSystemMessage(clientName + " joined the chat using " + clientType));
                    broadcastXml(buildEvent("system", clientName + " joined the chat using " + clientType));
                    break;

                case "message":
                    String text = json.get("message").getAsString();
                    for (ClientHandlerSmart client : Server.getClients()) {
                        if (!client.clientName.equals(this.clientName) && !client.isXml) {
                            client.sendJson(buildUserMessage(this.clientName, text));
                        }
                    }
                    for (ClientHandlerSmart client : Server.getClients()) {
                        if (!client.clientName.equals(this.clientName) && client.isXml) {
                            try {
                                client.sendXml(buildServerMessage(this.clientName, text));
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    }
                    break;

                case "list":
                    JsonObject listResponse = buildUserListJson();
                    sendJson(listResponse);
                    break;

                case "logout":
                    return;
            }
        }
    }

    private void handleXml(InputStream in) throws Exception {
        this.isXml = true;
        DataInputStream dataIn = new DataInputStream(in);
        xmlOut = new DataOutputStream(socket.getOutputStream());

        while (true) {
            int len = dataIn.readInt();
            byte[] buffer = new byte[len];
            dataIn.readFully(buffer);

            Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder()
                    .parse(new ByteArrayInputStream(buffer));
            Element root = doc.getDocumentElement();
            String cmd = root.getAttribute("name");

            switch (cmd) {
                case "login":
                    clientName = getText(root, "name");
                    clientType = getText(root, "type");
                    System.out.println("[LOGIN] " + clientName + " (" + clientType + ")");
                    sendXml(buildSuccess("login OK"));
                    broadcastXml(buildEvent("userlogin", clientName));
                    broadcastXml(buildEvent("system", clientName + " joined the chat using " + clientType));
                    broadcastJson(buildSystemMessage(clientName + " joined the chat using " + clientType));
                    break;

                case "message":
                    String text = getText(root, "message");
                    for (ClientHandlerSmart client : Server.getClients()) {
                        if (!client.clientName.equals(this.clientName) && client.isXml) {
                            client.sendXml(buildServerMessage(this.clientName, text));
                        }
                    }
                    for (ClientHandlerSmart client : Server.getClients()) {
                        if (!client.clientName.equals(this.clientName) && !client.isXml) {
                            client.sendJson(buildUserMessage(this.clientName, text));
                        }
                    }
                    sendXml(buildSuccess("message delivered"));
                    break;

                case "list":
                    sendXml(buildUserListXml());
                    break;

                case "logout":
                    broadcastXml(buildEvent("userlogout", clientName));
                    broadcastJson(buildSystemMessage(clientName + " left the chat."));
                    sendXml(buildSuccess("bye"));
                    socket.close();
                    return;
            }
        }
    }

    private JsonObject buildUserMessage(String name, String text) {
        JsonObject o = new JsonObject();
        o.addProperty("type", "message");
        o.addProperty("from", name);
        o.addProperty("text", text);
        return o;
    }

    private JsonObject buildSystemMessage(String text) {
        JsonObject o = new JsonObject();
        o.addProperty("type", "system");
        o.addProperty("text", text);
        return o;
    }

    private void sendJson(JsonObject msg) {
        if (jsonOut != null) {
            jsonOut.println(msg.toString());
        }
    }

    private void broadcastJson(JsonObject msg) {
        for (ClientHandlerSmart c : Server.getClients()) {
            if (!c.isXml) {
                c.sendJson(msg);
            }
        }
    }

    private void sendXml(Document doc) {
        try {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            Transformer t = TransformerFactory.newInstance().newTransformer();
            t.transform(new DOMSource(doc), new StreamResult(baos));
            byte[] bytes = baos.toByteArray();
            xmlOut.writeInt(bytes.length);
            xmlOut.write(bytes);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void broadcastXml(Document doc) {
        for (ClientHandlerSmart c : Server.getClients()) {
            if (c.isXml) {
                c.sendXml(doc);
            }
        }
    }

    private Document buildServerMessage(String name, String text) throws Exception {
        Document doc = newDoc();
        Element event = doc.createElement("event");
        event.setAttribute("name", "message");
        Element msg = doc.createElement("message");
        msg.setTextContent(text);
        Element n = doc.createElement("name");
        n.setTextContent(name);
        event.appendChild(msg);
        event.appendChild(n);
        doc.appendChild(event);
        return doc;
    }

    private Document buildEvent(String type, String name) {
        try {
            Document doc = newDoc();
            Element event = doc.createElement("event");
            event.setAttribute("name", type);
            Element n = doc.createElement("name");
            n.setTextContent(name);
            event.appendChild(n);
            doc.appendChild(event);
            return doc;
        } catch (Exception e) {
            return null;
        }
    }

    private Document buildSuccess(String message) {
        try {
            Document doc = newDoc();
            Element success = doc.createElement("success");
            Element msg = doc.createElement("message");
            msg.setTextContent(message);
            success.appendChild(msg);
            doc.appendChild(success);
            return doc;
        } catch (Exception e) {
            return null;
        }
    }

    private Document buildUserListXml() {
        try {
            Document doc = newDoc();
            Element success = doc.createElement("success");
            Element listusers = doc.createElement("listusers");
            for (ClientHandlerSmart client : Server.getClients()) {
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
        } catch (Exception e) {
            return buildError("Failed to build user list");
        }
    }

    private JsonObject buildUserListJson() {
        JsonObject result = new JsonObject();
        result.addProperty("type", "list");
        JsonArray users = new JsonArray();
        for (ClientHandlerSmart client : Server.getClients()) {
            JsonObject user = new JsonObject();
            user.addProperty("name", client.clientName);
            user.addProperty("type", client.clientType);
            users.add(user);
        }
        result.add("users", users);
        return result;
    }

    private Document buildError(String errorMsg) {
        try {
            Document doc = newDoc();
            Element error = doc.createElement("error");
            Element msg = doc.createElement("message");
            msg.setTextContent(errorMsg);
            error.appendChild(msg);
            doc.appendChild(error);
            return doc;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    private Document newDoc() throws Exception {
        return DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
    }

    private String getText(Element parent, String tag) {
        NodeList list = parent.getElementsByTagName(tag);
        if (list.getLength() == 0) return null;
        return list.item(0).getTextContent();
    }
}