# CSV Template Generator - Executable Distribution

## 🎯 Overview
This is a standalone executable version of the CSV Template Generator application. It can run on any Windows computer without requiring Python or any dependencies to be installed.

## 📦 What's Included
- `CSV_Template_Generator.exe` - The main executable file
- All necessary libraries and dependencies bundled together
- No installation required - just run the executable!

## 🚀 How to Use

### Running the Application
1. **Double-click** `CSV_Template_Generator.exe` to start the application
2. The application will automatically open in your default web browser
3. If the browser doesn't open automatically, go to: `http://127.0.0.1:7860`

### Using the Features
The application has two main tabs:

#### 🎯 Generate Images Tab
1. **Upload CSV File**: Upload a CSV with columns for Name, URL, Price, and RRP
2. **Upload Template Image**: Upload your template image (like Ref.jpg)
3. **Click Generate**: Process your data and create batch images
4. **Download**: Get a ZIP file with all generated images

#### 📄 Create A4 Layouts Tab
1. **Upload ZIP File**: Upload the ZIP file from the Generate Images tab
2. **Click Create A4 Layouts**: Arrange images on print-ready A4 pages
3. **Download**: Get A4 layout pages ready for printing

## 📋 CSV Format Requirements
Your CSV file should have these columns (flexible naming):
- **Name/Product/Title**: Product name
- **URL/Link/Website**: Website URL for QR code
- **Price/Current_Price/Now**: Current price
- **RRP/Retail_Price/Original_Price/Was**: Original retail price

Example CSV:
```csv
Name,URL,Price,RRP
Nival Blanco Matt 30x60,https://tilemania.com/nival-blanco,15.00,35
Carrara Marble Gloss 60x60,https://tilemania.com/carrara-marble,25.50,45
```

## 🖼️ Template Image
- Upload a template image (JPG, PNG, JPEG)
- The application will overlay text and QR codes on this template
- Default positioning is optimized for the provided reference template

## ✨ Features
- **Batch Processing**: Generate multiple images from CSV data
- **QR Code Generation**: Automatic QR codes from URLs
- **Flexible Column Detection**: Handles various CSV column names
- **Print-Ready A4 Layouts**: 12 images per page at 300 DPI
- **Error Handling**: Detailed logs and error messages
- **ZIP Downloads**: Convenient packaging of generated files

## 🔧 Troubleshooting

### Application Won't Start
- Make sure you have the entire `CSV_Template_Generator` folder
- Don't move the `.exe` file out of its folder
- Check Windows Defender/antivirus isn't blocking the file

### Browser Doesn't Open
- Manually go to `http://127.0.0.1:7860` in your browser
- Make sure no other application is using port 7860

### File Upload Issues
- Ensure CSV files are properly formatted
- Check that image files are in supported formats (JPG, PNG, JPEG)
- File paths should not contain special characters

### Performance
- Large CSV files (100+ rows) may take several minutes to process
- Template images with high resolution will increase processing time
- Close other applications if memory usage is high

## 🖨️ Printing Guidelines
- A4 layouts are created at 300 DPI for professional printing
- Each A4 page contains 12 images in a 3x4 grid
- 0.5-inch margins on all sides for proper printing
- Use high-quality paper for best results

## 📁 Distribution
To share this application with others:
1. Copy the entire `CSV_Template_Generator` folder
2. Send the complete folder (not just the .exe file)
3. Recipients can run the .exe file directly
4. No installation or setup required on target computers

## 🆘 Support
If you encounter issues:
1. Check the processing log in the application for error details
2. Ensure your CSV format matches the requirements
3. Try with a smaller dataset first to test functionality
4. Make sure your template image is accessible and not corrupted

## 🔄 Updates
To update the application:
1. Replace the entire folder with the new version
2. Your data and settings are not stored in the application folder
3. Always backup your CSV files and templates before updating

---

**Note**: This executable was built with PyInstaller and contains all necessary dependencies. The application runs locally on your computer and does not send data to external servers.
