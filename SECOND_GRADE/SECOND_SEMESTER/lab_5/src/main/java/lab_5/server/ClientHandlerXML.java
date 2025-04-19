package lab_5.server;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.net.Socket;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;

public class ClientHandlerXML extends ClientHandler {
    private DocumentBuilder builder;

    public ClientHandlerXML(Socket socket, DataInputStream dis, DataOutputStream dos, Server server) {
        super(socket, dis, dos, server);
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            builder = factory.newDocumentBuilder();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public void run() {
        boolean normalLogout = false;
        try {
            label:
            while (true) {
                int length;
                try {
                    length = dis.readInt();
                } catch (EOFException eof) {
                    break;
                }
                if (length <= 0) {
                    continue;
                }
                byte[] data = new byte[length];
                dis.readFully(data);
                String request = new String(data, StandardCharsets.UTF_8);
                Document doc;
                try {
                    doc = builder.parse(new ByteArrayInputStream(data));
                } catch (Exception parseEx) {
                    server.log("Failed to parse XML from client: " + parseEx.getMessage());
                    continue;
                }
                Element root = doc.getDocumentElement();
                if (root == null || !root.getTagName().equals("command")) {
                    continue;
                }
                String command = root.getAttribute("name");
                if (command == null) {
                    continue;
                }
                switch (command) {
                    case "login" -> {
                        String loginName = "";
                        String loginType = "";
                        NodeList nameNodes = root.getElementsByTagName("name");
                        if (nameNodes.getLength() > 0) {
                            loginName = nameNodes.item(0).getTextContent().trim();
                        }
                        NodeList typeNodes = root.getElementsByTagName("type");
                        if (typeNodes.getLength() > 0) {
                            loginType = typeNodes.item(0).getTextContent().trim();
                        }
                        if (loginName.isEmpty()) {
                            sendErrorResponse("Invalid name");
                            continue;
                        }
                        synchronized (server) {
                            if (server.isNameTaken(loginName)) {
                                sendErrorResponse("Name already taken");
                                continue;
                            }
                            this.userName = loginName;
                            this.clientType = !loginType.isEmpty() ? loginType : "XMLClient";
                            this.sessionId = Server.generateSessionId();
                            this.loggedIn = true;
                            sendSuccessResponse("<session>" + sessionId + "</session>");
                            server.broadcastUserLogin(this.userName, this.sessionId);
                            server.log("User logged in: " + this.userName + " (" + this.clientType + ")");
                        }
                    }
                    case "list" -> {
                        if (!loggedIn) {
                            sendErrorResponse("Not logged in");
                            continue;
                        }
                        NodeList sessionNodes = root.getElementsByTagName("session");
                        String sess = (sessionNodes.getLength() > 0 ? sessionNodes.item(0).getTextContent() : null);
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
                        NodeList sessionNodes = root.getElementsByTagName("session");
                        String sess = (sessionNodes.getLength() > 0 ? sessionNodes.item(0).getTextContent() : null);
                        if (sess == null || !sess.equals(this.sessionId)) {
                            sendErrorResponse("Invalid session");
                            continue;
                        }
                        NodeList msgNodes = root.getElementsByTagName("message");
                        String msg = (msgNodes.getLength() > 0 ? msgNodes.item(0).getTextContent() : "");
                        server.broadcastMessage(this.userName, msg, this.sessionId);
                        sendSuccessResponse("");
                    }
                    case "logout" -> {
                        if (!loggedIn) {
                            break label;
                        }
                        NodeList sessionNodes = root.getElementsByTagName("session");
                        String sess = (sessionNodes.getLength() > 0 ? sessionNodes.item(0).getTextContent() : null);
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
        String xml = "<event name=\"userlogin\"><name>" + escapeXml(name) + "</name></event>";
        sendXml(xml);
    }

    @Override
    public void sendUserLogoutEvent(String name) {
        String xml = "<event name=\"userlogout\"><name>" + escapeXml(name) + "</name></event>";
        sendXml(xml);
    }

    @Override
    public void sendMessageEvent(String fromUser, String message) {
        String xml = "<event name=\"message\"><message>" + escapeXml(message) + "</message><name>" + escapeXml(fromUser) + "</name></event>";
        sendXml(xml);
    }

    @Override
    public void sendSuccessResponse(String content) {
        String xml;
        if (content != null && !content.isEmpty()) {
            xml = "<success>" + content + "</success>";
        } else {
            xml = "<success></success>";
        }
        sendXml(xml);
    }

    @Override
    public void sendErrorResponse(String reason) {
        String xml = "<error><message>" + escapeXml(reason) + "</message></error>";
        sendXml(xml);
    }

    @Override
    public void sendUserList(List<ClientHandler> clients) {
        StringBuilder sb = new StringBuilder();
        sb.append("<success><listusers>");
        for (ClientHandler c : clients) {
            if (!c.isLoggedIn()) continue;
            sb.append("<user><name>").append(escapeXml(c.getUserName())).append("</name>");
            sb.append("<type>").append(escapeXml(c.clientType)).append("</type></user>");
        }
        sb.append("</listusers></success>");
        sendXml(sb.toString());
    }

    private String escapeXml(String text) {
        if (text == null) return "";
        String result = text;
        result = result.replace("&", "&amp;");
        result = result.replace("<", "&lt;");
        result = result.replace(">", "&gt;");
        result = result.replace("\"", "&quot;");
        result = result.replace("'", "&apos;");
        return result;
    }

    private void sendXml(String xml) {
        try {
            byte[] bytes = xml.getBytes(StandardCharsets.UTF_8);
            dos.writeInt(bytes.length);
            dos.write(bytes);
            dos.flush();
        } catch (IOException e) {
            server.log("Failed to send XML to " + this.userName);
        }
    }
}