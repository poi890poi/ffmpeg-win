from pydantic import BaseModel
from typing import List, Optional


AUDIO_CODECS = {
    "FLAC": "flac",
    "AAC": "aac",
}

SAMPLING_RATES = {
    "48 kHz": "48000",
    "96 kHz": "96000",
    "128 kHz": "128000",
}

BIT_RATES = {
    "128k": "128k",
    "256k": "256k",
    "384k": "384k",
}

class Component(BaseModel):
    type: str  # Type of the component (e.g., "file_selection", "property_viewer", etc.)
    label: str  # Label for the component
    default: Optional[str] = None  # Default value for the component
    options: Optional[List[str]] = None  # Options for dropdown lists (if applicable)

class Tab(BaseModel):
    name: str  # Name of the tab
    callback: str
    rows: List[List[Component]]  # Rows of components in the tab

class Layout(BaseModel):
    tabs: List[Tab]  # List of all tabs

layout = Layout(
    tabs=[
        Tab(
            name="File Inspection",
            callback="None",
            rows=[
                [Component(type="file_selection", label="Select File")],
                [Component(type="property_viewer", label="File Properties")]
            ]
        ),
        Tab(
            name="Trim Audio",
            callback="trim_audio",
            rows=[
                [Component(type="file_selection", label="Select File")],
                [Component(type="text_input", label="Output File", default="")],
                [Component(type="time_input", label="Start Time", default="00:00:00")],
                [Component(type="time_input", label="Duration", default="11:59:59")],
                [Component(type="button", label="Start")],
                [Component(type="progress_bar", label="Trimming Progress")]
            ]
        ),
        Tab(
            name="Loop Video",
            callback="loop_video",
            rows=[
                [Component(type="file_selection", label="Select File")],
                [Component(type="text_input", label="Output File", default="")],
                [Component(type="time_input", label="Duration", default="00:02:00")],
                [Component(type="button", label="Start")],
                [Component(type="progress_bar", label="Looping Progress")],
            ]
        ),
        Tab(
            name="Combine A&V",
            callback="combine_audio_video",
            rows=[
                [Component(type="file_selection", label="Select Video File")],
                [Component(type="file_selection", label="Select Audio File")],
                [Component(type="text_input", label="Output File", default="")],
                [Component(type="options", label="Audio Codec",
                           options=AUDIO_CODECS.keys(), default="AAC")],
                [Component(type="options", label="Sampling Rate", 
                           options=SAMPLING_RATES.keys(), default="96 kHz")],
                [Component(type="options", label="Bit Rate", 
                           options=BIT_RATES.keys(), default="384k")],
                [Component(type="button", label="Start")],
                [Component(type="progress_bar", label="Combining Progress")]
            ]
        )
    ]
)
