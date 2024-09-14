# Twitch Stream Recorder

A simple Python script to record Twitch streams using asyncio and streamlink libraries. This tool allows you to record the best available quality livestream of a Twitch streamer without the need for API tokens or complex setups.

## Features

- Record Twitch streams in real-time
- Save streams as .ts files (more reliable in case of failures)
- Option to convert .ts files to .mp4
- Easy setup and usage

## Setup

1. Install [python](https://www.python.org/downloads/) and ensure you add to PATH when installing.

2. Download or clone this repository.

3. Install the required Python libraries:

``pip install asyncio streamlink configparser``

4. Install `ffmpeg` and ensure it's in your system PATH:
- [Windows guide](https://www.wikihow.com/Install-FFmpeg-on-Windows)
- [Other OS guide](https://www.hostinger.com/tutorials/how-to-install-ffmpeg)

## Usage

Run the script:

```python
python3 twitch-recorder.py [username]
```

You can provide the username as an argument or run without it to be prompted for input.

On first run, you'll be asked to set an output folder for recordings. This will be saved in `config.ini` for future use.

The script will continuously check for the stream and start recording when it's live. To stop, use Ctrl+C (Cmd+C on macOS).

Note: If you choose not to convert the .ts files, you can watch them with media players like [MPV](https://mpv.io/) or [VLC](https://www.videolan.org/).

## Configuration

Edit `config.ini` to change settings:
- `convert_to_mp4`: Set to "True" or "False"
- `use_ffmpeg_convert`: Set to "True" or "False" (only applies if `convert_to_mp4` is True)
- `check_interval`: Time in seconds between checks for live streams

## Disclaimer
Please note that recording and distributing Twitch streams without the permission of the content creator may violate Twitch's terms of service and could lead to legal consequences. Use this code responsibly and with respect for the creators whose content you are recording.

