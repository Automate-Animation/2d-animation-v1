#!/usr/bin/env python3
"""
Master script to create animation video in one command.
This script runs the entire pipeline: core.py -> frame_generator.py -> frame_to_video.py
"""

import argparse
import sys
import os
import subprocess
import time
from datetime import datetime


def run_script(script_name, description, extra_args=None):
    """Run a Python script and handle errors."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"Running: {script_name}")
    print(f"{'='*60}")

    try:
        cmd = [sys.executable, script_name] + (extra_args or [])
        # Run the script using Python
        result = subprocess.run(cmd, capture_output=False, text=True, check=True)
        print(f"✅ {description} completed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}:")
        print(f"Exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error running {script_name}: {e}")
        return False


def run_frame_to_video_with_name(video_name=None):
    """Run frame_to_video.py with optional video name."""
    print(f"\n{'='*60}")
    print(f"STEP: Creating final video")
    print(f"Running: frame_to_video.py")
    print(f"{'='*60}")

    try:
        if video_name:
            cmd = [sys.executable, "frame_to_video.py", "-n", video_name]
            print(f"Creating video with name: {video_name}")
        else:
            cmd = [sys.executable, "frame_to_video.py"]
            print(f"Creating video with timestamp name")

        result = subprocess.run(cmd, capture_output=False, text=True, check=True)
        print(f"✅ Video creation completed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running frame_to_video.py:")
        print(f"Exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error running frame_to_video.py: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Create animation video from script and audio"
    )
    parser.add_argument("-n", "--name", help="Name for the output video file", type=str)
    parser.add_argument("--script", required=True, help="Path to the story text file.")
    parser.add_argument(
        "--audio",
        help="Path to an existing audio file. If omitted, audio is synthesized via ElevenLabs.",
    )
    parser.add_argument("--out-dir", help="Output directory (default: ./build/<name>).")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default 24).")
    parser.add_argument(
        "--skip-core", action="store_true", help="Skip core.py (use existing CSV)"
    )
    parser.add_argument(
        "--skip-frames",
        action="store_true",
        help="Skip frame generation (use existing frames)",
    )

    args = parser.parse_args()

    name_for_dir = args.name or os.path.splitext(os.path.basename(args.script))[0]
    out_dir = args.out_dir or os.path.join("build", name_for_dir)

    core_args = ["--script", args.script, "--out-dir", out_dir, "--fps", str(args.fps)]
    if args.audio:
        core_args += ["--audio", args.audio]

    print("🎬 Animation Video Creation Pipeline")
    print("=" * 60)
    print("This script will run the complete animation pipeline:")
    print("1. core.py - Process script and audio, create CSV")
    print("2. frame_generator.py - Generate animation frames")
    print("3. frame_to_video.py - Combine frames into video")
    print("=" * 60)

    start_time = time.time()
    success = True

    # Step 1: Run core.py
    if not args.skip_core:
        success = run_script(
            "core.py", "Processing script and audio (core.py)", extra_args=core_args
        )
        if not success:
            print("\n❌ Pipeline failed at core.py step!")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping core.py (using existing CSV file)")

    # Step 2: Run frame_generator.py
    if not args.skip_frames:
        success = run_script(
            "frame_generator.py", "Generating animation frames (frame_generator.py)"
        )
        if not success:
            print("\n❌ Pipeline failed at frame generation step!")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping frame generation (using existing frames)")

    # Step 3: Run frame_to_video.py
    success = run_frame_to_video_with_name(args.name)
    if not success:
        print("\n❌ Pipeline failed at video creation step!")
        sys.exit(1)

    # Success!
    end_time = time.time()
    duration = end_time - start_time

    print(f"\n🎉 SUCCESS! Animation pipeline completed!")
    print(f"⏱️  Total time: {duration:.2f} seconds ({duration/60:.1f} minutes)")
    print(f"📁 Check the './videos/' folder for your animation")

    if args.name:
        print(f"🎬 Video name: {args.name}.mp4")
    else:
        print(f"🎬 Video name: {datetime.now()}.mp4")


if __name__ == "__main__":
    main()
