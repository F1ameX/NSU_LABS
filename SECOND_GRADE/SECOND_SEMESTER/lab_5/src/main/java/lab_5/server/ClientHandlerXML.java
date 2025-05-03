package lab_5.server;

import org.w3c.dom.*;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.*;
import java.net.Socket;

public class ClientHandlerXML extends ClientHandler {
    private final DataInputStream in;
    private final DataOutputStream out;
    private final DocumentBuilder builder;
    private final Object sendLock = new Object();
    private long lastPingTime = System.currentTimeMillis();

    public ClientHandlerXML(Socket socket, InputStream input, OutputStream output, Server server) throws IOException {
        super(socket, server);
        this.in = new DataInputStream(input);
        this.out = new DataOutputStream(output);
        try {
            this.builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
        } catch (Exception e) {throw new IOException("Failed to create XML parser", e);}
    }

    @Override
    public void start() {new Thread(this).start();}

    @Override
    public void updatePingTime() {lastPingTime = System.currentTimeMillis();}

    @Override
    public long getLastPingTime() {return lastPingTime;}

    private Document newDocument() throws Exception {
        return DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
    }

    @Override
    public void run() {
        try {
            while (true) {
                int len = in.readInt();
                byte[] data = new byte[len];
                in.readFully(data);

                Document doc = builder.parse(new ByteArrayInputStream(data));
                Element root = doc.getDocumentElement();
                String command = root.getAttribute("name");

                switch (command) {
                    case "ping" -> updatePingTime();

                    case "login" -> {
                        String name = getText(root, "name");
                        String type = getText(root, "type");

                        if (name == null || type == null || name.isEmpty()) {
                            sendError("Missing name/type");
                            continue;
                        }

                        synchronized (server) {
                            if (server.isNameTaken(name)) {
                                sendError("Name already taken");
                                continue;
                            }
                        }

                        this.userName = name;
                        this.clientType = type;
                        this.sessionId = Server.generateSessionId();

                        sendSuccess("login OK", sessionId);
                        server.sendHistoryTo(this);
                        server.broadcastUserLogin(userName, sessionId);
                    }

                    case "message" -> {
                        String text = getText(root, "message");
                        if (text == null || text.isEmpty()) {
                            sendError("Empty message");
                            continue;
                        }
                        server.enqueueMessage(new ChatMessage(userName, text, sessionId));
                    }

                    case "list" -> sendUserList();

                    case "logout" -> {
                        sendSuccess("bye");
                        return;
                    }

                    default -> sendError("Unknown command: " + command);
                }
            }
        } catch (Exception e) {
            server.log("[ERROR] XML client crashed: " + e.getMessage());
        } finally {
            server.removeClient(this);
            if (userName != null) server.broadcastUserLogout(userName, sessionId);
        }
    }

    private void sendXml(Document doc) {
        synchronized (sendLock) {
            try {
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                Transformer t = TransformerFactory.newInstance().newTransformer();
                t.transform(new DOMSource(doc), new StreamResult(baos));
                byte[] xml = baos.toByteArray();
                out.writeInt(xml.length);
                out.write(xml);
            } catch (Exception e) {server.log("[ERROR] Failed to send XML: " + e.getMessage());}
        }
    }

    private String getText(Element parent, String tag) {
        NodeList list = parent.getElementsByTagName(tag);
        if (list.getLength() == 0) return null;
        return list.item(0).getTextContent();
    }

    @Override
    public void sendUserLoginEvent(String name) {
        try {
            Document doc = newDocument();
            Element e = doc.createElement("event");
            e.setAttribute("name", "userlogin");
            Element n = doc.createElement("name");
            n.setTextContent(name);
            e.appendChild(n);
            doc.appendChild(e);
            sendXml(doc);
        } catch (Exception e) {sendError("Failed to send login event");}
    }

    @Override
    public void sendUserLogoutEvent(String name) {
        try {
            Document doc = newDocument();
            Element e = doc.createElement("event");
            e.setAttribute("name", "userlogout");
            Element n = doc.createElement("name");
            n.setTextContent(name);
            e.appendChild(n);
            doc.appendChild(e);
            sendXml(doc);
        } catch (Exception e) {sendError("Failed to send logout event");}
    }

    @Override
    public void sendMessageEvent(String from, String message) {
        try {
            Document doc = newDocument();
            Element e = doc.createElement("event");
            e.setAttribute("name", "message");

            Element name = doc.createElement("name");
            name.setTextContent(from);
            Element msg = doc.createElement("message");
            msg.setTextContent(message);

            e.appendChild(name);
            e.appendChild(msg);
            doc.appendChild(e);
            sendXml(doc);
        } catch (Exception e) {sendError("Failed to send message");}
    }

    @Override
    public void sendError(String msg) {
        try {
            Document doc = newDocument();
            Element error = doc.createElement("error");
            Element message = doc.createElement("message");
            message.setTextContent(msg);
            error.appendChild(message);
            doc.appendChild(error);
            sendXml(doc);
        } catch (Exception e) {server.log("[ERROR] Cannot send error XML: " + e.getMessage());}
    }

    @Override
    public void sendSuccess(String msg) {
        try {
            Document doc = newDocument();
            Element success = doc.createElement("success");
            Element message = doc.createElement("message");
            message.setTextContent(msg);
            success.appendChild(message);
            doc.appendChild(success);
            sendXml(doc);
        } catch (Exception e) {server.log("[ERROR] Cannot send success XML: " + e.getMessage());}
    }

    @Override
    public void sendSuccess(String msg, String sessionId) {
        try {
            Document doc = newDocument();
            Element success = doc.createElement("success");
            Element message = doc.createElement("message");
            message.setTextContent(msg);
            Element sess = doc.createElement("session");
            sess.setTextContent(sessionId);
            success.appendChild(message);
            success.appendChild(sess);
            doc.appendChild(success);
            sendXml(doc);
        } catch (Exception e) {server.log("[ERROR] Cannot send session XML: " + e.getMessage());}
    }

    private void sendUserList() {
        try {
            Document doc = newDocument();
            Element success = doc.createElement("success");
            Element list = doc.createElement("listusers");

            for (ClientHandler client : server.getLoggedInClients()) {
                Element user = doc.createElement("user");
                Element name = doc.createElement("name");
                name.setTextContent(client.getUserName());
                Element type = doc.createElement("type");
                type.setTextContent(client.getClientType());

                user.appendChild(name);
                user.appendChild(type);
                list.appendChild(user);
            }

            success.appendChild(list);
            doc.appendChild(success);
            sendXml(doc);
        } catch (Exception e) {sendError("Failed to send user list");}
    }
}