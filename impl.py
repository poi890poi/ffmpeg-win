import os

def get_file_properties(file_path):
    try:
        # Gather file properties
        file_properties = {
            "File Name": os.path.basename(file_path),
            "File Size": f"{os.path.getsize(file_path)} bytes",
            "Last Modified": f"{os.path.getmtime(file_path):.0f}"
        }
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
