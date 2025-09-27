Perfect — going with Gradio is the fastest way to get this live. Since you want a Product Requirements Document (PRD) for the project, here's a structured version tailored to your case:

📄 PRD: CSV-to-Ref.jpg Template Batch Image Generator (Gradio App)
1. Objective

Build a simple web-based tool using Python + Gradio that allows users to:

Upload a CSV file containing fields exactly: Name, Link, Rrp, Price.

Upload a template image (e.g., Ref.jpg) that contains labeled areas for: Name, RRP, Now, and a QR area.

Automatically generate a batch of images by replacing:
- Name → the Name text area on the template
- Rrp → the RRP text area on the template
- Price → the Now text area on the template
- QR code → generated from Link and placed into the QR area

Provide a ZIP download of all generated images.

This will reduce repetitive manual design work when creating marketing images, product labels, or posters.

2. Users

Primary users: Small businesses, marketers, or internal teams who need to mass-produce images with structured data.

Secondary users: Developers/testers using it for internal workflows.

3. User Stories

As a user, I want to upload a CSV file with columns Name, Link, Rrp, Price so that I can provide structured product data.

As a user, I want to upload a template image (like Ref.jpg) so all generated images follow the same design.

As a user, I want the app to automatically overlay Name, RRP, and Now (Price) text and place a QR code from Link at fixed positions matching the template.

As a user, I want to download all generated images in a ZIP file so I can use them immediately.

As a user, I want to generate a batch of images from a single CSV in one click.

4. Scope
In-Scope

CSV file upload with headers exactly: Name, Link, Rrp, Price.

Template image upload (PNG or JPG), expected to be visually similar to Ref.jpg (areas labeled Name, RRP, Now, and a QR area).

Generate QR codes per row from the Link field.

Overlay text fields at fixed coordinates tuned to the Ref.jpg layout:
- Name → Name label area
- Rrp → RRP label area
- Price → Now label area

Place the generated QR code into the QR area.

Export final images as PNG (default).

Zip and provide download link for the entire batch.

Optional (nice-to-have in v1 if trivial): Preview of the first generated image.

Out-of-Scope (v1)

Interactive UI to move/resize elements.

Multiple templates per batch.

Advanced styling (font families, colors, dynamic text wrapping beyond basics).

Cloud storage integrations.

5. Functional Requirements

File Upload

Accepts .csv with headers: Name, Link, Rrp, Price (case-sensitive for v1).
Accepts .png or .jpg template image.

CSV Processing

Parse CSV with pandas.
Validate required columns: Name, Link, Rrp, Price.
Handle blank or missing values gracefully (skip row with an error message recorded).

Per-Row Generation

Generate QR code from Link (error on invalid URL; skip row with message).
Overlay text:
- Name: replace Name area text
- Rrp: replace RRP area text
- Price: replace Now area text (no currency added automatically; use provided value as-is)
Place QR into the template's QR region.

Positions and Styling

Use fixed pixel coordinates and font sizes tuned for Ref.jpg. These will be constants in code (to be measured from Ref.jpg during implementation).
Basic text wrapping or truncation if string is too long (truncate with ellipsis for v1).

Output

Save each image as PNG using a deterministic filename, e.g., {row_index}_{slugified_name}.png.
After processing all rows, compress outputs into a .zip and present a download link.

UI (Gradio)

File uploader for CSV.
File uploader for template image.
"Generate Images" button.
Outputs: generation log (success/errors) and ZIP download.

6. Non-Functional Requirements

Performance: Handle CSV files up to ~500 rows on a typical laptop.

Usability: Minimal UI; drag-and-drop.

Portability: Run locally with python app.py or deploy to Spaces.

Reliability: Gracefully handle malformed CSVs and invalid URLs; skip failing rows and continue.

7. Tech Stack

Python 3.10+

Libraries:

pandas (CSV handling)

Pillow (image manipulation)

qrcode (QR generation)

gradio (UI)

zipfile (batch export)

8. Success Metrics

User can generate and download a ZIP from a single CSV (100–500 rows) in under 2 minutes.

Output images place Name, Rrp, Price, and QR code at correct locations aligned with the Ref.jpg layout.

At least 95% of rows process successfully for well-formed CSVs.

9. Acceptance Criteria

Given a CSV with headers Name, Link, Rrp, Price and a Ref.jpg-like template:
- When I click Generate Images, the app produces one PNG per row and a ZIP.
- The Name text appears where "Name" is on the template.
- The Rrp text appears where "RRP" is on the template.
- The Price appears where "Now" is on the template.
- A scannable QR code generated from Link is placed in the QR area.
- The app shows a short log indicating processed/failed rows.

10. CSV Format Example

```csv
Name,Link,Rrp,Price
Widget Pro,https://example.com/widget-pro,39.99,29.99
Smart Device,https://example.com/smart-device,249.99,199.99
Premium Tool,https://example.com/premium-tool,199.50,149.50
```

11. Error Handling

Missing columns → show a clear error and stop.

Invalid URL → skip the row; log the issue.

Empty Name/Price/Rrp → skip the row; log the issue.

Image write failure → skip row; log the issue.

ZIP creation failure → show error and provide individual files if possible.

12. Implementation Notes

Coordinate Measurements: Measure pixel coordinates and text anchor points from Ref.jpg and store as constants (e.g., NAME_POS, RRP_POS, NOW_POS, QR_BOX).

Fonts: Use Pillow ImageFont.truetype with a bundled or system-safe font; fallback to default if unavailable. Font sizes tuned for Ref.jpg.

Text Fit: Use basic truncation with ellipsis if text overflows the allowed region. No auto-resize in v1.

Image Mode: Work in RGBA; save as PNG.

File Naming: Slugify Name for readability in filenames.

13. Future Enhancements (v2+)

Interactive canvas to adjust positions.

Per-field font configs (family, size, weight, color).

Multiple templates per run.

Currency formatting helpers for Rrp/Price.

Cloud storage integrations.

API endpoint for automation.

✅ With this PRD, you can now move straight into implementation for the Ref.jpg-driven layout and single-CSV batch generation.