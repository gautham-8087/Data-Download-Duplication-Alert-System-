const express = require('express');
const cors = require('cors'); // Import CORS middleware
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
app.use(express.json());

// Enable CORS for all routes
app.use(cors());

// Path to Downloads folder
const DOWNLOADS_DIR = path.join(require('os').homedir(), 'Downloads');

app.post('/check', (req, res) => {
  const fileName = req.body.fileName;
  const filePath = path.join(DOWNLOADS_DIR, fileName);

  // Check if the file exists
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (!err) {
      // If file exists, return a response with the path
      res.json({ exists: true, path: filePath });

      // Use a desktop notification (for Linux, or adapt to your OS)
      exec(`notify-send "File Already Exists" "The file '${fileName}' already exists at: ${filePath}"`);
    } else {
      // If file doesn't exist, allow download
      res.json({ exists: false });
    }
  });
});

app.listen(3000, () => {
  console.log('File check server running on port 3000');
});
