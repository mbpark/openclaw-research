#!/bin/bash
# Schedule the anthropic tasks for tomorrow morning
# Run this to schedule:
# bash schedule_task.sh

# Using macOS launchd
cat > /tmp/com.research.report_review.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.research.report_review</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/mitchparker/.openclaw/workspace/documents/research/report_rewrite/trigger.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/mitchparker/.openclaw/workspace/documents/research/report_rewrite</string>
</dict>
</plist>
EOF

echo "Installing launchd job..."
launchctl load /tmp/com.research.report_review.plist
echo "Job scheduled for 2:00 AM"
