package lab_4.factory.gui;
import lab_4.factory.controller.FactoryController;
import javax.swing.*;
import java.awt.*;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

public class FactoryView {
    private final FactoryController controller;
    private final JLabel producedCarsLabel;
    private final JLabel storageStatusLabel;
    private final JSlider supplierSpeedSlider;
    private final JSlider dealerSpeedSlider;
    private SwingWorker<Void, Void> updateProducedCarsWorker;
    private SwingWorker<Void, Void> updateStorageStatusWorker;
    private volatile boolean running = false;

    public FactoryView(String configPath) {
        controller = new FactoryController(configPath);

        JFrame frame = new JFrame("Factory Simulator");
        frame.setSize(500, 350);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new GridLayout(5, 1));

        supplierSpeedSlider = new JSlider(100, 2000, 500);
        dealerSpeedSlider = new JSlider(100, 2000, 1000);

        supplierSpeedSlider.setMajorTickSpacing(500);
        supplierSpeedSlider.setPaintTicks(true);
        supplierSpeedSlider.setPaintLabels(true);

        dealerSpeedSlider.setMajorTickSpacing(500);
        dealerSpeedSlider.setPaintTicks(true);
        dealerSpeedSlider.setPaintLabels(true);

        JPanel supplierPanel = new JPanel();
        supplierPanel.add(new JLabel("Supplier Speed:"));
        supplierPanel.add(supplierSpeedSlider);

        JPanel dealerPanel = new JPanel();
        dealerPanel.add(new JLabel("Dealer Speed:"));
        dealerPanel.add(dealerSpeedSlider);

        producedCarsLabel = new JLabel("Produced Cars: 0", SwingConstants.CENTER);
        storageStatusLabel = new JLabel("Storage Status: Loading...", SwingConstants.CENTER);

        JButton startButton = new JButton("Start");
        JButton stopButton = new JButton("Stop");

        startButton.addActionListener(e -> startFactory());
        stopButton.addActionListener(e -> stopFactory());

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(startButton);
        buttonPanel.add(stopButton);

        frame.add(supplierPanel);
        frame.add(dealerPanel);
        frame.add(producedCarsLabel);
        frame.add(storageStatusLabel);
        frame.add(buttonPanel);

        supplierSpeedSlider.addChangeListener(e -> controller.setSupplierDelay(supplierSpeedSlider.getValue()));
        dealerSpeedSlider.addChangeListener(e -> controller.setDealerDelay(dealerSpeedSlider.getValue()));

        frame.addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent e) { stopFactory(); }
        });
        frame.setVisible(true);
    }

    private void startFactory() {
        if (!running) {
            running = true;
            controller.start();

            updateProducedCarsWorker = new SwingWorker<>() {
                @Override
                protected Void doInBackground() {
                    while (running) {
                        SwingUtilities.invokeLater(() -> producedCarsLabel.setText("Produced Cars: " + controller.getProducedCars()));
                        try {
                            Thread.sleep(1000);
                        } catch (InterruptedException e) {
                            break;
                        }
                    }
                    return null;
                }
            };

            updateStorageStatusWorker = new SwingWorker<>() {
                @Override
                protected Void doInBackground() {
                    while (running) {
                        SwingUtilities.invokeLater(() -> storageStatusLabel.setText("Storage Status: " + controller.getStorageStatus()));
                        try {
                            Thread.sleep(100);
                        } catch (InterruptedException e) {
                            break;
                        }
                    }
                    return null;
                }
            };

            updateProducedCarsWorker.execute();
            updateStorageStatusWorker.execute();
        }
    }

    private void stopFactory() {
        running = false;
        controller.stop();
        if (updateProducedCarsWorker != null) updateProducedCarsWorker.cancel(true);
        if (updateStorageStatusWorker != null) updateStorageStatusWorker.cancel(true);
    }
}