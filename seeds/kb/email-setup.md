# Email Setup and Troubleshooting

Complete guide for setting up and troubleshooting email issues.

## Initial Email Setup

### Outlook Setup
1. Open Outlook
2. Click "Add Account"
3. Enter your email address (firstname.lastname@company.com)
4. Click "Connect"
5. Enter your password when prompted
6. Complete MFA if required
7. Outlook will configure automatically

### Apple Mail Setup (Mac)
1. Open Mail app
2. Mail > Add Account
3. Select "Exchange"
4. Enter:
   - Name: Your name
   - Email: your.email@company.com
   - Password: Your password
5. Click "Sign In"
6. Select apps to use (Mail, Calendar, Notes)
7. Click "Done"

### Mobile Setup (iOS/Android)
1. Open Settings
2. Accounts & Passwords (iOS) or Accounts (Android)
3. Add Account > Exchange
4. Enter email and password
5. Server: outlook.office365.com
6. Complete MFA

## Common Issues

### Issue 1: Can't Send Emails

**Symptoms**: Emails stuck in Outbox

**Solutions**:
1. Check internet connection
2. Verify email account is authenticated (Settings > Accounts)
3. Check if account is locked (try logging into web portal)
4. Restart email client
5. Clear Outlook cache:
   - Close Outlook
   - Delete .ost file (Windows: %LOCALAPPDATA%\Microsoft\Outlook)
   - Reopen Outlook

### Issue 2: Not Receiving Emails

**Solutions**:
1. Check spam/junk folder
2. Verify account is syncing (check sync status)
3. Check mailbox quota (may be full)
4. Verify rules aren't auto-deleting or moving emails
5. Try web version (portal.office.com)

### Issue 3: "Authentication Failed" Error

**Solutions**:
1. Re-enter password (may have expired)
2. Update account credentials
3. Check MFA is properly configured
4. Verify account isn't locked
5. Remove and re-add account

### Issue 4: Calendar Not Syncing

**Solutions**:
1. Check calendar permissions in account settings
2. Verify Exchange calendar is enabled
3. Sync calendar manually: View > Send/Receive > Update Folder
4. Restart Outlook/Mail app

## Email Settings

### Server Information
- **Exchange Server**: outlook.office365.com
- **IMAP**: outlook.office365.com (port 993, SSL)
- **SMTP**: smtp.office365.com (port 587, STARTTLS)
- **POP3**: outlook.office365.com (port 995, SSL)

### Recommended Settings
- Sync email: Last 12 months
- Download attachments: On demand
- Auto-archive: Enabled (older than 12 months)
- Junk email: Automatic filtering enabled

## Best Practices

1. **Archive regularly** - Keep inbox under 10,000 items
2. **Use folders** - Organize important emails
3. **Check spam weekly** - Important emails may be misclassified
4. **Update recovery info** - Keep alternate email current
5. **Use mobile sync** - Stay connected on the go

## Advanced Features

### Shared Mailboxes
To access a shared mailbox:
1. Request access from mailbox owner
2. Outlook > File > Account Settings > Account Settings
3. Click "Change" > "More Settings" > "Advanced" > "Add"
4. Enter shared mailbox email

### Email Rules
Create rules to automatically organize:
1. Outlook > Home > Rules > Manage Rules
2. Create new rule
3. Set conditions (sender, subject, keywords)
4. Set actions (move, forward, delete)

### Email Signatures
Add professional signature:
1. Outlook > File > Options > Mail > Signatures
2. Create new signature
3. Include: Name, Title, Email, Phone, Company

## Need Help?

Common resolutions:
- **Can't login**: Reset password via self-service portal
- **Missing emails**: Check spam and other folders
- **Syncing issues**: Remove and re-add account
- **Quota exceeded**: Archive old emails or contact IT to increase quota

If issues persist, create a support ticket with:
- Email address
- Error messages (screenshot if possible)
- When issue started
- Steps you've already tried

