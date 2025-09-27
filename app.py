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
        self.FONT_SIZE_LARGE = 28  # For product name
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
            price_text = str(price)
            rrp_text = str(rrp)
            
            # Draw text overlays using dynamic font sizing with bold fonts
            # Draw name text (potentially multi-line) - use bold large font
            name_font = self.get_large_font(bold=True)
            for i, line in enumerate(name_lines):
                line_y = self.NAME_POS[1] + (i * (self.FONT_SIZE_LARGE + 2))  # Add small line spacing
                draw.text((self.NAME_POS[0], line_y), line, fill="black", font=name_font)
            # Draw prices with bold fonts
            draw.text(self.RRP_POS, f"RRP: ${rrp_text}", fill="black", font=self.get_medium_font(bold=True))
            draw.text(self.NOW_POS, f"Now: ${price_text}", fill="red", font=self.get_large_font(bold=True))
            
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

def create_interface():
    """Create Gradio interface"""
    generator = ImageGenerator()
    
    with gr.Blocks(title="CSV to Template Image Generator", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🖼️ CSV to Template Image Generator")
        gr.Markdown("Upload a CSV file and template image to generate batch images with QR codes")
        
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
                    label="CSV Format Example",
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
    
    return interface

if __name__ == "__main__":
    app = create_interface()
    app.launch(share=True, debug=True)
