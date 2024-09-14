import asyncio
import streamlink
import os
import configparser
import shutil
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

config_file_path = "config.ini"
config = configparser.ConfigParser()

# Check if the config file exists, if not create one with default values
if not os.path.exists(config_file_path):
    config["DEFAULT"] = {
        "output_folder": "",
        "convert_to_mp4": "True",
        "use_ffmpeg_convert": "True",
        "check_interval": "60",
    }
    with open(config_file_path, "w") as configfile:
        config.write(configfile)

# Load the config file
config.read(config_file_path)


def get_valid_path(path):
    # Expand user directory if path starts with ~
    expanded_path = os.path.expanduser(path)
    # Normalize the path (converts / to \ on Windows if needed)
    normalized_path = os.path.normpath(expanded_path)
    # Check if the path exists, if not, create it
    if not os.path.exists(normalized_path):
        try:
            os.makedirs(normalized_path)
        except OSError as e:
            logging.error(f"Error creating directory: {e}")
            return None
    return normalized_path


# Get username from argument or prompt
if len(sys.argv) > 1:
    twitch_username = sys.argv[1]
else:
    twitch_username = input("Streamer Username to record: ")

output_folder = config["DEFAULT"]["output_folder"]

# If the output_folder variable is not set, ask the user for input
if not output_folder:
    output_folder = input("Enter the output folder path for recordings: ")
    output_folder = get_valid_path(output_folder)
    if output_folder:
        config["DEFAULT"]["output_folder"] = output_folder
    else:
        logging.error("Invalid output folder. Exiting.")
        sys.exit(1)

# Save the variables to the config file
with open(config_file_path, "w") as configfile:
    config.write(configfile)

convert_to_mp4 = config["DEFAULT"].getboolean("convert_to_mp4")
use_ffmpeg_convert = config["DEFAULT"].getboolean("use_ffmpeg_convert")
check_interval = config["DEFAULT"].getint("check_interval")


async def get_best_stream_url(username):
    twitch_stream_url = f"https://www.twitch.tv/{username}"
    streams = streamlink.streams(twitch_stream_url)
    if "best" in streams:
        best_stream = streams["best"]
        m3u8_url = best_stream.url
        logging.info(
            f"Stream is live! Will record from best livestream .m3u8 URL: {m3u8_url}"
        )
        return m3u8_url
    else:
        return None
        # print("No available streams found.")


async def record_stream(username):
    try:
        while True:
            m3u8_url = await get_best_stream_url(username)
            if m3u8_url:
                timestamp = datetime.now().strftime("%d_%m_%y-%H_%M")
                ts_filename = f"{twitch_username}-{timestamp}.ts"
                ts_filepath = os.path.join(output_folder, ts_filename)

                # Record stream to .ts file
                ffmpeg_record_cmd = [
                    "ffmpeg",
                    "-i",
                    m3u8_url,
                    "-c",
                    "copy",
                    ts_filepath,
                ]
                process = await asyncio.create_subprocess_exec(*ffmpeg_record_cmd)
                await process.communicate()

                if convert_to_mp4:
                    mp4_filename = f"{twitch_username}-{timestamp}.mp4"
                    mp4_filepath = os.path.join(output_folder, mp4_filename)

                    if use_ffmpeg_convert:
                        # Convert .ts to .mp4 using ffmpeg
                        ffmpeg_convert_cmd = [
                            "ffmpeg",
                            "-i",
                            ts_filepath,
                            "-c",
                            "copy",
                            mp4_filepath,
                        ]
                        process = await asyncio.create_subprocess_exec(
                            *ffmpeg_convert_cmd
                        )
                        await process.communicate()
                        os.remove(ts_filepath)  # Remove the original .ts file
                    else:
                        # Simply rename .ts to .mp4
                        shutil.move(ts_filepath, mp4_filepath)

                    logging.info(f"Converted and saved as: {mp4_filepath}")
                else:
                    logging.info(f"Saved as: {ts_filepath}")
            else:
                logging.info(f"No available streams found for {username}.")
                logging.info(
                    f"No stream available. Checking for {username} stream again in {check_interval} seconds..."
                )
                await asyncio.sleep(check_interval)
    except asyncio.CancelledError:
        logging.info("Recording stopped gracefully.")


async def main():
    try:
        await record_stream(twitch_username)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Stopping the recording...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program stopped by user.")
