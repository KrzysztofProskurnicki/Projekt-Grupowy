# Refactoring Documentation - Project Restructuring

## Overview
This document details the restructuring of the `Project` directory to improve code organization, maintainability, and separation of concerns. The flat file structure has been replaced with a modular directory layout.

## Resolved Issues
*   **Closes #6:** Rozdział plików na odpowiednie foldery

## Changes

### 1. Directory Structure
The following directories were created to categorize project files:

*   **`src/`**: Contains all source code logic and Python scripts.
*   **`config/`**: Stores configuration files.
*   **`data/`**: Stores application data (e.g., local storage databases).
*   **`assets/`**: Stores static assets such as images and design references.

### 2. File Relocation
| Original Location | New Location | Description |
| :--- | :--- | :--- |
| `Project/*.py` | `Project/src/` | All Python application modules (main, sidebar, views, etc.). |
| `Project/config.json` | `Project/config/config.json` | Application configuration settings. |
| `Project/passwords.json` | `Project/data/passwords.json` | Local password data storage. |
| `Project/design_option_*.json` | `Project/assets/` | Design concept files. |
| `Project/*.png` | `Project/assets/` | Image assets. |

### 3. Code Modifications
*   **Path Updates**: Import paths and file access paths in `main.py`, `login_dialog.py`, and `detail_view.py` were updated to use relative paths pointing to the new `../config/` and `../data/` locations.
