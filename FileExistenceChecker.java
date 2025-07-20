import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import javax.swing.*;

public class FileExistenceChecker {

    public static void main(String[] args) {
        // Create a frame for the application
        JFrame frame = new JFrame("File Existence Checker");
        frame.setSize(400, 200);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        // Create a text field for file name input
        JTextField fileNameField = new JTextField();
        frame.add(fileNameField, BorderLayout.CENTER);

        // Create a button to check file existence
        JButton checkButton = new JButton("Check File");
        frame.add(checkButton, BorderLayout.SOUTH);

        // Add action listener to the button
        checkButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String fileName = fileNameField.getText();
                String homeDir = System.getProperty("user.home");
                File file = new File(homeDir + File.separator + "Downloads" + File.separator + fileName);

                if (file.exists()) {
                    // Show a dialog if the file exists
                    JOptionPane.showMessageDialog(frame, 
                        "The file \"" + fileName + "\" already exists at: " + file.getAbsolutePath(),
                        "File Exists",
                        JOptionPane.INFORMATION_MESSAGE);
                } else {
                    // Show a dialog if the file does not exist
                    JOptionPane.showMessageDialog(frame, 
                        "The file \"" + fileName + "\" does not exist.",
                        "File Not Found",
                        JOptionPane.WARNING_MESSAGE);
                }
            }
        });

        // Display the frame
        frame.setVisible(true);
    }
}
