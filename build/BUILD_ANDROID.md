# Building Solitaire for Android with Buildozer

This guide provides the step-by-step process to package your Kivy Solitaire game into an Android APK.

## Prerequisites
- **Operating System:** Linux (Ubuntu 20.04+ recommended) or Windows with **WSL2** (Ubuntu). Buildozer does not run natively on Windows.
- **Python:** 3.8+
- **Hardware:** Android phone (e.g., Samsung A series) with **USB Debugging** enabled.

---

## Step 1: Install System Dependencies
On your Linux/WSL2 terminal, install the required packages:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade buildozer
```

---

## Step 2: Initialize Buildozer
In your project root directory, run:
```bash
buildozer init
```
This creates a `buildozer.spec` file.

---

## Step 3: Configure `buildozer.spec`
Open `buildozer.spec` and update these specific lines to match your project:

```ini
[app]
# (str) Title of your application
title = Solitaire

# (str) Package name
package.name = solitaire

# (str) Package domain
package.domain = org.solitaire.game

# (str) Icon filename (Updated to your new icon path)
icon.filename = %(source.dir)s/assets/icon.png

# (list) Application requirements
# Note: Add any other libraries if you add them later
requirements = python3, kivy

# (list) Supported orientations
orientation = portrait

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (list) Permissions (Required for Save/Load and Logging)
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Android API to use (33 is a good default for modern phones)
android.api = 33
```

---

## Step 4: Build and Deploy

### 1. Connect your Phone
- Plug your Samsung phone into your computer via USB.
- Go to **Settings > About Phone > Software Information**.
- Tap **Build Number** 7 times to enable **Developer Options**.
- Go to **Settings > Developer Options** and enable **USB Debugging**.

### 2. Run the Build
Run the following command to build the APK, deploy it to your phone, and start the app automatically:

```bash
buildozer android debug deploy run
```

*Note: The first build will take 15–30 minutes as it downloads the Android SDK and NDK. Subsequent builds will be much faster.*

---

## Troubleshooting
- **Logs:** If the app crashes on the phone, view the live logs using:
  ```bash
  buildozer android logcat
  ```
- **Clean Build:** If you face strange errors, try cleaning the build:
  ```bash
  buildozer android clean
  ```
- **Save Location:** Remember that on Android, your save games and logs are stored in the app's private data folder (e.g., `/data/user/0/org.solitaire.game/files/`).
