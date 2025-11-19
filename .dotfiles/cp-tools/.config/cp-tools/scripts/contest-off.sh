#!/bin/bash

echo "🏳️  EXITING CONTEST MODE"

# Check if the backup exists
if [ -f /etc/hosts.backup ]; then
    echo "♻️  Restoring original /etc/hosts..."
    sudo mv /etc/hosts.backup /etc/hosts
    
    # Flush DNS again so the unblocking happens immediately
    echo "🚽 Flushing DNS cache..."
    sudo resolvectl flush-caches
    sudo systemctl restart systemd-resolved
    
    echo "✅ Distractions allowed. Welcome back to the chaos."
else
    echo "❌ No backup found! Are you sure Contest Mode was on?"
fi
