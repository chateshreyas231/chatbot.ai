# VPN Troubleshooting Guide

Having trouble connecting to the company VPN? This guide covers common issues and solutions.

## Common Issues

### Issue 1: Cannot Connect to VPN Server

**Symptoms**: Connection times out or shows "Unable to connect"

**Solutions**:
1. Check your internet connection - ensure you can browse other websites
2. Verify VPN server address is correct (vpn.company.com)
3. Try switching to mobile hotspot to rule out network issues
4. Restart your network adapter:
   - Windows: Network Settings > Change adapter options > Disable/Enable
   - Mac: System Preferences > Network > Turn Wi-Fi off/on

### Issue 2: Authentication Fails

**Symptoms**: Login credentials rejected

**Solutions**:
1. Verify username format (use email address: firstname.lastname@company.com)
2. Check if password expired - reset via company portal
3. Ensure MFA is properly configured
4. Try logging into company portal first to verify credentials work

### Issue 3: Slow Connection Speed

**Symptoms**: Very slow internet while connected to VPN

**Solutions**:
1. Connect to VPN server closest to your location
2. Disable split tunneling if enabled
3. Check if other applications are using bandwidth
4. Try connecting during off-peak hours

### Issue 4: VPN Drops Frequently

**Symptoms**: Connection disconnects after a few minutes

**Solutions**:
1. Update VPN client to latest version
2. Check for firewall or antivirus blocking VPN
3. Disable power saving mode on network adapter
4. Try different VPN protocol (IKEv2 vs SSL)

## Mac-Specific Issues

### Issue: VPN Client Not Installing

**Solution**: 
- Allow apps from identified developers in System Preferences > Security
- Run: `sudo spctl --master-disable` (for testing only, re-enable after)

### Issue: Can't Find VPN Connection

**Solution**:
- System Preferences > Network > Click + > Add VPN connection
- Type: IKEv2
- Server: vpn.company.com
- Authentication: Username and password

## Windows-Specific Issues

### Issue: VPN Error 789

**Solution**: 
- Check Windows Firewall settings
- Ensure IKE and AuthIP IPsec Keying Modules service is running
- Reset network settings: `netsh winsock reset`

### Issue: Cannot Find VPN Connection

**Solution**:
- Settings > Network & Internet > VPN > Add VPN connection
- VPN provider: Windows (built-in)
- Connection name: Company VPN
- Server name: vpn.company.com

## Advanced Troubleshooting

### Check VPN Logs
- Windows: Event Viewer > Windows Logs > System
- Mac: Console app > Look for VPN entries

### Test Connectivity
Run these commands:
```
ping vpn.company.com
telnet vpn.company.com 443
```

### Reset VPN Settings
- Remove and recreate VPN connection
- Clear stored credentials
- Reinstall VPN client

## Still Not Working?

If none of these solutions work:
1. Collect error messages and screenshots
2. Note when the issue started
3. Check if others in your location have the same issue
4. Open a support ticket with all this information

## Contact Support

For urgent VPN issues, call IT support at ext. 1234 or create a ticket with priority P2.

