"""
Section Crop Script - Hybrid boundary detection

Two detection methods combined:
  1. Uniform band detection: finds separator gaps between sections
  2. Color shift detection: finds sharp transitions (e.g. white header -> gradient hero)

Then merges both, applies min_section_height, and crops.
"""
import sys
import os
from PIL import Image
import numpy as np


def find_section_boundaries(img_path, min_section_height=120, uniform_band_height=8,
                            color_variance_threshold=5, color_shift_threshold=30):
    """
    Hybrid boundary detection: uniform bands + color shifts.

    Parameters:
        img_path: image file path
        min_section_height: minimum section height (smaller sections get merged)
        uniform_band_height: minimum height of a uniform color band to count as boundary
        color_variance_threshold: max std-dev within a row to be considered uniform
        color_shift_threshold: min average color diff between adjacent rows for sharp transition
    """
    img = Image.open(img_path)
    arr = np.array(img)[:, :, :3].astype(float)
    height, width = arr.shape[:2]

    # --- Method 1: Uniform band detection ---
    row_std = arr.std(axis=1).mean(axis=1)
    uniform_rows = row_std < color_variance_threshold

    band_boundaries = []
    start = None
    for i in range(height):
        if uniform_rows[i]:
            if start is None:
                start = i
        else:
            if start is not None:
                band_h = i - start
                if band_h >= uniform_band_height:
                    band_boundaries.append((start + i) // 2)
                start = None
    if start is not None and height - start >= uniform_band_height:
        band_boundaries.append((start + height) // 2)

    # --- Method 2: Color shift detection ---
    row_means = arr.mean(axis=1)  # (height, 3)
    shift_boundaries = []
    for i in range(1, height):
        diff = np.abs(row_means[i] - row_means[i - 1]).mean()
        if diff > color_shift_threshold:
            shift_boundaries.append(i)

    # --- Merge boundaries ---
    all_candidates = sorted(set(band_boundaries + shift_boundaries))

    # Filter: enforce min_section_height
    boundaries = [0]
    for candidate in all_candidates:
        if candidate - boundaries[-1] >= min_section_height:
            boundaries.append(candidate)

    if height - boundaries[-1] >= min_section_height:
        boundaries.append(height)
    elif boundaries[-1] != height:
        boundaries[-1] = height

    return boundaries, img


def crop_sections(img_path, output_dir, min_section_height=120):
    """Crop image into sections and save each as PNG."""
    boundaries, img = find_section_boundaries(img_path, min_section_height)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Image: {img.width}x{img.height}px")
    print(f"Sections: {len(boundaries) - 1}")
    print(f"Boundaries: {boundaries}")
    print("=" * 60)

    sections = []
    for i in range(len(boundaries) - 1):
        y_start = boundaries[i]
        y_end = boundaries[i + 1]
        h = y_end - y_start

        cropped = img.crop((0, y_start, img.width, y_end))

        if i == 0:
            name = f"{i + 1:02d}_header"
        elif i == len(boundaries) - 2:
            name = f"{i + 1:02d}_footer"
        else:
            name = f"{i + 1:02d}_section_{i}"

        path = os.path.join(output_dir, f"{name}.png")
        cropped.save(path)

        avg = np.array(cropped)[:, :, :3].mean(axis=(0, 1)).astype(int)
        sections.append({'name': name, 'y_start': y_start, 'y_end': y_end, 'height': h})
        print(f"  {name}.png  {img.width}x{h}px  (y:{y_start}-{y_end})  avg=RGB{tuple(avg)}")

    print(f"\nSaved to: {output_dir}")
    return sections


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python crop_sections.py <image_path> [output_dir] [min_section_height]")
        sys.exit(1)

    img_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(img_path), 'sections')
    min_h = int(sys.argv[3]) if len(sys.argv) > 3 else 80

    crop_sections(img_path, output_dir, min_h)
