# Power Management Privilege Escalation Setup

The homepage power management features (CPU governor and I/O scheduler control) require root privileges to modify system settings. To avoid running the entire service as root, we use privilege escalation tools.

## Supported Tools

The service automatically detects and uses one of these tools (in order of preference):

1. **pkexec** (recommended) - PolicyKit-based, GUI-friendly
2. **sudo** - Traditional privilege escalation
3. **doas** - OpenBSD-style alternative to sudo

## Quick Setup

### Option 1: Using pkexec (Recommended for Desktop)

1. **Install polkit** (if not already installed):
   ```bash
   # Debian/Ubuntu
   sudo apt install policykit-1
   
   # Arch Linux
   sudo pacman -S polkit
   
   # Fedora
   sudo dnf install polkit
   ```

2. **Install the polkit policy** (allows passwordless power management):
   ```bash
   sudo cp scripts/com.homepage.power-mgmt.policy /usr/share/polkit-1/actions/
   
   # Update the path in the policy file to match your installation:
   sudo sed -i "s|/home/andrath/Code/homepage|$(pwd)|" /usr/share/polkit-1/actions/com.homepage.power-mgmt.policy
   ```

3. **Restart your session** or reload polkit:
   ```bash
   sudo systemctl restart polkit
   ```

### Option 2: Using sudo

1. **Add sudoers entry** to allow the helper script without password:
   ```bash
   echo "$USER ALL=(ALL) NOPASSWD: $(pwd)/scripts/power-mgmt-helper.sh" | sudo tee /etc/sudoers.d/homepage-power-mgmt
   sudo chmod 440 /etc/sudoers.d/homepage-power-mgmt
   ```

### Option 3: Using doas

1. **Install doas**:
   ```bash
   # Arch Linux
   sudo pacman -S opendoas
   
   # Debian/Ubuntu (may need to build from source)
   ```

2. **Configure doas** in `/etc/doas.conf`:
   ```
   permit nopass $USER cmd /path/to/homepage/scripts/power-mgmt-helper.sh
   ```

## Security Notes

- The helper script (`power-mgmt-helper.sh`) validates all inputs to prevent command injection
- Only allows alphanumeric characters, hyphens, and underscores in governor/scheduler names
- Only allows alphanumeric characters in device names (no path traversal)
- Timeout set to 5 seconds to prevent hanging

## Testing

Test the setup manually:

```bash
# Test with pkexec
pkexec ./scripts/power-mgmt-helper.sh set-governor performance

# Test with sudo
sudo ./scripts/power-mgmt-helper.sh set-governor powersave

# Test with doas
doas ./scripts/power-mgmt-helper.sh set-scheduler nvme0n1 mq-deadline
```

## Troubleshooting

**"No privilege escalation tool found"**
- Install pkexec, sudo, or doas

**"Authentication required" popup every time**
- Install the polkit policy (for pkexec)
- Or configure sudo/doas for passwordless execution

**"Failed to set governor"**
- Check that the governor name is valid: `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors`
- Verify the helper script is executable: `chmod +x scripts/power-mgmt-helper.sh`

**"Permission denied" errors**
- Check polkit policy is installed correctly
- Verify sudoers/doas configuration
- Check file permissions on the helper script
