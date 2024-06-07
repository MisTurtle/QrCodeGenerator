import qrcode
from tkinter import *
from tkinter import ttk, colorchooser, filedialog
from PIL import Image, ImageTk
from os.path import exists


class ColorInput:

    def __init__(self, _short: str, _long: str, _display: Canvas, _value: tuple[tuple[int, int, int], str]):
        self.short_name = _short
        self.long_name = _long
        self.display = _display
        self.value = _value


qr_code_values: dict = {}


# Data to be encoded
def generate_qr_code():
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H if has_logo_var.get() else qrcode.constants.ERROR_CORRECT_L,  # High error correction
        box_size=10,
        border=1,
    )
    qr.add_data(qr_code_values.get('data').get())
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color=qr_code_values.get('fg').value[0], back_color=qr_code_values.get('bg').value[0])

    if has_logo_var.get() and exists(logo_path_var.get()) and logo_size_var.get() > 0:
        # Load the logo and resize it
        logo = Image.open(logo_path_var.get()).convert("RGBA")
        basewidth = int(logo_size_var.get() * img.size[0])
        wpercent = (basewidth / float(logo.size[0]))
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.LANCZOS)

        # Calculate logo position (center of the QR code)
        img = img.convert("RGB")
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)

        # Paste the logo onto the QR code
        img.paste(logo, pos, mask=logo)

    success_label.grid_remove()
    return img


def open_color_picker(_short: str):
    global qr_code_values
    ci: ColorInput = qr_code_values.get(_short, None)
    if ci is None:
        raise ValueError("Invalid Color Code : %s" % _short)
    value: tuple[tuple[int, int, int] | tuple[int, int, int, int], str] | tuple[None, None] = colorchooser.askcolor(title="Choose %s Color" % ci.long_name.title(), initialcolor=ci.value[1])
    if None in value:
        return
    ci.value = value
    ci.display.config(background=value[1])
    refresh_code()


def add_color_field(_short: str, _long: str, _default: tuple[tuple[int, int, int] | tuple[int, int, int, int], str], _row_id: int):
    ttk.Label(frame, text="%s Color" % _long.title()).grid(column=0, row=_row_id)
    ttk.Button(frame, text="Change...", command=lambda: open_color_picker(_short)).grid(column=1, row=row_id)
    fg_display = Canvas(frame, width=10, height=10, highlightbackground="black", highlightcolor="black",
                        background=_default[1])
    fg_display.grid(column=2, row=row_id)

    qr_code_values[_short] = ColorInput(_short, _long, fg_display, _default)


def open_existing_file(extensions: list[tuple[str, str]], default: str):
    return filedialog.askopenfilename(filetypes=extensions, initialdir=default)


def save_file(extensions: list[tuple[str, str]], default: str):
    return filedialog.asksaveasfile(filetypes=extensions, initialdir=default)


def toggle_logo_section():
    state = "enabled" if has_logo_var.get() else "disabled"
    for el in logo_path_elems:
        el.config(state=state)


def refresh_code(*args):
    pil_img = generate_qr_code()
    tk_img = ImageTk.PhotoImage(pil_img)

    qr_display.config(image=tk_img, width=tk_img.width(), height=tk_img.height())
    qr_display.image = tk_img


def export():
    path = save_file([('Image', '.png .jpg')], logo_path_var.get())
    if path is None:
        return
    generate_qr_code().save(path.name)
    success_label.grid()


variables = []
root = Tk()

root.title("Quick Projects - QR Code Generator")
frame = ttk.Frame(root, padding=10, width=520, height=520)
frame.grid()
frame.anchor('w')

# QR Code Data
row_id = 0
data_var = StringVar(root, value="Sample Data")

ttk.Label(frame, text="QR Code Text Data", anchor="center").grid(column=0, row=row_id)
ttk.Entry(frame, textvariable=data_var).grid(column=1, row=row_id, columnspan=2)

variables.append(data_var)
qr_code_values['data'] = data_var

# Foreground Color
row_id = 1
add_color_field("fg", "foreground", ((0, 0, 0), "#000000"), row_id)

# Background Color
row_id = 2
add_color_field("bg", "background", ((255, 255, 255, 0), "#ffffff"), row_id)

# Logo Checkbox
row_id = 3
has_logo_var = BooleanVar(frame, False)
ttk.Checkbutton(frame, text="Add Logo", onvalue=True, offvalue=False, variable=has_logo_var, command=toggle_logo_section).grid(column=0, row=row_id)
variables.append(has_logo_var)

# Logo Path
row_id = 4
logo_path_var = StringVar()
logo_path_elems = []
ttk.Label(frame, text="Logo Path", anchor='w').grid(column=0, row=row_id)

logo_path_input = ttk.Entry(frame, textvariable=logo_path_var, state='disabled')
logo_path_input.grid(column=1, row=row_id)
logo_path_elems.append(logo_path_input)

logo_path_change = ttk.Button(frame, text="Change...", command=lambda: qr_code_values['logo_path'].set(open_existing_file([("Image", ".png .jpg")], logo_path_var.get())), state='disabled')
logo_path_change.grid(column=2, row=row_id)
logo_path_elems.append(logo_path_change)

qr_code_values['logo_path'] = logo_path_var
variables.append(logo_path_var)

# Logo Size
row_id = 5
logo_size_var = DoubleVar(frame, 0)
logo_size_display = StringVar(frame, "0% width")
ttk.Label(frame, text="Logo Size").grid(row=row_id, column=0)

logo_size_change = ttk.Scale(frame, variable=logo_size_var, command=lambda x: logo_size_display.set("%d%% width" % (logo_size_var.get() * 100)))
logo_size_change.grid(row=row_id, column=1)
logo_path_elems.append(logo_size_change)

ttk.Label(frame, textvariable=logo_size_display).grid(row=row_id, column=2)

qr_code_values['logo_size'] = logo_size_var
variables.append(logo_size_var)

# Qr Code Display
row_spawn, row_id = row_id + 1, 0

qr_display = Label(root)
qr_display.grid()

for variable in variables:
    variable.trace_add('write', refresh_code)


# Export Button
row_id = 7
ttk.Button(frame, text="Export QR Code", command=export, padding=[10, 10, 10, 10]).grid(row=row_id, columnspan=3)


# Success Label
row_id = 8
success_label = ttk.Label(frame, text="Successfully Exported !", foreground="#00CC00")
success_label.grid(row=row_id, columnspan=3)

toggle_logo_section()
refresh_code()
root.mainloop()
