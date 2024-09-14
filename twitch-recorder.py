import asyncio
import streamlink
import os
import configparser
import shutil
from datetime import datetime

config_file_path = "config.ini"
config = configparser.ConfigParser()

# Check if the config file exists, if not create one with default values
if not os.path.exists(config_file_path):
    config["DEFAULT"] = {
        "output_folder": "",
        "convert_to_mp4": "True",
        "use_ffmpeg_convert": "True",
    }
    with open(config_file_path, "w") as configfile:
        config.write(configfile)

# Load the config file
config.read(config_file_path)

twitch_username = input("Streamer Username to record: ")
output_folder = config["DEFAULT"]["output_folder"]

# If the output_folder variable is not set, ask the user for input
if not output_folder:
    output_folder = input("Enter the output folder path for recordings: ")
    config["DEFAULT"]["output_folder"] = output_folder

# Save the variables to the config file
with open(config_file_path, "w") as configfile:
    config.write(configfile)

convert_to_mp4 = config["DEFAULT"].getboolean("convert_to_mp4")
use_ffmpeg_convert = config["DEFAULT"].getboolean("use_ffmpeg_convert")

os.system(f"title {twitch_username} @ {output_folder}")


async def get_best_stream_url(username):
    twitch_stream_url = f"https://www.twitch.tv/{username}"
    streams = streamlink.streams(twitch_stream_url)
    if "best" in streams:
        best_stream = streams["best"]
        m3u8_url = best_stream.url
        print(f"Will record from best livestream .m3u8 URL: {m3u8_url}")
        return m3u8_url
    else:
        print("No available streams found.")


async def record_stream(username):
    m3u8_url = await get_best_stream_url(username)
    if m3u8_url:
        timestamp = datetime.now().strftime("%d_%m_%y-%H_%M")
        ts_filename = f"{twitch_username}-{timestamp}.ts"
        ts_filepath = os.path.join(output_folder, ts_filename)

        # Record stream to .ts file
        ffmpeg_record_cmd = ["ffmpeg", "-i", m3u8_url, "-c", "copy", ts_filepath]
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
                process = await asyncio.create_subprocess_exec(*ffmpeg_convert_cmd)
                await process.communicate()
                os.remove(ts_filepath)  # Remove the original .ts file
            else:
                # Simply rename .ts to .mp4
                shutil.move(ts_filepath, mp4_filepath)

            print(f"Converted and saved as: {mp4_filepath}")
        else:
            print(f"Saved as: {ts_filepath}")


if __name__ == "__main__":
    asyncio.run(record_stream(twitch_username))
