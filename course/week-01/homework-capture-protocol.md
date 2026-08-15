# Homework — design your own capture protocol

Before session 2.

Week 2 opens by running a detector on **your** photographs. Whatever is wrong with your
protocol will be visible in the numbers within twenty minutes — which is the point.

## Collect

- At least **3 cats** you have real access to.
- Per cat: **5 head angles × 2 lighting conditions**.
- Per cat: **10 macro shots of the nose**, focused on the philtrum ridge pattern.
- **Two sessions on different days**, so the model cannot learn the day.

## Log

One row per photograph, in a CSV you design. Start from
[`capture_log.template.csv`](capture_log.template.csv):

```csv
cat_name,session_date,shot_index,shot_type,angle_deg,distance_cm,light_source,device,subjective_quality_1to5,notes
```

- `shot_type` is one of `face` or `nose_macro`.
- `subjective_quality_1to5` is *your* judgement, recorded before you see any model output.
  Week 2 compares your rating against the measured Laplacian variance, and the disagreements
  are the interesting part.

Save your working copy as `data/capture_log.csv`. **`data/` is gitignored on purpose** —
house rule: raw pet imagery is never committed to the repository (threat model row 4:
biometrics cannot be reissued after a breach). Bring the folder and the CSV; keep the images
local.

## Do not clean the data

The bad shots are the point. They are what the quality gate in
[REQ-001](../../specs/00-system-spec.md) has to catch, and a cleaned dataset silently
deletes the evidence that the gate is needed at all.

Bring the folder and the CSV exactly as captured.
