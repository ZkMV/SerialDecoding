# Serial Port Interface (v01)

A lightweight PyQt5 application for working with COM ports. It allows the user to:

* **Refresh** the list of available COM ports.
* **Select** a port from a dropdown menu.
* **Select Baudrate** from a predefined list (4800, 9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600).
* **Connect** to the chosen port ("Connect" button).
* **Display** incoming data in a terminal window (light gray background framed by a thin black border).
* **Send** arbitrary text to the serial port (input field + "Send" button), with:

  * **Enter key** support for sending.
  * **Keep command** checkbox: when checked, the input field retains the last command after sending; otherwise, it clears automatically.
* **Disconnect** from the port ("Disconnect" button).

## Features

* **Dynamic button states**: "Connect" is enabled only after selecting a port; "Send" activates after the first successful send/receive; "Disconnect" becomes active once connected.
* **Visual styling**: The terminal window is light gray to match the application background and is outlined with a thin black line.
* **Connection health check**: Every 5 seconds, if no data is received, the "Send" button automatically disables.
* **Error handling**: If the COM port cannot open (busy or missing), a popup displays the error and a message appears in the terminal window with the error details.
* Easily extendable **SEQUENCE:** packet handling logic (illustrated with comments in the code).

## Requirements

* **Python 3.6** or newer
* **PyQt5**
* **pyserial**

## Installation

1. Clone or download this repository:

   ```bash
   git clone https://github.com/username/DecodingSignalSequence.git
   cd DecodingSignalSequence
   ```
2. It’s recommended to create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux/Mac
   .\.venv\Scripts\activate   # Windows PowerShell
   ```
3. Install dependencies:

   ```bash
   pip install PyQt5 pyserial
   ```

## Running the Application

Ensure your virtual environment is active and you’re inside the project directory. Then run:

```bash
python main.py
```

* Click **Refresh COMs** to update the list of available ports.
* Select a COM port from the dropdown.
* Choose the appropriate **Baudrate**.
* Click **Connect** to establish a connection. If successful, the terminal will display "Connected to COMx.".
* Incoming data will appear in the terminal window in real time.
* To send text, type into the input field and press **Enter** or click **Send**.

  * If **Keep command** is unchecked, the input clears after sending.
* To end the session, click **Disconnect**.

## File Structure

* `main.py` — Main Python script containing the GUI and serial logic.
* `README.md` — This file with instructions and project information.
* `.gitignore` — Specifies files and directories ignored by Git.

## Release Notes for v01

* Implemented PyQt5 GUI for COM port and baudrate selection, connect/disconnect.
* Added terminal window with light gray background and black border.
* Implemented serial read thread to display incoming data.
* Added text sending with Enter key support.
* Added **Keep command** check
