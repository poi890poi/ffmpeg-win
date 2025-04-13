import math
import os
import subprocess
import re
import threading
import queue
import time

from util import *


TASK_COMPLETION_SIGNAL = "===TASK_COMPLETION_SIGNAL==="

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

REGEX_PROGRESS = r"time=(\d+:\d+:\d+\.\d+) bitrate=(\d+\.\d+kbits/s) speed=(\d+\.\d+x)"

def get_ffmpeg_audio_stream_info(filename):
    try:
        # Run the `ffmpeg` command to get file information
        command = ["ffmpeg", "-i", filename]
        process = subprocess.Popen(
            command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()  # Capture stderr output for metadata

        # Parse file info for duration and bitrate
        file_info_match = re.search(REGEX_FILE_INFO, stderr)
        duration = file_info_match.group(1) if file_info_match else "Unknown"
        overall_bitrate = file_info_match.group(2) if file_info_match else "Unknown"
        stream_info = {
            "Duration": duration,
            "Overall Bitrate": overall_bitrate,
        }

        # Search for the audio stream information using the constant regular expression
        match = re.search(REGEX_AUDIO_STREAM, stderr)
        if match:
            codec = match.group(1)  # Extract codec (e.g., pcm_f32le)
            sampling_rate = match.group(2)  # Extract sampling rate (e.g., 192000 Hz)
            channels = match.group(3)  # Extract channels (e.g., stereo)
            bit_depth = match.group(4)  # Extract bit depth (e.g., flt)
            bitrate = match.group(5)  # Extract bitrate (e.g., 12288 kb/s)

            # Return the parsed information
            stream_info.update({
                "Bitrate": bitrate,
                "Codec": codec,
                "Sampling Rate": sampling_rate,
                "Channels": channels,
                "Bit Depth": bit_depth,
            })
        else:
            print("Audio stream information not found.")
        return stream_info

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

import subprocess

def run_ffmpeg_loop(input_file, output_file,
                    loop_times, truncate_duration, output_queue):
    print(run_ffmpeg_loop, input_file, output_file, loop_times, truncate_duration)
    def target():
      try:
          # Build the FFmpeg command
          command = [
              "ffmpeg",
              "-y",
              "-stream_loop", str(loop_times),
              "-i", input_file,
              "-t", str(truncate_duration),
              output_file
          ]

          print(command)
          
          # Run the command
          process = subprocess.Popen(
              command,
              stdout=subprocess.PIPE, 
              stderr=subprocess.PIPE, 
              text=True
          )
          
          # Capture output in real-time
          for line in process.stderr:
              # print(line.strip())  # Print to console (or parse to update UI)
              output_queue.put(line.strip())
              # yield line.strip()   # Yield output for progress bar parsing

          process.wait()
          output_queue.put(TASK_COMPLETION_SIGNAL)

      except Exception as e:
          print(f"Error while running FFmpeg: {e}")

    threading.Thread(target=target).start()

def trim_audio(input_values, active_page):
    try:
        # Example external program call
        file_path = input_values.get("Select File")
        start_time = input_values.get("Start Time")
        duration = input_values.get("Duration")
        print(f"Trimming audio: {file_path}, Start: {start_time}, Duration: {duration}")
    except Exception as e:
        print(f"Error in trim_audio: {e}")

def parse_progress(ffmpeg_output):
    # Match progress info like "frame=123 time=00:00:02.50 ..."
    match = re.search(REGEX_PROGRESS, ffmpeg_output)
    if match:
        current_time = match.group(1)
        bitrate = match.group(2)
        speed = match.group(3)
        print(f"Current processing time: {current_time}")
        return(duration_to_seconds(current_time))

# Timer thread to update the progress bar
def update_progress_bar_with_timer(active_page, output_queue, total_duration):
    def update(time_start):
        while not output_queue.empty():
            now = time.time()
            elapsed = now - time_start
            line = output_queue.get()
            current_time = parse_progress(line)
            # Update the progress bar here (e.g., calculate percentage)
            if current_time is not None:
                percent = current_time / total_duration
                ete = elapsed / percent
                remaining = ete - elapsed
                eta = now + remaining
                print(line, f'elapsed: {elapsed}')
                print('step', current_time, total_duration, percent)
                active_page.find_progress_bar()['value'] = int(percent * 100)
                active_page.set_entry("progress_text", (
                    f'elapsed: {convert_seconds_to_hhmmss(elapsed)}, '
                    f'remaining: {convert_seconds_to_hhmmss(remaining)}, '
                    f'eta: {convert_epoch_to_hhmmss(eta)}'))
            else:
              if TASK_COMPLETION_SIGNAL in line:
                print(TASK_COMPLETION_SIGNAL)
                return True

        # Schedule the next update
        threading.Timer(0.1, update, args=(time_start,)).start()

    update(time.time())

def loop_video(input_values, active_page):
    try:
        # Example external program call
        file_path = input_values.get("Select File")
        duration = input_values.get("Duration")
        dir, filename = os.path.split(file_path)
        _, ext = os.path.splitext(filename)
        output_file = input_values.get("Output File")
        output_file = os.path.join(dir, f'{output_file}{ext}')

        # Check if output_file exist and ask for confirmation on overwriting.
        if os.path.isfile(output_file):
            user_response = active_page.ask_user_for_overwrite(output_file)
            if user_response:  # If user confirmed overwrite
                ...
            else:  # If user declined overwrite
                print("User canceled the operation.")
                return False

        file_properties = get_ffmpeg_audio_stream_info(file_path)
        print(file_properties['Duration'])
        duration_src = duration_to_seconds(file_properties['Duration'])
        duration_target = duration_to_seconds(duration)
        loop_times = math.ceil(duration_target / duration_src)

        # Queue to handle output between threads
        output_queue = queue.Queue()

        run_ffmpeg_loop(file_path, output_file,
                        loop_times, duration, output_queue)
        update_progress_bar_with_timer(active_page,
                                       output_queue, duration_target)
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
