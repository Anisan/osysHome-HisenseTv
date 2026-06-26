# HisenseTv - Hisense TV Control

![HisenseTv Icon](static/hisensetv.png)

MQTT-based control system for Hisense smart TVs.

## Description

The `HisenseTv` module provides control capabilities for Hisense smart TVs via MQTT protocol for the osysHome platform. It enables remote control, state monitoring, and property linking.

## Main Features

- ✅ **MQTT Control**: MQTT-based TV control
- ✅ **Device Management**: Manage multiple Hisense TVs
- ✅ **Property Linking**: Link TV controls to object properties
- ✅ **State Monitoring**: Monitor TV state
- ✅ **Command Support**: Send commands to TV

## Admin Panel

The module provides an admin interface for:
- Viewing Hisense TV devices
- Configuring device settings
- Managing TV data/commands
- Linking controls to properties

## Configuration

- **Device IP**: TV IP address
- **MQTT Settings**: MQTT broker configuration
- **Device ID**: Unique device identifier

## Usage

### Adding TV Device

1. Navigate to HisenseTv module
2. Click "Add Device"
3. Enter TV IP address
4. Configure MQTT settings
5. Link controls to object properties

## Technical Details

- **Protocol**: MQTT
- **Device Type**: Hisense smart TVs
- **Connection**: Per-device MQTT client

## Version

Current version: **0.2**

## Category

Devices

## Actions

The module provides the following actions:
- `cycle` - Background MQTT communication

## Requirements

- Flask
- paho-mqtt
- SQLAlchemy
- osysHome core system

## Author

Eraser

## License

See the main osysHome project license

