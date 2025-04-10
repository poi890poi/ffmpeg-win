from pydantic import BaseModel
from typing import List, Optional

class Component(BaseModel):
    type: str  # Type of the component (e.g., "file_selection", "property_viewer", etc.)
    label: str  # Label for the component
    options: Optional[List[str]] = None  # Options for dropdown lists (if applicable)

class Tab(BaseModel):
    name: str  # Name of the tab
    rows: List[List[Component]]  # Rows of components in the tab

class Layout(BaseModel):
    tabs: List[Tab]  # List of all tabs

layout = Layout(
    tabs=[
        Tab(
            name="File Inspection",
            rows=[
                [Component(type="file_selection", label="Select File")],
                [Component(type="property_viewer", label="File Properties")]
            ]
        ),
        Tab(
            name="Trim Audio",
            rows=[
                [Component(type="file_selection", label="Select File")],
                [Component(type="time_input", label="Start Time")],
                [Component(type="time_input", label="Duration")],
                [Component(type="progress_bar", label="Trimming Progress")]
            ]
        ),
        Tab(
            name="Loop Video",
            rows=[
                [Component(type="file_selection", label="Select File")],
                [Component(type="time_input", label="Duration")],
                [Component(type="progress_bar", label="Looping Progress")]
            ]
        ),
        Tab(
            name="Combine A&V",
            rows=[
                [Component(type="file_selection", label="Select Video File")],
                [Component(type="file_selection", label="Select Audio File")],
                [Component(type="options", label="Audio Codec", options=["AAC", "FLAC"])],
                [Component(type="options", label="Sampling Rate", options=["48 kHz", "96 kHz", "128 kHz"])],
                [Component(type="options", label="Bit Rate", options=["128k", "256k", "384k"])],
                [Component(type="progress_bar", label="Combining Progress")]
            ]
        )
    ]
)
