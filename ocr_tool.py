import os
import cv2
import json
import pytesseract
import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
from typing import List, Optional
from tkinter import ttk, messagebox, filedialog, Menu

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR-tool")

        # Variables
        self.folder_path: Optional[str] = None
        self.file_list: Optional[List[str]] = None
        self.image_path: Optional[str] = None
        self.preprocessor = None
        self.original_image = None
        self.binary_image = None
        self.crop_all_fraction = tk.DoubleVar(value=0.0)
        self.crop_top_fraction = tk.DoubleVar(value=0.0)
        self.crop_left_fraction = tk.DoubleVar(value=0.0)
        self.crop_right_fraction = tk.DoubleVar(value=0.0)
        self.crop_bottom_fraction = tk.DoubleVar(value=0.0)
        self.language: str = 'nld'
        self.config_list: List[int] = [3, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.selected_config = tk.StringVar(self.root)
        self.resize_after_id = None

        # GUI Elements
        self.create_widgets()

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)

    def create_widgets(self) -> None:
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File Menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open File...", command=self.select_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Open Folder...", command=self.select_folder, accelerator="Ctrl+F")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save Image...", command=self.save_image, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save as PDF...", command=self.make_pdf, accelerator="Ctrl+P")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")

        # Help Menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="PSM Help", command=self.show_psm)

        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.select_file())
        self.root.bind('<Control-f>', lambda e: self.select_folder())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-p>', lambda e: self.make_pdf())
        self.root.bind('<Control-r>', lambda e: self.perform_ocr())

        # Image Display Frame
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas for original image
        self.original_canvas = tk.Canvas(self.image_frame, bg='grey')
        self.original_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas for processed image
        self.processed_canvas = tk.Canvas(self.image_frame, bg='grey')
        self.processed_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Control Frame
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_rowconfigure(1, weight=1)
        self.control_frame.grid_rowconfigure(2, weight=1)

        # OCR
        self.ocr_frame = tk.Frame(self.control_frame)
        self.ocr_frame.grid(row=0, sticky='n')

        self.ocr_button = ttk.Button(self.ocr_frame, text='Perform OCR', command=self.perform_ocr)
        self.ocr_button.grid(row=1, column=0, padx=5, pady=5, columnspan=3, sticky='nsew')

        self.config_label = ttk.Label(self.ocr_frame, text='PSM mode:')
        self.config_label.grid(row=0, column=0, padx=5, pady=10, columnspan=2)

        self.config_menu = ttk.OptionMenu(self.ocr_frame, self.selected_config, *self.config_list)
        self.config_menu.grid(row=0, column=2, padx=5, pady=10)

        # Cropping
        self.crop_frame = tk.Frame(self.control_frame)
        self.crop_frame.grid(row=1)

        self.crop_label = ttk.Label(self.crop_frame, text='Crop Image:')
        self.crop_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.crop_all_label = ttk.Label(self.crop_frame, text="All")
        self.crop_all_label.grid(row=1, column=0, padx=0, pady=0)
        self.crop_all_slider = ttk.Scale(self.crop_frame, variable=self.crop_all_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_all_fraction)
        self.crop_all_slider.grid(row=1, column=1, padx=10, pady=10)

        self.crop_top_label = ttk.Label(self.crop_frame, text="Top")
        self.crop_top_label.grid(row=3, column=0, padx=0, pady=0)
        self.crop_top_slider = ttk.Scale(self.crop_frame, variable=self.crop_top_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_fraction)
        self.crop_top_slider.grid(row=3, column=1, padx=10, pady=10)

        self.crop_left_label = ttk.Label(self.crop_frame, text="Left")
        self.crop_left_label.grid(row=4, column=0, padx=0, pady=0)
        self.crop_left_slider = ttk.Scale(self.crop_frame, variable=self.crop_left_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_fraction)
        self.crop_left_slider.grid(row=4, column=1, padx=10, pady=10)

        self.crop_right_label = ttk.Label(self.crop_frame, text="Right")
        self.crop_right_label.grid(row=5, column=0, padx=0, pady=0)
        self.crop_right_slider = ttk.Scale(self.crop_frame, variable=self.crop_right_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_fraction)
        self.crop_right_slider.grid(row=5, column=1, padx=10, pady=10)

        self.crop_bottom_label = ttk.Label(self.crop_frame, text="Bottom")
        self.crop_bottom_label.grid(row=6, column=0, padx=0, pady=0)
        self.crop_bottom_slider = ttk.Scale(self.crop_frame, variable=self.crop_bottom_fraction, from_=0.0, to=0.25, orient=tk.HORIZONTAL, length=100, command=self.update_crop_fraction)
        self.crop_bottom_slider.grid(row=6, column=1, padx=10, pady=10)


        # Binarizing
        self.binarize_frame = tk.Frame(self.crop_frame)
        self.binarize_frame.grid(row=7, column=0, columnspan=2)

        self.binarize_button = ttk.Button(self.binarize_frame, text='Binarize', command=self.binarize_image)
        self.binarize_button.grid(row=0, column=0, padx=5, pady=10)

        self.unbinarize_button = ttk.Button(self.binarize_frame, text='Undo', command=self.crop_image)
        self.unbinarize_button.grid(row=0, column=1, padx=5, pady=10)

        # Image Buttons
        self.image_control_frame = tk.Frame(self.control_frame)
        self.image_control_frame.grid(row=2, sticky='s')

        self.previous_button = ttk.Button(self.image_control_frame, text="Previous", command=self.previous_file, state='disabled')
        self.previous_button.grid(row=0, column=0, padx=5, pady=10)

        self.next_button = ttk.Button(self.image_control_frame, text="Next", command=self.next_file, state='disabled')
        self.next_button.grid(row=0, column=1, padx=5, pady=10)

    def select_file(self) -> None:
        self.image_path: Optional[str] = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        self.open_image()
        self.folder_path = None
        self.next_button['state'] = 'disabled'
        self.previous_button['state'] = 'disabled'
    
    def select_folder(self) -> None:
        self.folder_path: Optional[str] = filedialog.askdirectory()
        self.file_list = None
        self.file_list = sorted(os.listdir(self.folder_path))
        self.image_path = os.path.join(self.folder_path, self.file_list[0])
        self.open_image()
        self.crop_image()
        self.next_button['state'] = 'normal'
        self.previous_button['state'] = 'normal'

    def open_image(self) -> None:
        if self.image_path:
            try:
                self.original_image = cv2.imread(self.image_path)
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.binary_image = self.original_image
                self.display_image(self.original_image, self.original_canvas)
                self.display_image(self.binary_image, self.processed_canvas)

            except Exception as e:
                print(f"Error opening image: {e}")
    
    def next_file(self) -> None:
        if self.image_path is not None and self.folder_path is not None:
            temp_path: str = os.path.split(self.image_path)[-1]
            if temp_path != self.file_list[-1]:
                index: int = self.file_list.index(temp_path)
                self.image_path: str = os.path.join(self.folder_path, self.file_list[index + 1])
                self.open_image()
                self.crop_image()
    
    def previous_file(self) -> None:
        if self.image_path is not None and self.folder_path is not None:
            temp_path: str = os.path.split(self.image_path)[-1]
            if temp_path != self.file_list[0]:
                index: int = self.file_list.index(temp_path)
                self.image_path: str = os.path.join(self.folder_path, self.file_list[index - 1])
                self.open_image()
                self.crop_image()

    def display_image(self, image, canvas) -> None:
        """Display the image on the canvas while maintaining aspect ratio."""
        canvas.delete("all")  # Clear the canvas before displaying a new image

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Calculate the scaled dimensions to fit the canvas
        image_height, image_width = image.shape[:2]
        scale = min(canvas_width / image_width, canvas_height / image_height)
        new_width: int = int(image_width * scale)
        new_height: int = int(image_height * scale)

        # Resize the image using OpenCV
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Convert the OpenCV image to a Tkinter-compatible format
        photo = ImageTk.PhotoImage(image=Image.fromarray(resized))
        canvas.image = photo
        # Center the image on the canvas
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2
        canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo)

    def on_window_resize(self, event) -> None:
        """Handle window resize event with a delay to prevent excessive calls."""
        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
        self.resize_after_id = self.root.after(300, self.resize_images)

    def resize_images(self) -> None:
        """Resizes and updates displayed images."""
        if self.original_image is not None:
            self.display_image(self.original_image, self.original_canvas)
        if self.binary_image is not None:
            self.display_image(self.binary_image, self.processed_canvas)

    def update_crop_all_fraction(self, value) -> None:
        all_value = self.crop_all_fraction.get()
        self.crop_top_fraction.set(all_value)
        self.crop_left_fraction.set(all_value)
        self.crop_right_fraction.set(all_value)
        self.crop_bottom_fraction.set(all_value)
        
        if self.original_image is not None:
            self.crop_image()

    def update_crop_fraction(self, value) -> None:
        self.crop_all_fraction.set(0.0)
        if self.original_image is not None:
            self.crop_image()

    def crop_image(self) -> None:
        if self.binary_image is not None:
            self.binary_image = self.original_image
            height, width = self.original_image.shape[:2]
            left: int = int(width * self.crop_left_fraction.get())
            top: int = int(height * self.crop_top_fraction.get())
            right: int = int(width * (1 - self.crop_right_fraction.get()))
            bottom: int = int(height * (1 - self.crop_bottom_fraction.get()))
            self.binary_image = self.binary_image[top:bottom, left:right]
            self.display_image(self.binary_image, self.processed_canvas)

    def binarize_image(self) -> None:
        if self.binary_image is not None:
            self.preprocessor = OCRpreprocessor(self.binary_image)
            self.preprocessor.process()
            self.binary_image = self.preprocessor.binary
            self.display_image(self.binary_image, self.processed_canvas)

    def perform_ocr(self) -> None:
        if self.binary_image is None:
            messagebox.showwarning("No Image", "Please process an image first.")
            return
        self.ocr_button.config(state='disabled')

        # Perform OCR using pytesseract
        custom_config: str = f'--oem 3 --psm {self.selected_config.get()}'
        ocr_text: str = pytesseract.image_to_string(self.binary_image, lang=self.language, config=custom_config)
        self.ocr_button.config(state='normal')
        self.show_ocr_result(ocr_text)

    def show_ocr_result(self, ocr_text) -> None:
        if ocr_text is None:
            return

        # Create a new window to display the OCR text
        ocr_window = tk.Toplevel(self.root)
        ocr_window.title(os.path.split(self.image_path)[-1])

        # Create a text widget to display the OCR text
        text_widget = tk.Text(ocr_window, wrap=tk.WORD)
        text_widget.insert(tk.END, ocr_text)
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Add buttons for saving as TXT, PDF, or ALTO XML
        button_frame = ttk.Frame(ocr_window)
        button_frame.pack(pady=10)

        txt_button = ttk.Button(button_frame, text="Save as .txt", command=lambda: self.save_as_txt(ocr_text))
        txt_button.pack(side=tk.LEFT, padx=5)

        json_button = ttk.Button(button_frame, text='Save as JSON', command=lambda: self.save_as_json(ocr_text))
        json_button.pack(side=tk.RIGHT, padx=5)
    
    def show_psm(self) -> None:
        psm_options: str = """
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

    def save_as_txt(self, text: str) -> None:
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
        
    def save_as_json(self, text: str) -> None:
        if text is None:
            return
        
        page_dict = {
            'file_name': os.path.split(self.image_path)[-1],
            'date': str(datetime.now()),
            'text': text
        }

        page_object = json.dumps(page_dict, indent=4)
        filepath = filedialog.asksaveasfilename(
            title='Save as JSON',
            defaultextension='.json',
            filetypes=(('JSON files', '*.json'), ('All files', '*.*'))
        )

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(page_object)
            messagebox.showinfo('Succes', f'Text saved to {filepath}')

    def make_pdf(self) -> None:
        if self.binary_image is None:
            messagebox.showwarning("No Image", "Please process an image first.")
            return

        # Perform OCR using pytesseract with the custom config
        custom_config: str = f'--oem 3 --psm {self.selected_config.get()}'
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

    def save_image(self) -> None:
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

    def get_grayscale(self) -> None:
        self.gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        return self
    
    def remove_noise(self) -> None:
        if self.gray is None:
            self.gray = self.get_grayscale()
        self.gray = cv2.GaussianBlur(self.gray, (1,1), 0)
        return self
    
    def binarize(self) -> None:
        if self.gray is None:
            self.gray = self.get_grayscale()

        _, otsu = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.binary = otsu
        return self

    def dilate(self) -> None:
        """Dilate the image to connect text components"""
        if self.binary is None:
            self.binarize()
            
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        self.binary = cv2.dilate(self.binary, kernel, iterations=1)
        return self

    def erode(self) -> None:
        """Erode the image to remove small noise"""
        if self.binary is None:
            self.binarize()
            
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        self.binary = cv2.erode(self.binary, kernel, iterations=1)
        return self
    
    def process(self) -> None:
        return (self.get_grayscale()
                .remove_noise()
                .binarize()
                .dilate()
                .erode())


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()