# Twinkly Squares Wall Clock — Maintenance Guide

Two deployment targets: **Raspberry Pi Zero W** (primary) and **Synology DS720+ NAS** (Docker).

| | Pi Zero W | Synology NAS |
|---|---|---|
| **Host IP** | 192.168.1.101 | NAS IP |
| **Twinkly IP** | 192.168.1.100 | 192.168.1.100 |
| **App location** | /home/pi/twinkly-clock | /volume1/docker/twinkly-clock |
| **Runs via** | systemd service | Docker Compose |

---

## Pi Zero W

### SSH In

```bash
ssh pi@192.168.1.101
```

### Check Status

```bash
sudo systemctl status twinkly-clock
```

### View Logs

```bash
# Live logs
journalctl -u twinkly-clock -f

# Last 100 lines
journalctl -u twinkly-clock -n 100

# Logs since last boot
journalctl -u twinkly-clock -b
```

### Restart

```bash
sudo systemctl restart twinkly-clock
```

### Stop / Start

```bash
sudo systemctl stop twinkly-clock
sudo systemctl start twinkly-clock
```

### Change Theme or Config

Edit the config file — the app hot-reloads theme changes every 60 seconds, no restart needed:

```bash
nano /home/pi/twinkly-clock/config/config.yaml
```

Changes to `fps`, `night_brightness`, `night_start`, or `brightness_schedule` require a restart:

```bash
sudo systemctl restart twinkly-clock
```

### Update Code

```bash
cd /home/pi/twinkly-clock
git pull
sudo systemctl restart twinkly-clock
```

### Update Python Dependencies

```bash
cd /home/pi/twinkly-clock
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart twinkly-clock
```

### First-Time Setup (Fresh Pi)

```bash
# Clone the repo
cd /home/pi
git clone https://github.com/Robiul2015/twinkly_squire_clock.git twinkly-clock
cd twinkly-clock

# Create venv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Edit config
nano config/config.yaml

# Install and start the service
sudo cp twinkly-clock.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable twinkly-clock
sudo systemctl start twinkly-clock
```

### Disable Auto-Start on Boot

```bash
sudo systemctl disable twinkly-clock
```

### Re-enable Auto-Start on Boot

```bash
sudo systemctl enable twinkly-clock
```

### Reboot the Pi

The service starts automatically on boot. To reboot:

```bash
sudo reboot
```

### Watchdog (Cron-Based Auto-Recovery)

systemd already auto-restarts the service on crash, but if it hits a hard failure state the cron watchdog is a safety net. It checks every 5 minutes and forces a restart if the service is inactive.

**Install:**

```bash
# Copy the watchdog script
sudo cp /home/pi/twinkly-clock/scripts/watchdog.sh /usr/local/bin/twinkly-watchdog.sh
sudo chmod +x /usr/local/bin/twinkly-watchdog.sh

# Add to root's crontab (runs every 5 minutes)
sudo crontab -e
```

Add this line:

```cron
*/5 * * * * /usr/local/bin/twinkly-watchdog.sh
```

**Check watchdog activity:**

```bash
sudo tail -f /var/log/twinkly-clock-watchdog.log
```

**Remove the watchdog:**

```bash
sudo crontab -e      # Delete the line
sudo rm /usr/local/bin/twinkly-watchdog.sh
```

### Check Pi Resource Usage

```bash
# CPU and memory
htop

# Disk space
df -h

# Temperature (important for Pi Zero W)
vcgencmd measure_temp
```

---

## Synology NAS (Docker)

### SSH In

```bash
ssh admin@<NAS_IP>
cd /volume1/docker/twinkly-clock
```

### Check Status

```bash
docker compose ps
```

### View Logs

```bash
# Live logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail 100
```

### Restart

```bash
docker compose restart
```

### Stop / Start

```bash
docker compose stop
docker compose start
```

### Change Theme or Config

Edit the config file — theme changes hot-reload every 60 seconds:

```bash
nano config/config.yaml
```

For other config changes, restart:

```bash
docker compose restart
```

### Update Code and Rebuild

```bash
cd /volume1/docker/twinkly-clock
git pull
docker compose build
docker compose up -d
```

### Full Rebuild (No Cache)

```bash
docker compose build --no-cache
docker compose up -d
```

### Remove and Recreate Container

```bash
docker compose down
docker compose up -d
```

### First-Time Setup (Synology)

1. Install **Container Manager** from Synology Package Center
2. Enable SSH in **Control Panel > Terminal & SNMP**
3. SSH in and run:

```bash
cd /volume1/docker
git clone https://github.com/Robiul2015/twinkly_squire_clock.git twinkly-clock
cd twinkly-clock
nano config/config.yaml          # Set your twinkly_ip
nano docker-compose.yml          # Set your timezone
docker compose build
docker compose up -d
```

---

## Common Tasks (Both Platforms)

### Change the Active Theme

In `config/config.yaml`, set the `theme` field. Available themes:

| Key | Name |
|-----|------|
| `ocean_drift` | Calm cyan-blue with wave border |
| `ember_glow` | Warm fireplace with flickering embers |
| `neon_synthwave` | Retro 80s magenta/cyan |
| `minimal_white` | Clean white with breathing effect |
| `aurora_borealis` | Shifting green/purple aurora |
| `time_of_day` | Adaptive — changes with actual time |
| `sunset_boulevard` | Golden hour gradient |
| `cyberpunk_tokyo` | Hot pink/lime pixel chase |
| `forest_canopy` | Natural greens with shimmer |
| `lava_lamp` | Slow-morphing warm blobs |
| `ice_crystal` | Cold whites with sparkle |
| `rainbow_shift` | Digits cycle full spectrum |
| `green_lava` | Green digits with lava background |
| `matrix_terminal` | Phosphor green with scanlines and falling code rain |

No restart needed — theme hot-reloads within 60 seconds.

### Change the Font

In `config/config.yaml`, set the `font` field:

| Font | Style |
|------|-------|
| `5x7` | Classic dot matrix (default) |
| `5x7r` | Rounded, softer curves |
| `5x7b` | Bold, thick strokes |

Requires a restart.

### Adjust Brightness Schedule

In `config/config.yaml`:

```yaml
brightness: 95              # Default daytime brightness (0-100)
night_brightness: 5         # Night mode brightness
night_start: 22             # Night starts at 10 PM
brightness_schedule:
  8: 95                     # 8 AM - full brightness
  20: 60                    # 8 PM - dim for evening
```

Requires a restart.

### Twinkly Device Not Responding

1. Check the Twinkly device is powered on and connected to WiFi
2. Ping it: `ping 192.168.1.100`
3. If the IP changed, update `twinkly_ip` in `config/config.yaml` and restart
4. The app auto-reconnects with exponential backoff — check logs for connection errors

### Clock Shows Wrong Time

Check the timezone is set correctly:
- **Pi:** `sudo timedatectl set-timezone Australia/Sydney`
- **Docker:** verify `TZ=Australia/Sydney` in `docker-compose.yml`
