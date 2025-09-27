import gradio as gr
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
import zipfile
import os
import tempfile
import io
from typing import Optional, Tuple, List


class ImageGenerator:
    def __init__(self):
        self.temp_dir = None
        
    def generate_qr_code(self, data: str, size: int = 100) -> Image.Image:
        """Generate QR code from data string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        return qr_img.resize((size, size), Image.Resampling.LANCZOS)
    
    def get_default_font(self, size: int = 20) -> ImageFont.ImageFont:
        """Get default font, fallback to default if custom font not available"""
        try:
            # Try to use a common system font
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except:
                return ImageFont.load_default()
    
    def overlay_text_and_qr(self, template: Image.Image, row_data: dict, row_index: int) -> Image.Image:
        """Overlay text and QR code on template image to match tile label design"""
        # Create a copy of the template
        img = template.copy()
        draw = ImageDraw.Draw(img)
        
        # Get image dimensions for positioning
        width, height = img.size
        
        # Define fonts for different elements
        fonts = {
            'header': self.get_default_font(32),      # TILE MANIA
            'product_name': self.get_default_font(28), # Product name
            'subtitle': self.get_default_font(18),     # Wall And Floor
            'rrp': self.get_default_font(16),          # RRP price
            'now_price': self.get_default_font(24),    # Now price
            'call_to_action': self.get_default_font(14), # Buy Online text
            'checkboxes': self.get_default_font(14)    # Checkbox labels
        }
        
        # Colors
        colors = {
            'black': (0, 0, 0),
            'red': (220, 20, 20),
            'white': (255, 255, 255),
            'gray': (128, 128, 128)
        }
        
        # Layout positions (adjust based on your template size)
        margin_left = 30
        margin_top = 60
        
        # 1. TILE MANIA header (top center)
        header_text = "TILE MANIA"
        header_bbox = draw.textbbox((0, 0), header_text, font=fonts['header'])
        header_width = header_bbox[2] - header_bbox[0]
        header_x = (width - header_width) // 2
        draw.text((header_x, 20), header_text, fill=colors['black'], font=fonts['header'])
        
        # 2. Product name
        product_name = str(row_data.get('name', 'Product Name'))
        draw.text((margin_left, margin_top), product_name, fill=colors['black'], font=fonts['product_name'])
        
        # 3. Subtitle "Wall And Floor"
        subtitle_y = margin_top + 35
        draw.text((margin_left, subtitle_y), "Wall And Floor", fill=colors['black'], font=fonts['subtitle'])
        
        # 4. RRP with strikethrough
        rrp_y = subtitle_y + 40
        if 'rrp' in row_data and pd.notna(row_data['rrp']):
            rrp_text = f"Rrp £{row_data['rrp']}"
            draw.text((margin_left, rrp_y), rrp_text, fill=colors['gray'], font=fonts['rrp'])
            
            # Add strikethrough line
            rrp_bbox = draw.textbbox((margin_left, rrp_y), rrp_text, font=fonts['rrp'])
            line_y = rrp_y + (rrp_bbox[3] - rrp_bbox[1]) // 2
            draw.line([(margin_left, line_y), (rrp_bbox[2], line_y)], fill=colors['gray'], width=2)
        
        # 5. "Now" price in red
        now_y = rrp_y + 25
        if 'price' in row_data and pd.notna(row_data['price']):
            now_text = f"Now £{row_data['price']}/m2"
            draw.text((margin_left, now_y), now_text, fill=colors['red'], font=fonts['now_price'])
        
        # 6. "Buy Online? Scan Me Now" with arrow
        cta_y = now_y + 50
        cta_text = "Buy Online?"
        draw.text((margin_left, cta_y), cta_text, fill=colors['black'], font=fonts['call_to_action'])
        
        scan_y = cta_y + 20
        scan_text = "Scan Me Now"
        draw.text((margin_left, scan_y), scan_text, fill=colors['black'], font=fonts['call_to_action'])
        
        # Arrow pointing to QR code
        arrow_start_x = margin_left + 100
        arrow_y = scan_y + 8
        arrow_end_x = width - 160
        # Draw arrow line
        draw.line([(arrow_start_x, arrow_y), (arrow_end_x, arrow_y)], fill=colors['black'], width=2)
        # Draw arrowhead
        draw.polygon([(arrow_end_x, arrow_y), (arrow_end_x-10, arrow_y-5), (arrow_end_x-10, arrow_y+5)], fill=colors['black'])
        
        # 7. Checkboxes at bottom
        checkbox_y = height - 60
        checkbox_options = ["☐ Porcelain", "☐ Ceramic", "☐ Wall", "☐ Floor"]
        checkbox_x = margin_left
        
        for i, option in enumerate(checkbox_options):
            x_pos = checkbox_x + (i * 80)  # Space checkboxes evenly
            if x_pos + 70 < width - 150:  # Don't overlap with QR code
                draw.text((x_pos, checkbox_y), option, fill=colors['black'], font=fonts['checkboxes'])
        
        # 8. Generate and overlay QR code
        if 'url' in row_data and pd.notna(row_data['url']):
            qr_img = self.generate_qr_code(str(row_data['url']), size=120)
            qr_x = width - 140
            qr_y = subtitle_y + 20
            img.paste(qr_img, (qr_x, qr_y))
        
        return img
    
    def process_csv_and_template(self, csv_file, template_file=None) -> Optional[str]:
        """Process CSV to generate tile label images"""
        if csv_file is None:
            return None
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Validate CSV has required columns (case-insensitive)
            df.columns = df.columns.str.lower()  # Convert to lowercase for consistency
            required_columns = ['name', 'url', 'price', 'rrp']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"CSV missing required columns: {missing_columns}")
            
            # Create a standard white template for tile labels (400x300 pixels)
            template = Image.new('RGB', (400, 300), color='white')
            
            # Create temporary directory for generated images
            self.temp_dir = tempfile.mkdtemp()
            generated_files = []
            
            # Process each row
            for index, row in df.iterrows():
                # Generate image for this row
                generated_img = self.overlay_text_and_qr(template, row, index)
                
                # Create filename
                product_name = str(row.get('name', f'product_{index}')).replace(' ', '_')
                filename = f"{index:03d}_{product_name}.png"
                filepath = os.path.join(self.temp_dir, filename)
                
                # Save image
                generated_img.save(filepath, 'PNG')
                generated_files.append(filepath)
            
            # Create ZIP file
            zip_path = os.path.join(self.temp_dir, 'generated_images.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in generated_files:
                    zipf.write(file_path, os.path.basename(file_path))
            
            return zip_path
            
        except Exception as e:
            return f"Error: {str(e)}"


def create_gradio_interface():
    """Create and configure Gradio interface"""
    generator = ImageGenerator()
    
    def process_files(csv_file):
        """Process uploaded CSV file and return download link"""
        if csv_file is None:
            return "Please upload a CSV file"
        
        result = generator.process_csv_and_template(csv_file)
        
        if result and not result.startswith("Error"):
            return result
        else:
            return result or "Failed to process files"
    
    # Create Gradio interface
    with gr.Blocks(title="Tile Mania Label Generator") as demo:
        gr.Markdown("""
        # 🏠 Tile Mania Label Generator
        
        Upload a CSV file with your tile product data to automatically generate professional tile labels with QR codes.
        
        **CSV Requirements:**
        - Must contain columns: `name`, `url`, `price`, `rrp`
        - `name`: Product name (e.g., "Nival Blanco Matt 30x60")
        - `url`: Website URL for QR code generation
        - `price`: Current selling price per m2
        - `rrp`: Recommended retail price
        
        **Generated Labels Include:**
        - TILE MANIA header, product details, prices, QR code, and checkboxes
        - Standard 400x300 pixel white background
        - Professional tile industry formatting
        """)
        
        with gr.Row():
            with gr.Column():
                csv_input = gr.File(
                    label="Upload CSV File",
                    file_types=[".csv"],
                    type="filepath"
                )
                
                generate_btn = gr.Button("Generate Tile Labels", variant="primary")
            
            with gr.Column():
                output = gr.File(
                    label="Download Generated Images (ZIP)",
                    type="filepath"
                )
        
        # Connect the processing function
        generate_btn.click(
            fn=process_files,
            inputs=[csv_input],
            outputs=output
        )
        
        gr.Markdown("""
        ### Example CSV Format:
        ```
        Name,URL,Price,RRP
        Nival Blanco Matt 30x60,https://tilemania.com/nival-blanco-matt,15.00,35
        Carrara Marble Gloss 60x60,https://tilemania.com/carrara-marble,25.50,45
        ```
        
        ### How it works:
        1. Upload your CSV with tile product data
        2. Click "Generate Tile Labels" 
        3. Download the ZIP file with all generated tile labels
        
        Each label will include:
        - **TILE MANIA** header (centered at top)
        - Product name and "Wall And Floor" subtitle
        - RRP price with strikethrough (in gray)
        - Current price in red with "Now £X.XX/m2" format
        - "Buy Online? Scan Me Now" call-to-action with arrow
        - QR code (right side, generated from URL)
        - Checkboxes for Porcelain, Ceramic, Wall, Floor (bottom)
        """)
    
    return demo


if __name__ == "__main__":
    # Create and launch the Gradio app
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
