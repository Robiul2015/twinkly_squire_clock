#!/bin/bash
# Watchdog for the Twinkly clock service.
# Run every 5 minutes via cron — restarts the service if it's not active.

SERVICE="twinkly-clock"
LOG="/var/log/twinkly-clock-watchdog.log"

if ! systemctl is-active --quiet "$SERVICE"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') $SERVICE is not running — restarting" >> "$LOG"
    systemctl reset-failed "$SERVICE"
    systemctl restart "$SERVICE"
    sleep 5
    if systemctl is-active --quiet "$SERVICE"; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') $SERVICE restart succeeded" >> "$LOG"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') $SERVICE restart FAILED" >> "$LOG"
    fi
fi
