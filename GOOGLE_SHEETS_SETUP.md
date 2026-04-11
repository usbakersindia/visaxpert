# Google Sheets Integration - UPDATED

## Your Google Sheet Columns (UPDATE REQUIRED)

Add **Email** column to your sheet. New order should be:

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Name | Email | Phone | City | Country | Date |

---

## Updated Apps Script Code

Go to your Google Sheet → **Extensions** → **Apps Script** and replace with:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    // Append the data as a new row (including email)
    sheet.appendRow([
      data.name,
      data.email || '',
      data.phone,
      data.city,
      data.country,
      data.date || new Date().toISOString()
    ]);
    
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

---

## After Updating

1. Save the script (Ctrl+S)
2. Click **Deploy** → **Manage deployments**
3. Click the pencil icon to edit
4. Change version to **New version**
5. Click **Deploy**

Your sheet will now capture emails too!
