import fpdf 
import PIL
from PIL import Image, ImageDraw, ImageFont
import sys
import traceback
import os
from pypdf import PdfReader,PdfWriter
#===plt====
# 1. Undercover Matplotlib setup to prevent mobile GUI paywall crashes
mpl = __import__('matplotlib')
mpl.use('Agg') # Lock to background mode safely
plt = __import__('matplotlib.pyplot', globals(), locals(), ['pyplot'])
#====plt====

#================================
#Generate  jpegs images with analysis report 
#================================


class JPEGReportBook:
    """ 
    Args:
        page_size:tuple =(width,height),
        output_dir:st = "Reports",
        github_url:str = None
    """
    def __init__(self,page_size =(1240,1754),output_dir = "Reports",github_url = None):
        self.output_dir = output_dir
        self.page_size = page_size
        self.github_url = github_url
        self.page_count = 0
        #Make dirs/folder
        os.makedirs(self.output_dir,exist_ok = True)
        #Dynamic scaling
        canvas_width = self.page_size[0]
        self.title_size = int(canvas_width *0.052)#~64px
        self.body_size = int(canvas_width*0.032)#~ 40px
        self.footer_size = int(canvas_width
        * 0.020) #~ 25px
        self.page_size_f = int(canvas_width*0.016)#~ 20px
        
        #Load system fonts safely 
        self._load_fonts()
    
    def _load_fonts(self):
        """Find and load in system font without matplotlib font system"""
        font_paths = [
            "/data/user/0/ru.turor.pydroid3/files/arm-linux-androideabi/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf",
            "/system/fonts/Roboto-Regular.ttf",
            "LiberationSans-Regular.ttf"
        ]
        
        #Search for existing  font in font_paths 
        chosen_font  = None
        for font in font_paths:
            if os.path.exists(font):
                chosen_font = font
                break               
        #
        if chosen_font:
            self.font_title = ImageFont.truetype(chosen_font, self.title_size)
            self.font_body = ImageFont.truetype(chosen_font, self.body_size)
            self.font_footer = ImageFont.truetype(chosen_font, self.footer_size)
            self.font_page = ImageFont.truetype(chosen_font, self.page_size_f)
            print(f"[SUCCESS] Layout typography initialized with: {os.path.basename(chosen_font)}")
        else:
            self.font_title = self.font_body = self.font_footer = self.font_page = ImageFont.load_default()            


    def _wrap_text_by_font(self,text,font,max_width):
       """
        Smart-wraps sentences based on pixel width instead of character count.
        This prevents words from splitting in half across lines!
        """
       words = text.split(" ")
       lines = []
       current_line = []
       
       #Dummy draw context to measure text pixel dimensions
       canvas_dummy =  Image.new("RGB",(1,1))
       draw_dummy = ImageDraw.Draw(canvas_dummy)
       
       for word in words:
           test_line =  " ".join(current_line + [word]) if current_line else word
           line_w =  draw_dummy.textlength(test_line,font = font)
           
           if  line_w <= max_width:
               current_line.append(word)
           else:
               if current_line:
                    line.append(' '.join(current_line))
               current_line = [word]
                    
       if current_line:
            line.append(' '.join(current_line))
            
       return "\n".join(lines)           

    # INTERNAL LAYOUT CONTAINER CANVAS BUILDER
    def _create_page(self, image_path, title, summary):
        self.page_count += 1

        # Premium Slate Dark Theme
        canvas = Image.new("RGB", self.page_size, "#121212") 
        draw = ImageDraw.Draw(canvas)
        margin_x = 80
        max_text_width = self.page_size[0] - (margin_x * 2) 

        # 1. Wrap and Draw Title
        wrapped_title = self._wrap_text_by_pixels(title.upper(), self.font_title, max_text_width)
        title_lines = len(wrapped_title.split('\n'))
        title_y_start = 70
        
        draw.text((margin_x, title_y_start), wrapped_title, fill="#17a2b8", font=self.font_title, spacing=12)
        
        line_y = title_y_start + (title_lines * (self.title_size + 12)) + 20
        draw.line([(margin_x, line_y), (self.page_size[0] - margin_x, line_y)], fill="#2d2d2d", width=4)

        # 2. Position Content / Adjust text position if image_path is None
        image_y_start = line_y + 50
        
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            max_img_h = 750 if title_lines > 1 else 850
            img.thumbnail((1080, max_img_h))
            
            x = (self.page_size[0] - img.width) // 2
            canvas.paste(img, (x, image_y_start))
            text_y_start = image_y_start + img.height + 40
            img.close()
        else:
            # If no image path is provided, push the summary up cleanly right under the title line
            text_y_start = image_y_start + 20

        # Enforce baseline coordinates only if an image actually exists
        if image_path and os.path.exists(image_path) and text_y_start < 1160:
            text_y_start = 1160

        # 3. Wrap and Draw Summary Text Block
        wrapped_summary = self._wrap_text_by_pixels(summary, self.font_body, max_text_width)
        draw.text((margin_x, text_y_start), wrapped_summary, fill="#ffffff", font=self.font_body, spacing=22)

        # Bottom Structural Footers
        footer_y = self.page_size[1] - 130
        draw.line([(margin_x, footer_y), (self.page_size[0] - margin_x, footer_y)], fill="#2d2d2d", width=2)
        
        if self.github_url:
            draw.text((margin_x, footer_y + 30), f"GitHub Source: {self.github_url}", fill="#4fc1ff", font=self.font_footer)
            
        draw.text((self.page_size[0] - 420, footer_y + 30), "Mpho048 Workspace", fill="#28a745", font=self.font_footer)
        draw.text((self.page_size[0] - 160, footer_y + 80), f"Page {self.page_count}", fill="#888888", font=self.font_page)

        output_file = os.path.join(self.output_dir, f"portfolio_slide_{self.page_count}.jpeg")
        canvas.save(output_file, "JPEG", quality=95)
        
        # Only clean temporary files if a valid path string starting with '_' was passed
        if image_path and os.path.exists(image_path) and os.path.basename(image_path).startswith("_"):
            os.remove(image_path)
            
        return output_file                                           
    # NATIVE TABLE DRAWING LAYER (NO PLT CALLS)
    def add_table(self,df,title,summary):
        """
        Draws structured matrices with clean Pillow boxes.
        Args:
            title:str,
            df:pd.DataFrame,
            summary:str
        """
        temp_file = "_table.png"
        t_width,t_height = 1080,500
        t_img = Image.new("RGB",(t_width, t_height), "#1e1e1e")
        t_draw = ImageDraw.Draw(t_img)
        
        #Get df data(Cols and values)
        cols = list(df.columns)
        rows = df.values.tolist()
        num_cols = len(cols)
        num_rows = len(rows) +1
        
        # Table cell calculation
        cell_w = t_width // num_cols
        cell_h = t_height // num_rows
        
        for r_idx in range(num_rows):
            for c_idx in range(num_cols):
                x1 = c_idx * cell_w 
                y1 = r_idx * cell_h
                x2 =  x1 + cell_w
                y2 = y1 + cell_h
                
                bg_color =  "#2d2d2d"  if r_idx == 0 else "#1e1e1e" 
                t_draw.rectangle([x1,y1,x2,y2],fill = bg_color, outline = "#3c3c3c",width = 2)
                
                val = cols[c_idx] if r_idx == 0 else str(rows[r_idx - 1][c_idx])
                t_draw.text((x1 +20,y1 +(cell_h // 3)),val,fill = "white", font = self.font_footer)
                
        t_img.save(temp_file, "PNG")
        t_img.close()
        
        return self._create_page(temp_file, title,summary)
        
    #DIRECT IMAGE/GRAPH PAGE LOADER
    def add_graph_page(self,image_path,title,summary):
        """
        Accepts a direct image file path string (e.g., 'bar.png').
        If image_path is None, it cleanly prints a text-only slide.
        """
        return self._create_page(image_path, title,summary)                                                                                                
#================================
#WRITE 🚫ERROR TO PDF/TEXT FILE.
#================================
os.environ['KIVY_NO_ARGS'] = '1'
def log_terminal_crash(error_message,format = "txt"):
    """Writes the exact crash text to a file so you never lose it.
    ARGS:
        error_message:exception,
    """
    file_name = "Crash_log"
    trace_text = traceback.format_exc()
    log_content = (
    "=============================\n"
    "🔴 KIVY APP CRASH REPORT DETECTED\n"
    "=============================\n\n"
    f"Error Found: {error_message}\n\n"
        f"Full Code Traceback Stack:\n{trace_text}"
    )
    if format.lower() == "txt":
        with open(f"{file_name}.txt","w") as log_file:
            log_file.write(log_content)           
    elif format.lower() == "pdf":
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B",14)
        pdf.cel(0,10,"Kivy App Crash Report:",inplace = True)
        pdf.ln(6)
        pdf.set_font("courier","",10)
        pdf.set_text_color(255,0,0)
        pdf.multi_cell(0,5,log_content)
    else:
        return  "Invalid file format (txt or pdf)" #I want to raise Exception forgot how to,help
    print(f"\n[CRASH DETECTED] Error written safely to '{file_name}.{format}'")




#================================
#CODE TO IMAGE[.py --->> .png]
#================================
def image_code(source_file,s= 0,l= 26 ,output_image_name="fiverr_ready.png"):
    print(f"Generating crisp portfolio card for {source_file}...")
    try:
        with open(source_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: '{source_file}' not found.")
        return

    # Canvas setup - 16:9 ratio for premium Fiverr presentation
    fig, ax = plt.subplots(figsize=(13, 8), facecolor='#1e1e1e')
    ax.axis('off')

    x_start = 0.05
    y_start = 0.92
    line_height = 0.032  # Large spacing for big fonts

    # Fit the first 26 lines cleanly so nothing feels crowded
    for idx, line in enumerate(lines[s:l]):
        current_y = y_start - (idx * line_height)
        clean_line = line.rstrip('\n')
        stripped = clean_line.strip()

        # Rule 1: Set color base based on line type (avoids overlaps)
        if stripped.startswith("#"):
            color = '#6a9955'  # Python Comment Green
        elif stripped.startswith("import") or stripped.startswith("from "):
            color = '#4fc1ff'  # Package Import Cyan Blue
        elif "print(" in clean_line or "pd.read_csv" in clean_line:
            color = '#dcdcaa'  # Function Call Yellow
        elif "'" in clean_line or '"' in clean_line:
            color = '#ce9178'  # Data Query / String Orange
        else:
            color = '#d4d4d4'  # Standard Code White/Grey

        # Draw the ENTIRE line at once. This guarantees spaces can NEVER break.
        ax.text(x_start, current_y, clean_line, transform=ax.transAxes,
                fontsize=13,          # Large, highly readable font
                fontfamily='monospace', # Keeps indentation perfectly aligned
                color=color, 
                va='top')

    # Sleek branding mark at the bottom right corner
    fig.text(0.95, 0.04, "Verified Python Data Pipeline", 
             fontsize=13, fontfamily='sans-serif', color='#17a2b8',
             weight='bold', horizontalalignment='right')

    plt.savefig(output_image_name, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"[SUCCESS] Portfolio card generated without space errors: {output_image_name}")




#================================
#CONVERT IMAGES TO PDF,PNG,JGP,JPEG.
#================================
def convert_image(path,new,format_tar = "jpeg"):
    """Convert images into different formats
    Args:
        name:str,original file name
        new:str,new name for the file
        format:str,[png,jpeg,jpg,pdf]
    """
    if not path.lower().endswith(("png", "jpg", "jpeg", "pdf")):
        return "Add file extension to file, e.g. png"
            
    print(f"[SYSTEM] Converting '{path}' into {format_tar.upper()}...")
    
    try:
        img = PIL.Image.open(path)
        
        if format_tar.lower() in ["png","jpg","pdf","jpeg"]:
            if img.mode in ("RGBA","P"):
                img = img.convert("RGB")
            final_path = f"{new}.{format_tar.lower()}"
            img.save(final_path,format = format_tar.upper(),quality=95)
            print(f"[SUCCESS] Image saved successfully: '{final_path}'")         
    except Exception as e:
      print(f"[ERROR] Extension conversion failed: {e}")                    
 