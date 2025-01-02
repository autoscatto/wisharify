# Wi-Fi QR Code Generator

This Python script generates a QR code for connecting to your currently active Wi-Fi network. The QR code encodes the SSID and password, which can be scanned by devices to automatically connect to the network. The program fetches the SSID and password from your system’s network manager and securely retrieves the password via a graphical authentication prompt.

## Features
- Retrieves the current Wi-Fi SSID and password.
- Generates a QR code for Wi-Fi connection.
- Displays the QR code in a graphical interface using Tkinter.
- The window can be closed via the "Exit" button or the window close button.

## Requirements
- **Python 3.7+**
- **Libraries:**
  - `qrcode[pil]`
  - `Pillow`
  - `keyring`

## Installation

To set up the environment and install dependencies, follow these steps:

1. **Install `uv`** if you haven't already:

   see [astral-sh/uv](https://github.com/astral-sh/uv)

2. **Install project dependencies**:

   In the project directory, run the following command to install all required dependencies:

   ```bash
   uv install
   ```

   This will automatically install the dependencies declared in the `pyproject.toml` file.

## How It Works
1. The script first checks the currently connected Wi-Fi SSID using the `nmcli` command.
2. It then retrieves the password for the SSID using system utilities with `pkexec` (for secure authentication).
3. A QR code is generated that encodes the Wi-Fi credentials in the following format:
   ```
   WIFI:T:WPA;S:<SSID>;P:<password>;;
   ```
4. The QR code is displayed in a graphical window using Tkinter.
5. The user can close the window either by pressing the "Exit" button or the window close button.

## Usage

### Running the Script
To run the script, simply execute it from the terminal or your preferred IDE:

```bash
python main.py
```

- The script will automatically detect your current Wi-Fi SSID and attempt to retrieve the password.
- If the password is not available in the system keyring, the script will ask for authentication and attempt to retrieve the password.
- Once retrieved, it will generate and display the QR code in a graphical window.

### Authentication

- The script uses the `pkexec` command to retrieve the Wi-Fi password, which will trigger a GUI-based authentication prompt asking for the user’s password.
- This ensures that only users with proper privileges can retrieve the password.

## Example Output

A QR code will be displayed in a Tkinter window

You can scan the QR code with any device to automatically connect to the Wi-Fi network.

## Troubleshooting

- **No Wi-Fi connection detected**: Ensure that your system is connected to a Wi-Fi network.
- **Error retrieving password**: Make sure you have the necessary privileges to retrieve the Wi-Fi password. The script uses `pkexec` to request the password securely.

### Possible Improvements
- Support for additional platforms (e.g., macOS, Windows).
- Option to save the generated QR code as an image file.
- Enhanced error handling for more specific issues (e.g., incorrect SSID format, network unavailable).

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for detail