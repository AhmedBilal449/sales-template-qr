# 🖼️ CSV-to-Template Image Generator

A Python Gradio application that generates batch images from CSV data using template images with QR codes. Perfect for creating marketing materials, product labels, or promotional images at scale.

## ✨ Features

- **📄 CSV Upload**: Process product data from CSV files
- **🖼️ Template Images**: Use custom template images for consistent branding
- **📱 QR Code Generation**: Automatically generate QR codes from URLs
- **⚡ Batch Processing**: Process hundreds of products in one go
- **📦 ZIP Download**: Get all generated images in a convenient ZIP file
- **🔧 Flexible Column Mapping**: Works with various CSV column names
- **📊 Real-time Logging**: See processing status and error messages
- **🎨 Modern UI**: Clean, intuitive Gradio interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd sales-template-qr
```

2. **Set up virtual environment:**
```bash
python -m venv env

# On Windows:
env\Scripts\activate

# On macOS/Linux:
source env/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the Application

**Option 1: Direct Python**
```bash
python app.py
```

**Option 2: Using batch file (Windows)**
```bash
.\run_app.bat
```

Then open your browser and navigate to the provided URL (usually http://localhost:7860)

## 📋 CSV Format

Your CSV file should contain these columns (flexible naming supported):

| Column Type | Accepted Names |
|-------------|----------------|
| Product Name | `Name`, `Product`, `Title` |
| URL | `URL`, `Link`, `Website` |
| Current Price | `Price`, `Current_Price`, `Now` |
| RRP | `RRP`, `Retail_Price`, `Original_Price`, `Was` |

### Example CSV:
```csv
Name,URL,Price,RRP
Nival Blanco Matt 30x60,https://tilemania.com/nival-blanco,15.00,35
Carrara Marble Gloss 60x60,https://tilemania.com/carrara-marble,25.50,45
Rustic Oak Wood Effect 20x120,https://tilemania.com/rustic-oak,18.75,32
```

## 🖼️ Template Image Guidelines

- **Format**: PNG or JPG
- **Layout**: Ensure space for text overlays and QR code
- **Positioning**: The app uses fixed coordinates for:
  - Product name (top-left area)
  - RRP price (middle-left)
  - Current price (below RRP, in red)
  - QR code (right side, 150x150px)

## 📤 Output

- **Format**: PNG images
- **Naming**: `001_product-name.png`, `002_next-product.png`, etc.
- **Packaging**: All images bundled in `generated_images.zip`
- **Logging**: Detailed processing log with success/error status

## 🎯 How It Works

1. **Upload Files**: CSV data + template image
2. **Column Detection**: Automatically maps CSV columns
3. **Validation**: Checks for required data
4. **Image Generation**: For each CSV row:
   - Overlays product name, prices
   - Generates QR code from URL
   - Saves as PNG file
5. **ZIP Creation**: Packages all images
6. **Download**: Provides ZIP file link

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing columns error | Check CSV has Name, URL, Price, RRP columns |
| QR code generation fails | Verify URLs are valid and properly formatted |
| Image overlay issues | Ensure template image is not corrupted |
| No images generated | Check processing log for specific error messages |
| Module not found | Activate virtual environment before running |

## 📁 Project Structure

```
sales-template-qr/
├── app.py              # Main Gradio application
├── run_app.bat         # Windows batch file to run app
├── requirements.txt    # Python dependencies
├── sample_data.csv     # Example CSV data
├── Ref.jpg            # Reference template image
├── PLAN.md            # Detailed project requirements
└── README.md          # This file
```

## 🔧 Customization

To adjust text positioning or styling, modify these constants in `app.py`:

```python
self.NAME_POS = (50, 50)    # Product name position
self.RRP_POS = (50, 200)    # RRP price position  
self.NOW_POS = (50, 250)    # Current price position
self.QR_POS = (300, 50)     # QR code position
self.QR_SIZE = (150, 150)   # QR code size
```

## 📄 License

MIT License - feel free to use and modify for your projects!