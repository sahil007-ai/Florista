# Florista Lead Capture — Google Sheets Setup

The B2B enquiry form on `contact.html` does two things on submit:

1. **Logs the lead to a Google Sheet** via a Google Apps Script Web App (background, fire-and-forget).
2. **Opens WhatsApp** with a pre-filled message so the user can also send it directly.

Step 1 matters because step 2 only *opens* WhatsApp — the user still has to
tap Send inside WhatsApp for the message to actually reach Florista. If they
bail or the popup is blocked, the lead is still captured by step 1.

The endpoint URL is configured in `js/main.js` as the constant
`FORM_ENDPOINT_URL`. Until that URL is set, the form still works as a
WhatsApp redirect — it just won't log to a spreadsheet.

---

## One-time setup (10 minutes)

### 1. Create a Google Sheet

- Go to <https://sheets.google.com/> and create a new spreadsheet.
- Rename it something like **"Florista Leads"**. (Internal only — buyers never see this.)

### 2. Open the Apps Script editor

- In the sheet, click **Extensions → Apps Script**.
- A new tab opens with a blank `Code.gs` file.
- Delete the placeholder `function myFunction() { ... }`.

### 3. Paste this script

```javascript
// Florista Lead Capture — Google Apps Script Web App
// Receives JSON POSTs from the contact form on theflorista.in
// and appends each enquiry as a new row.

const SHEET_NAME = 'Leads';

function doPost(e) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
    }

    // First-time: write the header row.
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        'Received At',
        'Name & Company',
        'WhatsApp Number',
        'City',
        'Interested In',
        'Page',
        'User Agent'
      ]);
      sheet.setFrozenRows(1);
    }

    const data = JSON.parse(e.postData.contents);
    sheet.appendRow([
      new Date(),
      data.company  || '',
      data.phone    || '',
      data.city     || '',
      data.interest || '',
      data.page     || '',
      data.userAgent || ''
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    // Errors are returned as JSON; the website doesn't read them
    // (no-cors), but they're useful when testing manually.
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Lets you visit the /exec URL in a browser to confirm it's deployed.
function doGet() {
  return ContentService.createTextOutput(
    'Florista lead capture endpoint is alive. Use POST.'
  );
}
```

- Click the **Save** icon (or `Ctrl+S` / `Cmd+S`).
- Name the project (e.g. "Florista Lead Capture").

### 4. Deploy as a Web App

- Click **Deploy → New deployment** (top-right).
- Click the gear icon next to "Select type" and choose **Web app**.
- Fill in:
  - **Description:** Florista Lead Capture
  - **Execute as:** *Me (your-email@gmail.com)*
  - **Who has access:** ⚠️ **Anyone** *(this is required — the form on the website needs to POST without logging in)*
- Click **Deploy**.
- Google will ask you to **authorize the script**. Click through the warnings:
  - "Authorize access" → choose your account
  - "Google hasn't verified this app" → click **Advanced** → **Go to Florista Lead Capture (unsafe)**
  - Allow the requested permissions (it just needs to edit your sheet)
- After deploy, you'll see a **Web app URL** ending in `/exec`. Example:
  ```
  https://script.google.com/macros/s/AKfycbxxxxxxxxxxxx/exec
  ```
- **Copy this URL.**

### 5. Wire it into the website

- Open `js/main.js`.
- Find the line:
  ```javascript
  const FORM_ENDPOINT_URL = ''; // <-- paste your Apps Script /exec URL here
  ```
- Replace `''` with your URL in quotes:
  ```javascript
  const FORM_ENDPOINT_URL = 'https://script.google.com/macros/s/AKfycb.../exec';
  ```
- Commit & deploy the site.

### 6. Test

- Open <https://www.theflorista.in/contact.html>.
- Fill the form with test data (use your own number).
- Click **Send Enquiry on WhatsApp**.
- Check your Google Sheet — a new row should appear within a few seconds.

---

## Updating the script later

If you change the script (e.g. to add a column), you must redeploy:

- **Deploy → Manage deployments**
- Click the pencil (edit) icon on the active deployment
- **Version:** New version → **Deploy**

The `/exec` URL stays the same, so the website doesn't need any change.

---

## Troubleshooting

**No rows appear in the sheet after submitting.**
- Confirm "Who has access" is set to **Anyone**, not "Anyone with Google account".
- Open the `/exec` URL directly in a browser — you should see the message
  "Florista lead capture endpoint is alive."
- In Apps Script, click **Executions** (left sidebar) — you'll see every
  call and its error if any.

**Browser console shows a CORS or 405 error.**
- Apps Script returns CORS errors for `application/json` content-type but
  accepts `text/plain;charset=utf-8`. The form code already sends as plain
  text and uses `mode: 'no-cors'`, so this should not happen unless the
  setup was modified.

**Spam submissions.**
- Apps Script web apps don't have built-in rate limiting. If you start
  getting spam, the easiest mitigations are:
  - Add a hidden honeypot field to the form (a field bots fill in but
    real users don't see) and reject any payload that has it filled.
  - Check `e.postData.contents` for obvious junk (e.g. `phone` that doesn't
    contain digits) and skip those rows.

---

## Free-tier limits

Google Apps Script web apps allow generous quotas — for a contact form,
you'll never hit them. Reference: <https://developers.google.com/apps-script/guides/services/quotas>
