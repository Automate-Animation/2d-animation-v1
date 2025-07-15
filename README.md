# 2D Animation V1

## Description

2D Animation V1 is a Python-based automated animation tool that generates 2D animated videos from text scripts and corresponding audio files. It leverages AI for text analysis to extract animation cues and synchronizes character lip movements with the provided audio. The system composites character assets (heads, eyes, mouths, bodies) onto backgrounds to create individual animation frames, which are then compiled into a video.

## Features

*   **Automated Animation:** Generates 2D animations from script and audio inputs.
*   **AI-Powered Text Analysis:** Uses Google Generative AI to interpret text for animation cues such as:
    *   Head and eye movements
    *   Character emotions and body actions
    *   Dialogue attribution
    *   Camera instructions (zoom, screen mode).
*   **Audio Synchronization:** Transcribes audio and aligns it with the text script for timing.
*   **Lip Sync:** Generates phoneme data to synchronize character mouth movements with dialogue.
*   **Character Asset Management:** Dynamically loads and composites character image assets (PNGs) based on script cues.
*   **Frame-by-Frame Generation:** Creates individual animation frames by layering character parts and backgrounds.
*   **Video Compilation:** Compiles generated frames into a video file (AVI format).
*   **Extensible Character System:** Supports multiple characters and customizable assets (moods, body parts, etc.) through a structured image directory and metadata.

## Getting Started

### Prerequisites

*   Python 3.x
*   Docker (for the Gentle transcription service)
*   Pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd 2d-animation-v1
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up and run the Gentle transcription service:**
    The Gentle service is used for audio transcription and alignment. It runs in a Docker container.
    ```bash
    cd Docker
    docker-compose up -d
    ```
    This will start the Gentle service, typically available at `http://localhost:49153`.

### Project Structure

*   `core/`: Contains the main logic for the animation generation.
    *   `main.py`: Orchestrates the entire animation generation pipeline.
    *   `brain_requests/`: Handles interactions with AI services (transcription, text analysis).
    *   `image_manager/`: Manages character image assets.
        *   `CharacterManager.py`: Loads, composites, and manages character parts.
    *   `images/`: Stores character assets and metadata.
        *   `characters/`: Contains subdirectories for each character and their respective image parts (body, eyes, head, mouth).
        *   `metadata/metadata.json`: Defines properties and positions for character assets.
    *   `utils/`: Utility scripts for various tasks (phoneme generation, asset updates).
*   `Docker/`: Contains Docker configuration for services like Gentle.
    *   `docker-compose.yml`: Defines the Gentle service.
*   `example/story/`: Contains example audio (.mp3, .m4a) and text (.txt) files.
*   `Tasks/`: Contains text files describing development tasks.
*   `video_frames/`: (Generated directory) Stores the individual PNG frames created during animation.
*   `videos/`: (Generated directory) Stores the final output video files.
*   `requirements.txt`: Lists Python dependencies.
*   `LICENSE`: Project license file.
*   `README.md`: This file.

## Usage

1.  **Prepare your inputs:**
    *   Create a text script file (e.g., `my_story.txt`).
    *   Create a corresponding audio file (e.g., `my_story.mp3`). Ensure the audio matches the script content for proper alignment.

2.  **Run the main script:**
    ```bash
    python core/main.py --audio_path <path_to_audio_file> --transcript_path <path_to_transcript_file> --google_api_key <your_google_api_key> --video_name <output_video_name>
    ```

    ### Arguments

    - `--audio_path`: Path to the audio file.
    - `--transcript_path`: Path to the transcript file.
    - `--google_api_key`: Your Google API key.
    - `--video_name`: (Optional) Name of the output video file (default: "output").

## Character Customization

To add or modify characters and their assets:

1.  **Create Character Directory:**
    *   Add a new character folder under `core/images/characters/character_X/` (e.g., `core/images/characters/character_2/`).
2.  **Add Asset Subdirectories:**
    *   Inside your new character's folder, create subdirectories for different asset types: `body`, `eyes`, `head`, `mouth`, `background`.
3.  **Populate Assets:**
    *   Place your PNG image assets into the appropriate subdirectories.
    *   For assets with variations (e.g., different emotions for eyes, different head directions), create further subdirectories or follow the naming conventions observed in existing character assets. For example, `eyes` can have subfolders like `happy`, `sad`, and these can have `*_blink` subfolders for blinking animations.
4.  **Update Metadata:**
    *   Edit `core/images/metadata/metadata.json`.
    *   Add a new entry for your character and define the properties for each asset:
        *   `position`: `[x, y]` coordinates for placing the asset.
        *   `size`: `[width, height]` dimensions for the asset.
        *   `zoom_point`: `[x,y]` coordinates for the center of a zoom operation.
    *   Refer to the existing metadata structure for guidance.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.
(Further details can be added here, e.g., coding style, testing procedures.)

## License

This project is licensed under the terms of the LICENSE file.
