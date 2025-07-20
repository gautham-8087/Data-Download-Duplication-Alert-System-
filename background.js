chrome.downloads.onDeterminingFilename.addListener(function (downloadItem, suggest) {
    const fileName = downloadItem.filename;
    
    // Send the filename to the Node.js server for existence check
    fetch('http://localhost:3000/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fileName: fileName })
    })
    .then(response => response.json())
    .then(data => {
      if (data.exists) {
        // If the file exists, show a Chrome extension notification using a transparent icon
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'transparent.png', // Transparent or minimal icon
          title: 'File Already Exists',
          message: `The file "${fileName}" already exists at: ${data.path}`
        });
        
        // Suggest the filename anyway
        suggest({ filename: fileName });
      } else {
        // Proceed with download if the file doesn't exist
        suggest({ filename: fileName });
      }
    })
    .catch(err => {
      console.error('Error checking file:', err);
      // Proceed with download if there's an error
      suggest({ filename: fileName });
    });
});
