# 🖼️ CSV to Template Image Generator

A simple web-based tool built with Python and Gradio that automatically generates branded images by overlaying CSV data onto template images. Perfect for creating marketing materials, product labels, or promotional images at scale.

## ✨ Features

- **CSV Data Processing**: Upload CSV files with product/company information
- **Template-Based Generation**: Use your own template images as backgrounds
- **Automatic QR Code Generation**: Generate QR codes from URLs in your CSV
- **Batch Processing**: Handle hundreds of records at once
- **ZIP Download**: Get all generated images in a convenient ZIP file
- **Web Interface**: Easy-to-use drag-and-drop interface

## 🚀 Quick Start

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd sales-template-qr
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and go to `http://localhost:7860`

### Usage

1. **Prepare your CSV file** with the following required columns:
   - `company_name`: Name of the company
   - `product_name`: Name of the product
   - `price`: Product price ($ will be added automatically)
   - `qr_link` (optional): URL for QR code generation

2. **Upload your template image** (PNG or JPG format)

3. **Click "Generate Images"** to process your data

4. **Download the ZIP file** containing all generated images

## 📊 CSV Format Example

```csv
company_name,product_name,price,qr_link
Acme Corp,Widget Pro,29.99,https://example.com/widget-pro
Tech Solutions,Smart Device,199.99,https://example.com/smart-device
Best Products,Premium Tool,149.50,https://example.com/premium-tool
```

## 🎨 Template Layout

The application overlays information at fixed positions:
- **Company Name**: Top-left (large font)
- **Product Name**: Below company name (medium font)
- **Price**: Below product name (with $ prefix)
- **QR Code**: Bottom-right corner (100x100px)

## 🛠️ Technical Details

- **Python 3.10+** required
- **Dependencies**: Gradio, Pandas, Pillow, qrcode
- **Output Format**: PNG images
- **Performance**: Handles up to 500+ records efficiently
- **Deployment**: Can be deployed to Hugging Face Spaces or run locally

## 📝 Requirements

- CSV file with required columns
- Template image (PNG/JPG)
- Python environment with dependencies installed

## 🔧 Customization

To modify text positions or styling, edit the `positions` and `fonts` dictionaries in the `overlay_text_and_qr` method in `app.py`.

## 📄 License

This project is open source and available under the MIT License.
