# ⚠️ CRITICAL: Rotate MongoDB Credentials

## Security Alert

**GitHub detected exposed MongoDB credentials in the repository history.**

Even though we've removed them from git history, you should **immediately rotate your MongoDB Atlas credentials** as a security best practice.

## Steps to Rotate MongoDB Credentials

### 1. Create New MongoDB User

1. Log into MongoDB Atlas: https://cloud.mongodb.com
2. Navigate to your cluster > Security > Database Access
3. Click "Add New Database User"
4. Create a new user with a new password
5. Grant appropriate permissions

### 2. Update Application

Update your `.env` file with the new credentials:

```bash
MONGODB_URI=mongodb+srv://new-username:new-password@cluster.mongodb.net/?appName=AIChatbot
```

### 3. Delete Old User (After Verification)

Once you've verified the application works with the new credentials:

1. Go to Database Access in MongoDB Atlas
2. Delete the old user account (`chatbot-admin`)
3. This revokes access using the old credentials

## Why This Happened

The initial commit accidentally included a real MongoDB connection string in `infra/env.example`. We've since:

- ✅ Removed the file from git history
- ✅ Updated it with placeholder values only
- ✅ Added `.env` files to `.gitignore`

## Prevention

Going forward:

1. **Never commit `.env` files** - They're already in `.gitignore`
2. **Only use placeholders in example files** - Files like `env.example` should have placeholder values only
3. **Review before committing** - Always check what you're about to commit
4. **Use secret scanning** - GitHub automatically scans for secrets, which is how we caught this

## Verification

To verify the credentials are removed from git history:

```bash
# Search git history for the old password
git log --all -S "BX1Mm0otkfUxrcRf" --source --all
```

If nothing is returned, the credentials have been successfully removed.

## Additional Security Measures

1. **Enable MongoDB IP Whitelist** - Restrict access to specific IPs
2. **Use MongoDB Atlas Network Peering** - For production, use VPC peering
3. **Enable Audit Logging** - Monitor database access
4. **Use Read-Only Users** - For applications that only need read access
5. **Rotate Regularly** - Change credentials every 90 days

## Support

If you need help rotating credentials:
- MongoDB Atlas Documentation: https://docs.atlas.mongodb.com/security/
- MongoDB Support: support@mongodb.com

---

**Action Required:** Rotate your MongoDB credentials immediately if you haven't already done so.

