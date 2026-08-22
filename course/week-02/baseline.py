"""Block 0 — point an off-the-shelf detector at your own photographs.

Run a pretrained COCO detector over every image in `data/capture/` (Week 1's homework
folder), keep only the "cat" class, and report what an off-the-shelf model — trained on
nothing about your specific cats — already gets right and wrong on your own capture
protocol.

This is course material (`CLAUDE.md`: `course/` is not part of the system, nothing imports
from it, and it does not affect the gate). It intentionally depends on `torchvision`, which
is not a pinned project dependency (ADR-0004 only pins bare `torch` for export) — install it
yourself before running this:

    pip install torchvision

Usage:
    python course/week-02/baseline.py [data/capture/]

Writes `evals/out/baseline.csv`: one row per image — filename, number of cat boxes found,
largest cat box area as a fraction of the image, and mean confidence across cat boxes.
Then prints three totals: images with zero cat boxes, images with more than one, and images
with exactly one box covering at least 5% of the frame.

What this detector is and is not: it finds *cats*, generically. It does not find cat
*faces*, it knows nothing about your specific cats, and it has never seen a nose at macro
distance. That gap is the rest of Week 2's work — but the gap has to be measured before it
can be argued about.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
CAT_CATEGORY_NAME = "cat"
MIN_LARGE_BOX_FRACTION = 0.05


def _find_cat_category_index(categories: list[str]) -> int:
    return categories.index(CAT_CATEGORY_NAME)


def run(data_dir: Path, out_path: Path) -> None:
    import torch
    from torchvision.io import read_image
    from torchvision.models.detection import (
        FasterRCNN_MobileNet_V3_Large_320_FPN_Weights,
        fasterrcnn_mobilenet_v3_large_320_fpn,
    )

    images = sorted(p for p in data_dir.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)
    if not images:
        print(f"baseline: no images found under {data_dir}", file=sys.stderr)
        return

    weights = FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.DEFAULT
    model = fasterrcnn_mobilenet_v3_large_320_fpn(weights=weights, box_score_thresh=0.3)
    model.eval()
    cat_index = _find_cat_category_index(weights.meta["categories"])
    preprocess = weights.transforms()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    zero_box_count = 0
    multi_box_count = 0
    single_good_count = 0

    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["filename", "num_cat_boxes", "largest_box_area_frac", "mean_confidence"])

        for image_path in images:
            image = read_image(str(image_path))
            _channels, height, width = image.shape
            frame_area = float(height * width)

            with torch.no_grad():
                prediction = model([preprocess(image)])[0]

            cat_mask = prediction["labels"] == cat_index
            boxes = prediction["boxes"][cat_mask]
            scores = prediction["scores"][cat_mask]

            num_boxes = int(boxes.shape[0])
            if num_boxes == 0:
                largest_fraction = 0.0
                mean_confidence = 0.0
                zero_box_count += 1
            else:
                widths = boxes[:, 2] - boxes[:, 0]
                heights = boxes[:, 3] - boxes[:, 1]
                areas = widths * heights
                largest_fraction = float(areas.max().item()) / frame_area
                mean_confidence = float(scores.mean().item())
                if num_boxes > 1:
                    multi_box_count += 1
                elif largest_fraction >= MIN_LARGE_BOX_FRACTION:
                    single_good_count += 1

            writer.writerow([image_path.name, num_boxes, f"{largest_fraction:.4f}", f"{mean_confidence:.4f}"])

    print(f"baseline: wrote {out_path} ({len(images)} images)")
    print(f"images with zero cat boxes:                              {zero_box_count}")
    print(f"images with more than one cat box:                       {multi_box_count}")
    print(f"images with exactly one box covering >= 5% of the frame: {single_good_count}")


if __name__ == "__main__":
    data_dir_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/capture")
    out_path_arg = Path("evals/out/baseline.csv")
    run(data_dir_arg, out_path_arg)
