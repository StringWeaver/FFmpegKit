# this file is for fixing "the platform does not use shallow bundles" error on macCatalyst platform
# usage: 1. cd FFmpegKit/Sources 2. python3 fix_shallow_bundles.py

#!/usr/bin/env python3
import os
import shutil

def is_shallow_framework(fw_path):
    return os.path.isfile(os.path.join(fw_path, "Info.plist")) \
        and not os.path.isdir(os.path.join(fw_path, "Versions"))

def fix_framework(fw_path):
    fw_name = os.path.splitext(os.path.basename(fw_path))[0]
    versions = os.path.join(fw_path, "Versions")
    version_a = os.path.join(versions, "A")
    current = os.path.join(versions, "Current")

    print(f"[fix ] {fw_path}")

    os.makedirs(os.path.join(version_a, "Resources"), exist_ok=True)

    # binary
    bin_path = os.path.join(fw_path, fw_name)
    if os.path.exists(bin_path):
        shutil.move(bin_path, os.path.join(version_a, fw_name))

    # Info.plist
    plist = os.path.join(fw_path, "Info.plist")
    if os.path.exists(plist):
        shutil.move(plist, os.path.join(version_a, "Resources", "Info.plist"))

    # Headers / Modules
    for d in ("Headers", "Modules"):
        src = os.path.join(fw_path, d)
        if os.path.isdir(src):
            shutil.move(src, os.path.join(version_a, d))

    # symlinks
    os.makedirs(versions, exist_ok=True)
    if not os.path.exists(current):
        os.symlink("A", current)

    for name, target in {
        fw_name: f"Versions/Current/{fw_name}",
        "Headers": "Versions/Current/Headers",
        "Modules": "Versions/Current/Modules",
        "Resources": "Versions/Current/Resources",
    }.items():
        link = os.path.join(fw_path, name)
        if not os.path.exists(link):
            os.symlink(target, link)

def process_xcframework(xc_path):
    for slice_name in os.listdir(xc_path):
        if "maccatalyst" not in slice_name:
            continue

        slice_dir = os.path.join(xc_path, slice_name)
        if not os.path.isdir(slice_dir):
            continue

        for item in os.listdir(slice_dir):
            if item.endswith(".framework"):
                fw_path = os.path.join(slice_dir, item)
                if is_shallow_framework(fw_path):
                    fix_framework(fw_path)

def main():
    root = os.getcwd()
    for name in os.listdir(root):
        if name.endswith(".xcframework"):
            process_xcframework(os.path.join(root, name))

if __name__ == "__main__":
    main()
