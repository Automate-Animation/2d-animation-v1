# synctoon 🎬

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Automate-Animation/synctoon.svg)](https://github.com/Automate-Animation/synctoon/stargazers)

**Synctoon** is a powerful, AI-driven 2D animation tool that automatically creates engaging animated videos from text scripts and audio files. Transform your stories into professional-looking animations with synchronized lip movements, dynamic character expressions, and intelligent scene composition.

## 🌟 See It In Action

Check out animations created with synctoon on our YouTube channel: [**Daily YG Stories**](https://www.youtube.com/@DailyYGStories)

## ✨ Features

- 🤖 **AI-Powered Animation**: Leverages Google Generative AI for intelligent text analysis and animation cue extraction
- 🎭 **Automatic Lip Sync**: Generates phoneme data to synchronize character mouth movements with dialogue
- 👁️ **Dynamic Character Expressions**: Supports head movements, eye expressions, and body language
- 🎨 **Multi-Character Support**: Handle multiple characters with distinct visual assets and personalities
- 🎵 **Audio Synchronization**: Perfectly aligns animation with audio timing using transcription services
- 🖼️ **Extensible Asset System**: Easy-to-use character and background asset management
- 📹 **Frame-by-Frame Generation**: Creates smooth animations by compositing individual frames
- 🔄 **Automated Workflow**: Complete pipeline from script to final video

## 🚀 Quick Start

### Prerequisites

- Python 3.x
- Docker (for audio transcription service)
- Google API Key (for AI text analysis)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Automate-Animation/synctoon.git
   cd synctoon
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the transcription service:**
   ```bash
   cd Docker
   docker-compose up -d
   ```

4. **Configure your inputs:**
   - Export your Google API key (and optionally override default example assets):
     ```bash
     export GOOGLE_API_KEY="your-google-api-key"
     export SYNCTOON_TRANSCRIPT_PATH="/path/to/your_story.txt"   # optional
     export SYNCTOON_AUDIO_PATH="/path/to/your_story.mp3"        # optional
     export SYNCTOON_SERVICE_URL="http://localhost:49153/transcriptions?async=false"  # optional
     ```
   - Alternatively, provide the values via CLI flags when you run the pipeline (see below).

### Create Your First Animation

1. **Prepare your story files** (or use the provided examples):
   - Text script: `example/story/your_story.txt`
   - Audio file: `example/story/your_story.mp3`

2. **Generate the animation metadata (and optionally override paths/API keys per run):**
   ```bash
   cd core
   python core.py --transcript ../example/story/your_story.txt \
                  --audio ../example/story/your_story.mp3 \
                  --api-key "$GOOGLE_API_KEY"
   ```
   Use `python core.py --help` to see all available configuration flags and environment variables.

   To run the full pipeline (core processing, frame generation, and video assembly) in one step, use:
   ```bash
   python create_animation.py -n "my_first_animation"
   ```

3. **Combine video with audio** (final step):
   ```bash
   ffmpeg -i videos/my_first_animation.mp4 -i ../example/story/your_story.mp3 -c:v copy -c:a aac final_animation.mp4
   ```

## 🎯 Vision & Mission

**Our goal is to democratize animation creation.** We believe everyone should have access to powerful animation tools regardless of their technical background or budget. Synctoon is completely free and open-source, empowering storytellers, educators, content creators, and hobbyists to bring their ideas to life.

## 🗂️ Project Structure

```
synctoon/
├── core/                          # Main animation engine
│   ├── brain_requests/           # AI services integration
│   ├── image_manager/            # Character asset management
│   ├── images/                   # Character and background assets
│   │   ├── characters/          # Character image components
│   │   └── metadata/            # Asset positioning data
│   ├── utils/                    # Utility functions
│   ├── create_animation.py       # Main animation script
│   ├── frame_generator.py        # Frame composition logic
│   └── frame_to_video.py         # Video compilation
├── example/story/                # Sample scripts and audio
├── Docker/                       # Transcription service setup
└── requirements.txt              # Python dependencies
```

## 🎨 Character Customization

Synctoon supports extensive character customization:

1. **Add new characters** in `core/images/characters/character_X/`
2. **Organize assets** into folders: `body/`, `eyes/`, `head/`, `mouth/`, `background/`
3. **Configure positioning** in `metadata/metadata.json`
4. **Support for emotions** and expressions through asset variations

## 🔮 Future Roadmap

We're actively working on exciting new features:

- 🖼️ **Dynamic Background Elements**: Add contextual images, doodles, and visual elements that enhance storytelling
- 🌄 **Real-time Background Generation**: AI-powered background creation that adapts to story context
- 🎭 **Enhanced Character Library**: Expanded collection of characters, emotions, and animations
- 🎨 **Visual Effects System**: Particle effects, transitions, and cinematic elements
- 📱 **Web Interface**: Browser-based animation creation tool
- 🌍 **Multi-language Support**: International language and voice support
- 🤝 **Community Asset Marketplace**: Share and discover character assets and backgrounds

## 👨‍💻 Connect With The Creator

**Muhammad Kamal** - Creator & Lead Developer

- 🌐 **Portfolio**: [oyekamal.github.io/oykamal](https://oyekamal.github.io/oykamal/)
- 📸 **Instagram**: [@oykamal](https://instagram.com/oykamal)
- 💼 **LinkedIn**: [muhammad-kamal-025600121](https://linkedin.com/in/muhammad-kamal-025600121)
- 🐦 **Twitter**: [@oykamal](https://twitter.com/oykamal)
- 📺 **YouTube**: [@oykamal](https://youtube.com/@oykamal)

📍 **Location**: Pakistan (UTC -12:00)

## 🤝 Contributing

We welcome contributions from the community! Whether you're a developer, designer, or storyteller, there are many ways to help:

- 🐛 **Report bugs** and suggest features
- 💻 **Submit code** improvements and new features
- 🎨 **Create and share** character assets
- 📖 **Improve documentation** and tutorials
- 🌟 **Star the repository** to show your support

### For Developers

If you want to contribute code or understand the technical implementation details, please check our comprehensive **[Developer Guide](DEVELOPER.md)** which includes:

- 🏗️ **Architecture Overview**: Complete system design and data flow
- 🔧 **Code Structure**: Detailed breakdown of all components
- 🧪 **Testing Guidelines**: How to write and run tests
- 🚀 **Development Setup**: Local development environment setup
- 📊 **API Documentation**: Integration details and examples
- 🐛 **Troubleshooting**: Common issues and solutions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Generative AI for text analysis capabilities
- Gentle for audio transcription and alignment
- The open-source community for inspiration and support

---

**Made with ❤️ for the global storytelling community**

