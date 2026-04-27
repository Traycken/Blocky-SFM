Make with AI
# SFM Blockly Editor

A visual, block-based editor for creating and managing **Super Factory Manager (SFM)** scripts for Minecraft. This tool allows players to build complex automation logic using a interface, with automatic code generation and import/export capabilities.

## ✨ Key Features

- **Block-Based Logic:** Build scripts using intuitive blocks for Triggers, Inputs, Outputs, Conditions, and more.
- **Global Tag System:** Define inventory labels once in the sidebar and reuse them across your entire script with a single click.
- **Visual Side Picker:** A grid-based selector for choosing block faces (Top, Bottom, North, South, East, West) without typing.
- **Robust Heuristic Import:** Import raw SFM code directly. The editor intelligently reconstructs the block structure even for complex, multi-line scripts.
- **Real-Time Preview:** Watch your SFM code generate instantly as you build, with full syntax highlighting.
- **Local Workspace:** Multiple scripts can be saved and managed directly in your browser's local storage.
- **Themes:** Choose between Night, Day, and Twilight themes to suit your preference.

## 🚀 Getting Started

The SFM Blockly Editor is a **single-file web application**. No installation is required.

Visit: https://traycken.github.io/Blocky-SFM/sfm-blockly-editor.html

or

1.  Download `sfm-blockly-editor.html`.
2.  Open the file in any modern web browser (Chrome, Firefox, Edge, etc.).
3.  Start building!

## 🛠 Usage Tips

-   **Nesting:** ADD **Input**, **Output**, **If**, and **Forget** blocks directly into the "Statements" zones of **Triggers** or **IF branches**.
-   **Importing:** Use the "Import .sfm" button to load your existing scripts. Even if they weren't created with this editor, the heuristic parser will do its best to rebuild them.
-   **Exporting:** Click "Export .sfm" to save your script to a file that can be loaded directly into a Minecraft SFM Manager.
-   **Nesting Clarity:** Look at the colored backgrounds and left-border accents to understand the depth and flow of your logic.

## 📄 License

This project is open-source.
