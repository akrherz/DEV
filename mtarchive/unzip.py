"""Unzip archived files."""

import os
import subprocess


def main():
    """Go Main Go."""
    # Start from current directory
    start_dir = os.getcwd()
    print(f"Starting recursive scan from: {start_dir}\n")

    zip_count = 0
    for rootdir, _dirs, filenames in os.walk(start_dir):
        # Show we're traversing
        depth = rootdir.replace(start_dir, "").count(os.sep)
        indent = "  " * depth
        print(f"{indent}Scanning: {rootdir}")

        for filename in filenames:
            if not filename.endswith(".zip"):
                continue

            # Legacy shortcut zip files were exactly 70 bytes in size
            # If so, just delete those if found
            filepath = os.path.join(rootdir, filename)
            if os.path.getsize(filepath) == 70:
                os.remove(filepath)
                print(f"{indent}  Removed legacy shortcut zip: {filename}")
                continue

            zip_count += 1
            print(f"{indent}  Found zip: {filename}")

            # Extract in the same directory as the zip file
            try:
                subprocess.run(
                    ["unzip", "-n", "-q", filename],
                    cwd=rootdir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                # Only delete if extraction succeeded
                zip_filepath = os.path.join(rootdir, filename)
                os.remove(zip_filepath)
                print(f"{indent}  ✓ Extracted and removed {filename}")
            except subprocess.CalledProcessError as e:
                print(f"{indent}  ✗ Extraction failed: {e.stderr}")
            except OSError as e:
                print(f"{indent}  ✗ Could not delete {filename}: {e}")

    print(f"\nTotal zip files processed: {zip_count}")


if __name__ == "__main__":
    main()
