# LocalMEL - Local Mitsubishi Electric Integration for Home Assistant

A Home Assistant integration that allows local control of Mitsubishi Electric air conditioners without cloud dependency.

## Features

- Local control without internet connection
- Direct communication with AC units
- Support for basic operations (temperature, mode, fan speed)
- No cloud account required
- Secure encrypted communication

## Installation

1. Copy the `custom_components/mitsubishi_local` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click the "+ ADD INTEGRATION" button
5. Search for "Mitsubishi Local"
6. Follow the configuration steps

## Configuration

You'll need:
- IP address of your AC unit
- Port number (default: 8317)
- Encryption key (if your model requires it)

## Supported Models

This integration works with Mitsubishi Electric air conditioners that have built-in WiFi modules.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This project is not affiliated with Mitsubishi Electric Corporation. Use at your own risk.