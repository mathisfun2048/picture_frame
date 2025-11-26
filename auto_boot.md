# Auto-Boot

## Step 1: Create Systemd Service

### Terminal Command
''' sudo nano /etc/systemd/system/picture-frame.service '''

### Code

'''
[Unit]
Description=E-Ink Picture Frame
After=network.target

[Service]
Type=simple
User= <Your User Name>
WorkingDirectory=/home/<Your User Name>/picture_frame
ExecStart=/home/<Your User Name>/picture_frame/venv/bin/python /home/<Your User Name>/picture_frame/src/main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''

## Step 2: Enable Service

### Reload systemd to recognize new service
''' sudo systemctl daemon-reload '''

### Enable service to start on boot
''' sudo systemctl enable picture-frame.service '''

### Start service now
''' sudo systemctl start picture-frame.service '''

### Check status
''' sudo systemctl status picture-frame.service '''


## Useful Commands

### Stop the service
''' sudo systemctl stop picture-frame.service '''

### Restart the service
''' sudo systemctl restart picture-frame.service '''

### View logs
''' sudo journalctl -u picture-frame.service -f '''

### View last 50 lines of logs
''' sudo journalctl -u picture-frame.service -n 50 '''