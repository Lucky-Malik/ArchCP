#!/bin/bash

echo "⚔️  ENTERING CONTEST MODE ⚔️"

# 1. Kill Distractions
echo "🔪 Killing distraction apps..."
# Add or remove apps from this list as needed
killall -q discord slack telegram-desktop spotify firefox chromium

# 2. Backup /etc/hosts (Crucial: Only backup if one doesn't exist!)
# This prevents overwriting a "clean" backup with a "dirty" one if you run this script twice.
if [ ! -f /etc/hosts.backup ]; then
    echo "💾 Backing up /etc/hosts..."
    sudo cp /etc/hosts /etc/hosts.backup
else
    echo "⚠️  Backup already exists. Assuming we are already in contest mode."
fi

# 3. Apply the Blocklist
echo "🚫 Blocking distractions (IPv4 & IPv6)..."

# Define the sites to block
BLOCK_LIST=(
    "youtube.com" "www.youtube.com"
    "reddit.com" "www.reddit.com"
    "twitter.com" "www.twitter.com"
    "facebook.com" "www.facebook.com"
    "instagram.com" "www.instagram.com"
    "netflix.com" "www.netflix.com"
    "discord.com" "www.discord.com"
)

for site in "${BLOCK_LIST[@]}"; do
    # Block IPv4
    echo "127.0.0.1 $site" | sudo tee -a /etc/hosts > /dev/null
    # Block IPv6 (Fixes the ping/bypass issue)
    echo "::1 $site" | sudo tee -a /etc/hosts > /dev/null
done

# 4. Flush DNS Cache (Essential for immediate effect)
echo "🚽 Flushing DNS cache..."
sudo resolvectl flush-caches
sudo systemctl restart systemd-resolved

echo "✅ Focus enabled. Good luck, zcxdr!"
