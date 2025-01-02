import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import subprocess
import qrcode
from PIL import Image, ImageTk
import keyring
from keyring.backends.SecretService import Keyring

# === Configuration Constants ===
QR_BOX_SIZE = 10  # Size of each box in the QR code
QR_BORDER = 5  # Border size for the QR code
QR_IMAGE_SIZE = 450  # Size of the QR code image in pixels
WINDOW_TITLE = "Wisharify QR Code"  # Title of the GUI window
FONT_FAMILY = "Helvetica"  # Font family for labels
FONT_SIZE = 16  # Font size for the SSID label
KEYRING_SERVICE_NAME = "nmcli-wifi"  # Keyring service identifier
NMCLI_WIFI_FIELDS = "active,ssid"  # Fields to retrieve active Wi-Fi connections
NMCLI_CONNECTION_FIELDS = "active,uuid"  # Fields to retrieve connection UUID
NMCLI_PASSWORD_FIELD = "802-11-wireless-security.psk"  # Field for Wi-Fi password

# === Logging Setup ===
# Default to console logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# === Utility Functions ===

async def run_command(command: str, check: bool = True) -> str:
    """
    Run a shell command asynchronously.

    Args:
        command (str): The shell command to execute.
        check (bool): If True, raises an error for non-zero exit codes.

    Returns:
        str: The command's output as a string.
    """
    logger.debug("Running command: %s", command)
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if check and process.returncode != 0:
        logger.error("Command failed: %s - Error: %s", command, stderr.decode().strip())
        raise subprocess.CalledProcessError(
            process.returncode, command, stdout.decode(), stderr.decode()
        )
    return stdout.decode().strip()

async def get_current_ssid() -> str | None:
    """
    Retrieve the SSID of the currently connected Wi-Fi network.

    Returns:
        str | None: The current Wi-Fi SSID, or None if not connected.
    """
    try:
        output = await run_command(f"nmcli -t -f {NMCLI_WIFI_FIELDS} dev wifi")
        for line in output.splitlines():
            if line.startswith("yes"):
                ssid = line.split(":")[1]
                logger.info("Connected SSID: %s", ssid)
                return ssid
    except subprocess.CalledProcessError as e:
        logger.error("Command failed: %s", e)
    except asyncio.TimeoutError as e:
        logger.error("Command timed out: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
    return None

async def get_wifi_password(ssid: str) -> str | None:
    """
    Retrieve the Wi-Fi password for a given SSID using GUI-based authentication.

    Args:
        ssid (str): The SSID of the Wi-Fi network.

    Returns:
        str | None: The Wi-Fi password, or None if not retrievable.
    """
    try:
        output = await run_command(f"nmcli -t -f {NMCLI_CONNECTION_FIELDS} connection show")
        for line in output.splitlines():
            if line.startswith("yes"):
                uuid = line.split(":")[1]
                break
        else:
            return None

        command = f"pkexec nmcli -s -g {NMCLI_PASSWORD_FIELD} connection show {uuid}"
        password = await run_command(command)
        logger.info("Password retrieved for SSID '%s'", ssid)
        return password.strip()
    except Exception as e:
        logger.error("Failed to retrieve password for SSID '%s': %s", ssid, e)
        return None

def show_qr_code(ssid: str, password: str):
    """
    Generate and display a QR code for the Wi-Fi network in a graphical window.

    Args:
        ssid (str): The SSID of the Wi-Fi network.
        password (str): The Wi-Fi password.
    """
    wifi_config = f"WIFI:T:WPA;S:{ssid};P:{password};;"
    qr = qrcode.QRCode(box_size=QR_BOX_SIZE, border=QR_BORDER)
    qr.add_data(wifi_config)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")

    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry(f"{QR_IMAGE_SIZE+QR_BORDER*12}x{QR_IMAGE_SIZE+QR_BORDER*12}")

    frame = ttk.Frame(root, padding="10")
    frame.pack(fill="both", expand=True)

    label = ttk.Label(frame, text=f"Connect to: {ssid}", font=(FONT_FAMILY, FONT_SIZE))
    label.pack(pady=(10, 5))

    img = img.resize((QR_IMAGE_SIZE, QR_IMAGE_SIZE))
    img_tk = ImageTk.PhotoImage(img)

    qr_label = ttk.Label(frame, image=img_tk)
    qr_label.image = img_tk  # Prevent garbage collection
    qr_label.pack(pady=(5, 10))

    close_button = ttk.Button(frame, text="Exit", command=root.destroy)
    close_button.pack(pady=10)

    # Allow closing via the window close button
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    root.mainloop()

# === Main Execution ===

async def main():
    """
    Main script entry point.
    Retrieves the current Wi-Fi SSID and password, then displays a QR code.
    """
    keyring.set_keyring(Keyring())
    try:
        # Retrieve the current SSID
        ssid = await get_current_ssid()
        if not ssid:
            logger.error("No SSID detected. Are you connected to a Wi-Fi network?")
            messagebox.showerror("Error", "No SSID detected. Connect to a Wi-Fi network.")
            return

        # Retrieve the password from the keyring or fetch it if not cached
        password = keyring.get_password(KEYRING_SERVICE_NAME, ssid)
        if not password:
            password = await get_wifi_password(ssid)
            if password:
                keyring.set_password(KEYRING_SERVICE_NAME, ssid, password)

        if password:
            show_qr_code(ssid, password)
        else:
            logger.error("Password not found for SSID '%s'.", ssid)
            messagebox.showerror("Error", f"Password not found for SSID '{ssid}'.")
    except (subprocess.CalledProcessError, keyring.errors.KeyringError) as e:
        logger.critical("Unexpected error: %s", e)
        messagebox.showerror("Critical Error", f"An unexpected error occurred:\n{e}")

if __name__ == "__main__":
    asyncio.run(main())
