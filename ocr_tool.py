import cv2
import pytesseract
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR-tool")

        # Variables
        self.image_path = None
        self.preprocessor = None
        self.original_image = None
        self.binary_image = None
        self.crop_all_fraction = tk.DoubleVar(value=0.0)
        self.crop_top_fraction = tk.DoubleVar(value=0.0)
        self.crop_left_fraction = tk.DoubleVar(value=0.0)
        self.crop_right_fraction = tk.DoubleVar(value=0.0)
        self.crop_bottom_fraction = tk.DoubleVar(value=0.0)
        self.language = 'nld'
        self.config_list = ['3', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
        self.selected_config = tk.StringVar(self.root)
        self.resize_after_id = None

        # GUI Elements
        self.create_widgets()

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)

    def create_widgets(self):
        # Toolbar Frame
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.pack(fill=tk.X, padx=5, pady=5)

        # Button to open image
        self.open_button = ttk.Button(self.toolbar_frame, text="Open Image", command=self.open_image)
        self.open_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to save image
        self.save_button = ttk.Button(self.toolbar_frame, text='Save image', command=self.save_image)
        self.save_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Button to make PDF
        self.pdf_button = ttk.Button(self.toolbar_frame, text="Save as PDF", command=self.make_pdf)
        self.pdf_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Button to perform OCR
        self.ocr_button = ttk.Button(self.toolbar_frame, text='OCR', command=self.perform_ocr)
        self.ocr_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # PSM helper
        self.psm_help = ttk.Button(self.toolbar_frame, text='ⓘ', command=self.show_psm)
        self.psm_help.pack(side=tk.RIGHT)

        # Option menu
        self.config_menu = ttk.OptionMenu(self.toolbar_frame, self.selected_config, *self.config_list)
        self.config_menu.pack(side=tk.RIGHT, padx=5, pady=5)

        # PSM label
        self.config_label = ttk.Label(self.toolbar_frame, text='psm:')
        self.config_label.pack(side=tk.RIGHT, padx=5, pady=5)

        # Image Display Frame
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas for original image
        self.original_canvas = tk.Canvas(self.image_frame, bg="grey")
        self.original_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas for processed image
        self.processed_canvas = tk.Canvas(self.image_frame, bg="grey")
        self.processed_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Control Frame
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        self.crop_label = ttk.Label(self.control_frame, text='Crop Image:')
        self.crop_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Slider for crop fraction
        self.crop_all_label = ttk.Label(self.control_frame, text="All")
        self.crop_all_label.grid(row=1, column=0, padx=0, pady=0)
        self.crop_all_slider = ttk.Scale(self.control_frame, variable=self.crop_all_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_all_fraction)
        self.crop_all_slider.grid(row=1, column=1, padx=10, pady=10)

        self.crop_top_label = ttk.Label(self.control_frame, text="Top")
        self.crop_top_label.grid(row=2, column=0, padx=0, pady=0)
        self.crop_top_slider = ttk.Scale(self.control_frame, variable=self.crop_top_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_fraction)
        self.crop_top_slider.grid(row=2, column=1, padx=10, pady=10)

        self.crop_left_label = ttk.Label(self.control_frame, text="Left")
        self.crop_left_label.grid(row=3, column=0, padx=0, pady=0)
        self.crop_left_slider = ttk.Scale(self.control_frame, variable=self.crop_left_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_fraction)
        self.crop_left_slider.grid(row=3, column=1, padx=10, pady=10)

        self.crop_right_label = ttk.Label(self.control_frame, text="Right")
        self.crop_right_label.grid(row=4, column=0, padx=0, pady=0)
        self.crop_right_slider = ttk.Scale(self.control_frame, variable=self.crop_right_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_fraction)
        self.crop_right_slider.grid(row=4, column=1, padx=10, pady=10)

        self.crop_bottom_label = ttk.Label(self.control_frame, text="Bottom")
        self.crop_bottom_label.grid(row=5, column=0, padx=0, pady=0)
        self.crop_bottom_slider = ttk.Scale(self.control_frame, variable=self.crop_bottom_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_fraction)
        self.crop_bottom_slider.grid(row=5, column=1, padx=10, pady=10)

        # Button to binarize
        self.binarize_button = ttk.Button(self.control_frame, text='Binarize', command=self.binarize_image)
        self.binarize_button.grid(row=6, column=0, padx=5, pady=5, columnspan=2)

        # Configure grid weights
        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=1)

    def open_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if self.image_path:
            try:
                self.original_image = cv2.imread(self.image_path)
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.binary_image = self.original_image
                self.display_image(self.original_image, self.original_canvas)
                self.display_image(self.binary_image, self.processed_canvas)

            except Exception as e:
                print(f"Error opening image: {e}")

    def display_image(self, image, canvas):
        """Display the image on the canvas while maintaining aspect ratio."""
        canvas.delete("all")  # Clear the canvas before displaying a new image

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Calculate the scaled dimensions to fit the canvas
        image_height, image_width = image.shape[:2]
        scale = min(canvas_width / image_width, canvas_height / image_height)
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        # Resize the image using OpenCV
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Convert the OpenCV image to a Tkinter-compatible format
        photo = ImageTk.PhotoImage(image=Image.fromarray(resized))
        canvas.image = photo
        # Center the image on the canvas
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2
        canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo)

    def on_window_resize(self, event):
        """Handle window resize event with a delay to prevent excessive calls."""
        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
        self.resize_after_id = self.root.after(300, self.resize_images)

    def resize_images(self):
        """Resizes and updates displayed images."""
        if self.original_image is not None:
            self.display_image(self.original_image, self.original_canvas)
        if self.binary_image is not None:
            self.display_image(self.binary_image, self.processed_canvas)

    def update_crop_all_fraction(self, value):
        all_value = self.crop_all_fraction.get()
        self.crop_top_fraction.set(all_value)
        self.crop_left_fraction.set(all_value)
        self.crop_right_fraction.set(all_value)
        self.crop_bottom_fraction.set(all_value)
        
        if self.original_image is not None:
            self.crop_image()

    def update_crop_fraction(self, value):
        self.crop_all_fraction.set(0.0)
        if self.original_image is not None:
            self.crop_image()

    def crop_image(self):
        self.binary_image = self.original_image
        height, width = self.original_image.shape[:2]
        left = int(width * self.crop_left_fraction.get())
        top = int(height * self.crop_top_fraction.get())
        right = int(width * (1 - self.crop_right_fraction.get()))
        bottom = int(height * (1 - self.crop_bottom_fraction.get()))
        self.binary_image = self.binary_image[top:bottom, left:right]
        self.display_image(self.binary_image, self.processed_canvas)

    def binarize_image(self):
        if self.binary_image is not None:
            self.preprocessor = OCRpreprocessor(self.binary_image)
            self.preprocessor.process()
            self.binary_image = self.preprocessor.binary
            self.display_image(self.binary_image, self.processed_canvas)

    def perform_ocr(self):
        if self.binary_image is None:
            messagebox.showwarning("No Image", "Please process an image first.")
            return
        self.ocr_button.config(state='disabled')

        # Perform OCR using pytesseract
        custom_config = f'--oem 3 --psm {self.selected_config.get()}'
        ocr_text = pytesseract.image_to_string(self.binary_image, lang=self.language, config=custom_config)
        self.ocr_button.config(state='normal')
        self.show_ocr_result(ocr_text)

    def show_ocr_result(self, ocr_text):
        if ocr_text is None:
            return

        # Create a new window to display the OCR text
        ocr_window = tk.Toplevel(self.root)
        ocr_window.title("OCR Result")

        # Create a text widget to display the OCR text
        text_widget = tk.Text(ocr_window, wrap=tk.WORD)
        text_widget.insert(tk.END, ocr_text)
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Add buttons for saving as TXT, PDF, or ALTO XML
        button_frame = ttk.Frame(ocr_window)
        button_frame.pack(pady=10)

        txt_button = ttk.Button(button_frame, text="Save as .txt", command=lambda: self.save_as_txt(ocr_text))
        txt_button.pack(side=tk.LEFT, padx=5)
    
    def show_psm(self):
        psm_options = """
        Page segmentation modes:\n
  0    Orientation and script detection (OSD) only.\n
  1    Automatic page segmentation with OSD.\n
  2    Automatic page segmentation, but no OSD, or OCR.\n
  3    Fully automatic page segmentation, but no OSD. (Default)\n
  4    Assume a single column of text of variable sizes.\n
  5    Assume a single uniform block of vertically aligned text.\n
  6    Assume a single uniform block of text.\n
  7    Treat the image as a single text line.\n
  8    Treat the image as a single word.\n
  9    Treat the image as a single word in a circle.\n
 10    Treat the image as a single character.\n
 11    Sparse text. Find as much text as possible in no particular order.\n
 12    Sparse text with OSD.\n
 13    Raw line. Treat the image as a single text line,\n
       bypassing hacks that are Tesseract-specific.
        """
        tk.messagebox.showinfo(title=None, message=psm_options)

    def save_as_txt(self, text):
        if text is None:
            return

        # Open file dialog to save the TXT file
        filepath = filedialog.asksaveasfilename(
            title='Save as TXT',
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )

        if filepath:
            # Write the OCR text to the file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(text)
            messagebox.showinfo("Success", f"Text saved to {filepath}")

    def make_pdf(self):
        if self.binary_image is None:
            messagebox.showwarning("No Image", "Please process an image first.")
            return

        # Perform OCR using pytesseract with the custom config
        custom_config = f'--oem 3 --psm {self.selected_config.get()}'
        pdf_data = pytesseract.image_to_pdf_or_hocr(self.binary_image, config=custom_config, lang=self.language, extension='pdf')

        # Open file dialog to select where to save the PDF
        filepath = filedialog.asksaveasfilename(
            title='Save PDF',
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )

        # Save the PDF if a file path is provided
        if filepath:
            with open(filepath, 'wb') as pdf_file:
                pdf_file.write(pdf_data)
            messagebox.showinfo("Success", f"PDF saved to {filepath}")

    def save_image(self):
        if self.binary_image is not None:
            filepath = filedialog.asksaveasfilename(
                title='Save processed image',
                defaultextension='.jpg',
                filetypes=(("JPG files", "*.jpg"), ("All files", "*.*"))
            )

            if filepath:
                Image.fromarray(self.binary_image).save(filepath, dpi=(300, 300))
                messagebox.showinfo("Success", f'JPG saved to {filepath}')

class OCRpreprocessor:
    def __init__(self, image):
        self.original = image
        if self.original is None:
            raise ValueError("Could not load image")
        self.gray = None
        self.binary = None
        self.processed = None

    def get_grayscale(self):
        self.gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        return self
    
    def remove_noise(self):
        if self.gray is None:
            self.gray = self.get_grayscale()
        self.gray = cv2.GaussianBlur(self.gray, (1,1), 0)
        return self
    
    def binarize(self):
        if self.gray is None:
            self.gray = self.get_grayscale()

        _, otsu = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.binary = otsu
        return self

    def dilate(self):
        """Dilate the image to connect text components"""
        if self.binary is None:
            self.binarize()
            
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        self.binary = cv2.dilate(self.binary, kernel, iterations=1)
        return self

    def erode(self):
        """Erode the image to remove small noise"""
        if self.binary is None:
            self.binarize()
            
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        self.binary = cv2.erode(self.binary, kernel, iterations=1)
        return self
    
    def process(self):
        return (self.get_grayscale()
                .remove_noise()
                .binarize()
                .dilate()
                .erode())


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()