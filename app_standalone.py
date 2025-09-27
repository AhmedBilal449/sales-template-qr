import gradio as gr
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
import zipfile
import os
import tempfile
import shutil
from typing import List, Tuple, Optional
import re
import math
import sys
import webbrowser
from threading import Timer

class ImageGenerator:
    def __init__(self):
        # Default coordinates for Ref.jpg layout (will be refined based on actual image)
        # These coordinates are estimates and should be adjusted based on the actual template
        self.NAME_POS = (15, 100)  # Top left area for product name
        self.RRP_POS = (15, 170)  # RRP price position
        self.NOW_POS = (15, 200)  # Current price position
        self.QR_POS = (190, 165)   # QR code position
        self.QR_SIZE = (160, 160) # QR code size
        
        # Font settings
        self.FONT_SIZE_LARGE = 24  # For product name
        self.FONT_SIZE_MEDIUM = 20 # For prices
        
        # Store font paths for dynamic loading
        self.font_paths = [
            "rosario.ttf",
            "Rosario-Regular.ttf", 
            "Rosario.ttf",
            "C:/Windows/Fonts/Rosario-Regular.ttf",
            "C:/Windows/Fonts/rosario.ttf"
        ]
        
        # Store bold font paths for dynamic loading
        self.bold_font_paths = [
            "rosario-bold.ttf",
            "Rosario-Bold.ttf",
            "C:/Windows/Fonts/Rosario-Bold.ttf",
            "C:/Windows/Fonts/arial-bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf"
        ]
        
        # Cache for loaded fonts to avoid reloading
        self._font_cache = {}
    
    def get_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        """Get font with specified size and weight, using cache for performance"""
        cache_key = f"font_{size}_{'bold' if bold else 'regular'}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # Choose font paths based on whether bold is requested
        font_paths = self.bold_font_paths if bold else self.font_paths
        
        # Try to load font with the specified size and weight
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, size)
                self._font_cache[cache_key] = font
                return font
            except:
                continue
        
        # Fallback fonts
        fallback_fonts = ["arialbd.ttf", "arial-bold.ttf"] if bold else ["arial.ttf"]
        for fallback in fallback_fonts:
            try:
                font = ImageFont.truetype(fallback, size)
                self._font_cache[cache_key] = font
                return font
            except:
                continue
        
        # Final fallback - load default font
        font = ImageFont.load_default()
        self._font_cache[cache_key] = font
        return font
    
    def get_large_font(self, bold: bool = False) -> ImageFont.ImageFont:
        """Get large font using current FONT_SIZE_LARGE setting"""
        return self.get_font(self.FONT_SIZE_LARGE, bold)
    
    def get_medium_font(self, bold: bool = False) -> ImageFont.ImageFont:
        """Get medium font using current FONT_SIZE_MEDIUM setting"""
        return self.get_font(self.FONT_SIZE_MEDIUM, bold)
    
    def clear_font_cache(self):
        """Clear font cache - useful when font sizes are changed"""
        self._font_cache.clear()
    
    def update_font_sizes(self, large_size: int = None, medium_size: int = None):
        """Update font sizes and clear cache"""
        if large_size is not None:
            self.FONT_SIZE_LARGE = large_size
        if medium_size is not None:
            self.FONT_SIZE_MEDIUM = medium_size
        self.clear_font_cache()
    
    def create_qr_code(self, url: str) -> Image.Image:
        """Generate QR code from URL"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        return qr_img.resize(self.QR_SIZE, Image.Resampling.LANCZOS)
    
    def wrap_text(self, text: str, max_chars_per_line: int = 25) -> List[str]:
        """Wrap text into multiple lines if too long"""
        if len(text) <= max_chars_per_line:
            return [text]
        
        # Split text into words
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # If adding this word would exceed the limit, start a new line
            if len(current_line + " " + word) > max_chars_per_line and current_line:
                lines.append(current_line.strip())
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
        
        # Add the last line if it has content
        if current_line:
            lines.append(current_line.strip())
        
        # Limit to 2 lines maximum
        if len(lines) > 2:
            lines = lines[:2]
            # If we had to cut off text, add ellipsis to the second line
            if len(lines[1]) > max_chars_per_line - 3:
                lines[1] = lines[1][:max_chars_per_line-3] + "..."
            else:
                lines[1] = lines[1] + "..."
        
        return lines
    
    def slugify(self, text: str) -> str:
        """Convert text to filename-safe string"""
        text = re.sub(r'[^\w\s-]', '', text).strip()
        text = re.sub(r'[-\s]+', '-', text)
        return text.lower()
    
    def generate_image(self, template_img: Image.Image, name: str, url: str, price: str, rrp: str, row_index: int) -> Tuple[Optional[Image.Image], str]:
        """Generate a single image with overlays"""
        try:
            # Create a copy of the template
            img = template_img.copy()
            draw = ImageDraw.Draw(img)
            
            # Wrap text if needed
            name_lines = self.wrap_text(str(name), 25)
            # Format price and RRP to 2 decimal places with /m² suffix
            try:
                price_formatted = f"{float(price):.2f}/m²"
            except (ValueError, TypeError):
                price_formatted = f"{str(price)}/m²"
            
            try:
                rrp_formatted = f"{float(rrp):.2f}/m²"
            except (ValueError, TypeError):
                rrp_formatted = f"{str(rrp)}/m²"
            
            # Draw text overlays using dynamic font sizing with bold fonts
            # Draw name text (potentially multi-line) - use bold large font
            name_font = self.get_large_font(bold=True)
            for i, line in enumerate(name_lines):
                line_y = self.NAME_POS[1] + (i * (self.FONT_SIZE_LARGE + 2))  # Add small line spacing
                draw.text((self.NAME_POS[0], line_y), line, fill="black", font=name_font)
            # Draw prices with bold fonts
            rrp_font = self.get_medium_font(bold=True)
            rrp_full_text = f"RRP: £{rrp_formatted}"
            draw.text(self.RRP_POS, rrp_full_text, fill="black", font=rrp_font)
            
            # Add strikethrough line to RRP text (centered vertically)
            bbox = draw.textbbox(self.RRP_POS, rrp_full_text, font=rrp_font)
            # Calculate the vertical center of the text more accurately
            text_height = bbox[3] - bbox[1]
            line_y = bbox[1] + text_height // 2  # Use bbox coordinates for precise centering
            line_start_x = self.RRP_POS[0]
            line_end_x = bbox[2]
            draw.line([(line_start_x, line_y), (line_end_x, line_y)], fill="black", width=2)
            
            draw.text(self.NOW_POS, f"Now: £{price_formatted}", fill="red", font=self.get_large_font(bold=True))
            
            # Generate and paste QR code
            qr_img = self.create_qr_code(str(url))
            img.paste(qr_img, self.QR_POS)
            
            return img, f"✅ Row {row_index + 1}: Generated image for '{name}'"
            
        except Exception as e:
            return None, f"❌ Row {row_index + 1}: Error generating image for '{name}': {str(e)}"
    
    def process_csv_and_generate(self, csv_file, template_file) -> Tuple[Optional[str], str]:
        """Main processing function"""
        if csv_file is None or template_file is None:
            return None, "❌ Please upload both CSV file and template image"
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file.name)
            
            # Flexible column mapping - handle different column names
            column_mapping = {}
            columns = [col.lower().strip() for col in df.columns]
            
            # Map columns flexibly
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower in ['name', 'product', 'title']:
                    column_mapping['name'] = col
                elif col_lower in ['url', 'link', 'website']:
                    column_mapping['url'] = col
                elif col_lower in ['price', 'current_price', 'now']:
                    column_mapping['price'] = col
                elif col_lower in ['rrp', 'retail_price', 'original_price', 'was']:
                    column_mapping['rrp'] = col
            
            # Validate required columns
            required_fields = ['name', 'url', 'price', 'rrp']
            missing_fields = [field for field in required_fields if field not in column_mapping]
            
            if missing_fields:
                available_cols = ', '.join(df.columns)
                return None, f"❌ Missing required columns: {', '.join(missing_fields)}. Available columns: {available_cols}"
            
            # Load template image
            template_img = Image.open(template_file.name)
            
            # Create temporary directory for generated images
            temp_dir = tempfile.mkdtemp()
            generated_files = []
            log_messages = []
            
            log_messages.append(f"📊 Processing {len(df)} rows from CSV")
            log_messages.append(f"📋 Template image size: {template_img.size}")
            
            # Process each row
            for index, row in df.iterrows():
                name = row[column_mapping['name']]
                url = row[column_mapping['url']]
                price = row[column_mapping['price']]
                rrp = row[column_mapping['rrp']]
                
                # Skip rows with missing essential data
                if pd.isna(name) or pd.isna(url) or pd.isna(price) or pd.isna(rrp):
                    log_messages.append(f"⚠️ Row {index + 1}: Skipping due to missing data")
                    continue
                
                # Generate image
                img, message = self.generate_image(template_img, name, url, price, rrp, index)
                log_messages.append(message)
                
                if img is not None:
                    # Save image
                    filename = f"{index + 1:03d}_{self.slugify(str(name))}.png"
                    filepath = os.path.join(temp_dir, filename)
                    img.save(filepath, "PNG")
                    generated_files.append(filepath)
            
            if not generated_files:
                return None, "❌ No images were generated successfully"
            
            # Create ZIP file
            zip_path = os.path.join(temp_dir, "generated_images.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in generated_files:
                    zipf.write(file_path, os.path.basename(file_path))
            
            log_messages.append(f"✅ Successfully generated {len(generated_files)} images")
            log_messages.append(f"📦 ZIP file created with all images")
            
            return zip_path, "\n".join(log_messages)
            
        except Exception as e:
            return None, f"❌ Error processing files: {str(e)}"
    
    def create_a4_layout(self, zip_file) -> Tuple[Optional[str], str]:
        """Create A4 layouts with 12 images per page from a ZIP file"""
        if zip_file is None:
            return None, "❌ Please upload a ZIP file containing images"
        
        try:
            # A4 dimensions at 300 DPI (standard print resolution)
            A4_WIDTH = 2480  # 8.27 inches * 300 DPI
            A4_HEIGHT = 3508  # 11.69 inches * 300 DPI
            
            # Margins (0.5 inch on each side)
            MARGIN = 150  # 0.5 inch * 300 DPI
            
            # Calculate available space for images
            available_width = A4_WIDTH - (2 * MARGIN)
            available_height = A4_HEIGHT - (2 * MARGIN)
            
            # 12 images in 3 columns x 4 rows
            COLS = 3
            ROWS = 4
            IMAGES_PER_PAGE = COLS * ROWS
            
            # Calculate image size with small gaps between images
            GAP = 20  # Small gap between images
            image_width = (available_width - (GAP * (COLS - 1))) // COLS
            image_height = (available_height - (GAP * (ROWS - 1))) // ROWS
            
            # Extract images from ZIP
            temp_dir = tempfile.mkdtemp()
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            image_files = []
            with zipfile.ZipFile(zip_file.name, 'r') as zipf:
                for file_info in zipf.filelist:
                    if file_info.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        zipf.extract(file_info, extract_dir)
                        image_files.append(os.path.join(extract_dir, file_info.filename))
            
            if not image_files:
                return None, "❌ No image files found in the ZIP archive"
            
            # Sort image files for consistent ordering
            image_files.sort()
            
            log_messages = []
            log_messages.append(f"📊 Found {len(image_files)} images in ZIP file")
            log_messages.append(f"📄 Creating A4 layouts with {IMAGES_PER_PAGE} images per page")
            log_messages.append(f"🖼️ Each image will be {image_width}x{image_height} pixels")
            
            # Calculate number of pages needed
            num_pages = math.ceil(len(image_files) / IMAGES_PER_PAGE)
            log_messages.append(f"📑 Will create {num_pages} A4 page(s)")
            
            # Create A4 layout pages
            a4_pages = []
            for page_num in range(num_pages):
                # Create blank A4 page
                a4_page = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), 'white')
                
                # Calculate which images go on this page
                start_idx = page_num * IMAGES_PER_PAGE
                end_idx = min(start_idx + IMAGES_PER_PAGE, len(image_files))
                page_images = image_files[start_idx:end_idx]
                
                # Place images on the page
                for i, img_path in enumerate(page_images):
                    try:
                        # Calculate position
                        row = i // COLS
                        col = i % COLS
                        
                        x = MARGIN + col * (image_width + GAP)
                        y = MARGIN + row * (image_height + GAP)
                        
                        # Load and resize image
                        img = Image.open(img_path)
                        img_resized = img.resize((image_width, image_height), Image.Resampling.LANCZOS)
                        
                        # Paste image onto A4 page
                        a4_page.paste(img_resized, (x, y))
                        
                    except Exception as e:
                        log_messages.append(f"⚠️ Error processing image {os.path.basename(img_path)}: {str(e)}")
                        continue
                
                # Save A4 page
                page_filename = f"A4_Layout_Page_{page_num + 1:02d}.png"
                page_path = os.path.join(temp_dir, page_filename)
                a4_page.save(page_path, "PNG", dpi=(300, 300))
                a4_pages.append(page_path)
                
                log_messages.append(f"✅ Created page {page_num + 1} with {len(page_images)} images")
            
            # Create ZIP file with A4 layouts
            zip_path = os.path.join(temp_dir, "A4_Layouts.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for page_path in a4_pages:
                    zipf.write(page_path, os.path.basename(page_path))
            
            log_messages.append(f"📦 Created ZIP file with {len(a4_pages)} A4 layout page(s)")
            log_messages.append("🖨️ Ready for high-quality printing at 300 DPI")
            
            return zip_path, "\n".join(log_messages)
            
        except Exception as e:
            return None, f"❌ Error creating A4 layout: {str(e)}"

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://127.0.0.1:7860')

def create_interface():
    """Create Gradio interface"""
    generator = ImageGenerator()
    
    with gr.Blocks(title="CSV to Template Image Generator", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🖼️ CSV to Template Image Generator")
        gr.Markdown("Upload a CSV file and template image to generate batch images with QR codes")
        
        with gr.Tabs():
            with gr.TabItem("🎯 Generate Images"):
                create_image_generation_tab(generator)
            
            with gr.TabItem("📄 Create A4 Layouts"):
                create_a4_layout_tab(generator)
    
    return interface

def create_image_generation_tab(generator):
    """Create the image generation tab"""
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📄 Upload Files")
            csv_file = gr.File(
                label="CSV File", 
                file_types=[".csv"]
            )
            template_file = gr.File(
                label="Template Image", 
                file_types=[".jpg", ".jpeg", ".png"]
            )
            
            generate_btn = gr.Button("🚀 Generate Images", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### 📋 Expected CSV Format")
            gr.Textbox(
                value="""Name,URL,Price,RRP
Nival Blanco Matt 30x60,https://tilemania.com/nival-blanco,15.00,35
Carrara Marble Gloss 60x60,https://tilemania.com/carrara-marble,25.50,45""",
                label="CSV Format Example (Prices will be formatted as £XX.XX/m²)",
                lines=3,
                interactive=False
            )
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📊 Processing Log")
            log_output = gr.Textbox(
                label="Generation Log", 
                lines=10, 
                max_lines=20
            )
        
        with gr.Column():
            gr.Markdown("### 📦 Download")
            download_file = gr.File(
                label="Generated Images (ZIP)", 
                interactive=False
            )
    
    # Event handler
    generate_btn.click(
        fn=generator.process_csv_and_generate,
        inputs=[csv_file, template_file],
        outputs=[download_file, log_output]
    )
    
    gr.Markdown("""
    ### 📝 Instructions:
    1. **CSV File**: Upload a CSV with columns for Name, URL/Link, Price, and RRP
    2. **Template Image**: Upload your template image (like Ref.jpg)
    3. **Generate**: Click the generate button to create batch images
    4. **Download**: Get the ZIP file with all generated images
    
    ### 🎯 Features:
    - Flexible column name detection (Name/Product, URL/Link, Price/Now, RRP/Was)
    - QR code generation from URLs
    - Text overlay on template images
    - Batch processing with error handling
    - ZIP download of all generated images
    """)

def create_a4_layout_tab(generator):
    """Create the A4 layout tab"""
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📁 Upload ZIP File")
            zip_file = gr.File(
                label="ZIP File with Images", 
                file_types=[".zip"]
            )
            
            layout_btn = gr.Button("📄 Create A4 Layouts", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### 📐 Layout Information")
            gr.Markdown("""
            **A4 Layout Specifications:**
            - **Paper Size**: A4 (210 × 297 mm)
            - **Resolution**: 300 DPI (print quality)
            - **Images per page**: 12 (3 columns × 4 rows)
            - **Margins**: 0.5 inch on all sides
            - **Format**: PNG files ready for printing
            """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📊 Layout Log")
            a4_log_output = gr.Textbox(
                label="A4 Layout Log", 
                lines=10, 
                max_lines=20
            )
        
        with gr.Column():
            gr.Markdown("### 📦 Download A4 Layouts")
            a4_download_file = gr.File(
                label="A4 Layout Pages (ZIP)", 
                interactive=False
            )
    
    # Event handler
    layout_btn.click(
        fn=generator.create_a4_layout,
        inputs=[zip_file],
        outputs=[a4_download_file, a4_log_output]
    )
    
    gr.Markdown("""
    ### 📝 A4 Layout Instructions:
    1. **ZIP File**: Upload the ZIP file containing your generated images
    2. **Create Layouts**: Click to arrange images on A4 pages
    3. **Download**: Get the ZIP file with print-ready A4 layouts
    
    ### 🖨️ Printing Features:
    - **High Resolution**: 300 DPI for professional printing
    - **Optimal Layout**: 12 images per A4 page with proper margins
    - **Multiple Pages**: Automatically creates multiple pages if needed
    - **Print Ready**: Perfect for office or professional printing
    """)

if __name__ == "__main__":
    print("🚀 Starting CSV Template Generator...")
    print("📱 The application will open in your default web browser")
    print("🌐 If it doesn't open automatically, go to: http://127.0.0.1:7860")
    print("⏹️  Press Ctrl+C to stop the application")
    print("=" * 60)
    
    app = create_interface()
    
    # Open browser after a short delay
    Timer(2.0, open_browser).start()
    
    # Launch the app
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,  # Don't create public link for standalone version
        debug=False,  # Disable debug mode for production
        show_error=True,
        quiet=False
    )
