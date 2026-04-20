# Build Instructions

## App Spec

Prepare a `buildozer.spec` file for build settings

## Build Notes

- If building on Windows, need to use `WSL2`
  - Need to change setting in BIOS: find `Intel Virtualization Technology (VT-x)` or `AMD-V/SVM Mode` and set it to `Enabled`
  - Change WSL1 to WSL2: `wsl --set-version <Distro> 2`
- Build command: `buildozer android debug`
- You can use `Android Studio simulator` to simulate a virtual phone, and deploy apk on it to test
- Also can connect to a real phone (by USB cable or WiFi debugging) and move apk on it and install the app
- Use `ADB` package in `PowerShell` to check the logging: `adb logcat -s python`

## WSL Operation Notes

- List WSLs: `wsl -l -v`
- If forgot sudo password, use `wsl -u root` to enter WSL on `PowerShell`, then use `passwd username` to change password
