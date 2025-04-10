import os
import subprocess
import re


# Define constants for regular expressions
REGEX_AUDIO_STREAM = (
    r"Stream #\d+:\d+: Audio: (\w+)"  # Codec (e.g., pcm_f32le, flac)
    r"(?: \([^)]+\))?"               # Optional additional info in parentheses
    r", (\d+ Hz)"                    # Sampling rate (e.g., 192000 Hz)
    r", (stereo|mono|5\.1)"          # Channels (e.g., stereo)
    r"(?:, (\w+))?"                  # Optional bit depth or format (e.g., flt, s32)
    r"(?:, (\d+ kb/s))?"             # Optional bitrate (e.g., 12288 kb/s)
)

REGEX_FILE_INFO = (
    r"Duration: (\d+:\d+:\d+\.\d+), start: [\d.]+, bitrate: (\d+ kb/s)"
)

def get_ffmpeg_audio_stream_info(filename):
    try:
        # Run the `ffmpeg` command to get file information
        command = ["ffmpeg", "-i", filename]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()  # Capture stderr output for metadata

        # Parse file info for duration and bitrate
        file_info_match = re.search(REGEX_FILE_INFO, stderr)
        duration = file_info_match.group(1) if file_info_match else "Unknown"
        overall_bitrate = file_info_match.group(2) if file_info_match else "Unknown"

        # Search for the audio stream information using the constant regular expression
        match = re.search(REGEX_AUDIO_STREAM, stderr)
        if match:
            codec = match.group(1)  # Extract codec (e.g., pcm_f32le)
            sampling_rate = match.group(2)  # Extract sampling rate (e.g., 192000 Hz)
            channels = match.group(3)  # Extract channels (e.g., stereo)
            bit_depth = match.group(4)  # Extract bit depth (e.g., flt)
            bitrate = match.group(5)  # Extract bitrate (e.g., 12288 kb/s)

            # Return the parsed information
            return {
                "Duration": duration,
                "Bitrate": bitrate,
                "Codec": codec,
                "Sampling Rate": sampling_rate,
                "Channels": channels,
                "Bit Depth": bit_depth,
            }
        else:
            print("Audio stream information not found.")
            return None

    except Exception as e:
        print(f"Error while getting ffmpeg audio stream info: {e}")
        return None

def get_file_properties(file_path):
    try:
        # Gather file properties
        file_properties = get_ffmpeg_audio_stream_info(file_path)
        file_properties.update({
            "File Name": os.path.basename(file_path),
            "File Size": f"{os.path.getsize(file_path)} bytes",
            "Last Modified": f"{os.path.getmtime(file_path):.0f}"
        })
        return file_properties
    except Exception as e:
        print(f"Error in get_file_properties: {e}")
        return None

def trim_audio(input_values, active_page):
    try:
        # Example external program call
        file_path = input_values.get("Select File")
        start_time = input_values.get("Start Time")
        duration = input_values.get("Duration")
        print(f"Trimming audio: {file_path}, Start: {start_time}, Duration: {duration}")
    except Exception as e:
        print(f"Error in trim_audio: {e}")

def loop_video(input_values, active_page):
    try:
        # Example external program call
        file_path = input_values.get("Select File")
        duration = input_values.get("Duration")
        print(f"Looping video: {file_path}, Duration: {duration}")
    except Exception as e:
        print(f"Error in loop_video: {e}")

def combine_audio_video(input_values, active_page):
    try:
        # Example external program call
        video_file = input_values.get("Select Video File")
        audio_file = input_values.get("Select Audio File")
        audio_codec = input_values.get("Audio Codec")
        sampling_rate = input_values.get("Sampling Rate")
        bit_rate = input_values.get("Bit Rate")
        print(f"Combining video and audio: Video: {video_file}, Audio: {audio_file}, Codec: {audio_codec}, Sample Rate: {sampling_rate}, Bit Rate: {bit_rate}")
    except Exception as e:
        print(f"Error in combine_audio_video: {e}")
