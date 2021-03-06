from tkinter import *
import threading
import time
import DrawingPlot
from json import dumps, load


class Alert:
	def __init__(self, text, is_error, stay_time=5):
		self.move = 0
		self.moveAmount = padY / 2 + 1
		self.stayTime = stay_time

		if is_error:
			color = "#9d1c1c"
		else:
			color = "#43b581"

		self.errorBG = background.create_rectangle(0, mainHeight - 1, mainWidth - 1, mainHeight + padY / 2, fill=color)
		self.errorText = background.create_text(mainWidth / 2, mainHeight + padY / 4 - 1, text=text, fill="white", font="SegoeUILight 11 bold")
		self.error_in()

	def error_in(self):
		if self.move < self.moveAmount:
			background.after(4, self.error_in)
			background.move(self.errorBG, 0, -1)
			background.move(self.errorText, 0, -1)
		else:
			self.move = 0
			threading._start_new_thread(self.timer, ())
			return
		self.move += 1

	def timer(self):
		time.sleep(self.stayTime)
		self.error_out()
		return

	def error_out(self):
		if self.move < self.moveAmount:
			background.after(4, self.error_out)
			background.move(self.errorBG, 0, 1)
			background.move(self.errorText, 0, 1)
		else:
			background.delete(self.errorBG)
			background.delete(self.errorText)
			return
		self.move += 1


# Useful classes to easily create Tkinter widgets on a canvas
class CustomCheckbutton:
    def __init__(self, x, y, text, function, is_checked):
        self.isChecked = IntVar()
        self.checkbox = Checkbutton(background, text=text, bg="#36393e", activebackground="#36393e", bd=1,
                                    font="Neoteric 15", fg="#00ffff", activeforeground="#00ffff",
                                    selectcolor="#36393e", highlightbackground="#36393e", command=lambda: function(),
                                    variable=self.isChecked, disabledforeground="#808387"
                                    )
        background.create_window(x, y, window=self.checkbox, anchor=NW)

        if is_checked:
            self.checkbox.select()

    def uncheck(self):
        self.checkbox.deselect()

    def set_value(self, state):
        if not state:
            self.checkbox.deselect()
        else:
            self.checkbox.select()

    def set_state(self, state):
        if state == "disabled":
            self.checkbox.config(state=DISABLED)
        elif state == "normal":
            self.checkbox.config(state=NORMAL)
        else:
            print("Improper state provided")


class CustomEntry:
    def __init__(self, x, y, name, state=True, default_text="", char_width=10, distance=160):
        self.name = name + ":"
        self.text = background.create_text(x, y - 3, text=self.name, font="Neoteric 15", fill="#00ffff", anchor=NW)

        self.entry = Entry(background, bg="#2f3136", fg="#00ffff", insertbackground="white", insertborderwidth=1,
                           disabledbackground="#25262b", disabledforeground="#808387", highlightthickness=0,
                           width=char_width, textvariable=StringVar(root, default_text), justify='center'
                           )

        background.create_window(x + distance, y, window=self.entry, anchor=NW)

        if not state:
            self.set_state("disabled")

    def get_value(self):
        return self.entry.get()

    def set_value(self, text):
        self.entry.delete(0, END)
        self.entry.insert(0, text)

    def set_state(self, state):
        if state == "disabled":
            self.entry.config(state=DISABLED, relief=FLAT)
            background.itemconfig(self.text, fill="#808387")
        elif state == "normal":
            self.entry.config(state=NORMAL, relief=SUNKEN)
            background.itemconfig(self.text, fill="#00ffff")
        else:
            print("Improper state provided")


class CustomButton:
    color = "#ffffff"

    def __init__(self, x, y, size_x, size_y, text, color, text_color, font, function):
        self.color = color

        # Create button graphic
        self.buttonBG = background.create_rectangle(x, y, x + size_x, y + size_y, fill=color)
        self.buttonText = background.create_text(x + size_x / 2, y + size_y / 2, text=text, fill=text_color, font=font)

        # Button Events
        background.tag_bind(self.buttonBG, "<Button-1>", self.button_anims)
        background.tag_bind(self.buttonText, "<Button-1>", self.button_anims)
        background.tag_bind(self.buttonBG, "<Enter>", self.button_anims)
        background.tag_bind(self.buttonText, "<Enter>", self.button_anims)
        background.tag_bind(self.buttonBG, "<Leave>", self.button_anims)
        background.tag_bind(self.buttonText, "<Leave>", self.button_anims)
        background.tag_bind(self.buttonBG, "<ButtonRelease-1>", self.button_anims)
        background.tag_bind(self.buttonText, "<ButtonRelease-1>", self.button_anims)

        background.tag_bind(self.buttonBG, "<Button-1>", lambda func: function())
        background.tag_bind(self.buttonText, "<Button-1>", lambda func: function())

    def button_anims(self, event):
        if event.type == EventType.Enter:
            background.itemconfig(self.buttonBG, fill="#202225")
        elif event.type == EventType.Leave:
            background.itemconfig(self.buttonBG, fill=self.color)
        elif event.type == EventType.ButtonPress:
            background.itemconfig(self.buttonBG, fill=self.color)
        elif event.type == EventType.ButtonRelease:
            background.itemconfig(self.buttonBG, fill="#202225")


class CustomSlider:
    def __init__(self, x, y, name, from_=0, to=100, distance=140, orient=HORIZONTAL):

        self.name = name + ":"
        self.text = background.create_text(x, y + 5, text=self.name, font="Neoteric 15", fill="#00ffff", anchor=NW)
        self.scale = Scale(background, from_=from_, to=to, orient=orient, bg="#2f3136", fg="#00ffff",
                           highlightthickness=0, sliderlength=15)

        background.create_window(x + distance, y, window=self.scale, anchor=NW)

    def get_value(self):
        return self.scale.get()


# Holds all classes and widgets specifically created for the Block section of the generator
class Program:
    def __init__(self):
        # Properties #
        self.graphSizeInt = 0
        self.amplitudeMinInt = 0
        self.amplitudeMaxInt = 0
        self.amplitudeLerpSpeedInt = 0
        self.xSquishInt = 0
        self.ySquishInt = 0
        self.bezierCurveVisibilityBool = False
        self.moveSpeedInt = 0
        self.bezierStepsFloat = 0
        self.invertColorBool = False
        self.constantIncreaseBool = False
        self.animateBool = False
        self.frequencyFloat = 0

        self.drawing_plot = None

        # Seperators and borders #
        background.create_rectangle(padX, padY, padX + length, padY + 550, fill="#36393e", width=1)

        # Text #
        self.amplitudeMinText = CustomEntry(padX + 40, padY + 42, "Amp Min", True, "1")
        self.amplitudeMaxText = CustomEntry(padX + 40, padY + 75, "Amp Max", True, "10")
        self.frequency = CustomEntry(padX + 40, padY + 105, "Frequency", True, "1000")
        self.amplitudeLerpSpeed = CustomEntry(padX + 40, padY + 135, "Growth Speed", True, "1000")
        self.xSquish = CustomEntry(padX + 40, padY + 250, "X Eccentric", True, "1")
        self.ySquish = CustomEntry(padX + 40, padY + 285, "Y Eccentric", True, "1")
        self.graphSize = CustomEntry(padX + 40, padY + 320, "Graph Size", True, "10")

        # Checkboxes #
        self.bezierCurveVisibility = CustomCheckbutton(padX + 330, padY + 2, "Bezier Visibility", self.pass_func, True)
        self.invertColor = CustomCheckbutton(padX + 600, padY + 2, "Invert Color", self.pass_func, True)
        self.constantIncrease = CustomCheckbutton(padX + 40, padY + 170, "Increase Constantly?", self.constant_increase_func, False)
        self.isDrawingInstant = CustomCheckbutton(padX + 40, padY + 200, "Draw Instant?", self.pass_func, False)

        # Buttons #
        self.clearPoints = CustomButton(padX + 50, padY + 365, 200, 75, "CLEAR", "#9d1c1c", "#ffffff", "Neoteric 30", self.reset_points)
        self.start = CustomButton(padX + 50, padY + 445, 200, 75, "START", "#50c878", "#ffffff", "Neoteric 30", self.start)

        self.load()

    @staticmethod
    def reset_points():
        global bezier_plot
        bezier_plot.reset_plot()

    def pass_func(self):
        pass

    def constant_increase_func(self):
        if self.constantIncrease.isChecked.get():
            self.amplitudeMaxText.set_state("disabled")
        else:
            self.amplitudeMaxText.set_state("normal")

    def set_values(self):
        self.graphSizeInt = int(self.graphSize.get_value())
        self.amplitudeMinInt = float(self.amplitudeMinText.get_value())
        self.amplitudeMaxInt = float(self.amplitudeMaxText.get_value())
        self.amplitudeLerpSpeedInt = float(self.amplitudeLerpSpeed.get_value())
        self.xSquishInt = int(self.xSquish.get_value())
        self.ySquishInt = int(self.ySquish.get_value())
        self.bezierCurveVisibilityBool = bool(self.bezierCurveVisibility.isChecked.get())
        self.invertColorBool = bool(self.invertColor.isChecked.get())
        self.constantIncreaseBool = bool(self.constantIncrease.isChecked.get())
        self.animateBool = bool(self.isDrawingInstant.isChecked.get())
        self.frequencyFloat = float(self.frequency.get_value())

    def save(self):
        self.set_values()

        config = \
            {
                "size": self.graphSizeInt,
                "amp_min": self.amplitudeMinInt,
                "amp_max": self.amplitudeMaxInt,
                "amp_lerp_speed": self.amplitudeLerpSpeedInt,
                "x_squish": self.xSquishInt,
                "y_squish": self.ySquishInt,
                "bezier_visibility": self.bezierCurveVisibilityBool,
                "move_speed": self.moveSpeedInt,
                "bezier_steps": self.bezierStepsFloat,
                "invert_color": self.invertColorBool,
                "constant_increase": self.constantIncreaseBool,
                "is_drawing_instant": self.animateBool,
                "frequency": self.frequencyFloat
            }

        with open("data/config.json", "w+") as f:
            f.write(dumps(config, indent=4))

        Alert("Saved successfully!", False, 1)

    def load(self):
        try:
            with open("data/config.json", "r+") as f:
                config = load(f)

                self.graphSize.set_value(config["size"])
                self.amplitudeMinText.set_value(config["amp_min"])
                self.amplitudeMaxText.set_value(config["amp_max"])
                self.amplitudeLerpSpeed.set_value(config["amp_lerp_speed"])
                self.xSquish.set_value(config["x_squish"])
                self.ySquish.set_value(config["y_squish"])
                self.bezierCurveVisibility.set_value(config["bezier_visibility"])
                self.invertColor.set_value(config["invert_color"])
                self.constantIncrease.set_value(config["constant_increase"])
                self.isDrawingInstant.set_value(config["is_drawing_instant"])
                self.frequency.set_value(config["frequency"])
        except FileNotFoundError:
            pass

        self.constant_increase_func()

    def start(self):
        self.save()
        self.set_values()

        if len(bezier_points) >= 2:
            with open("data/points.txt", "w+") as f:
                for point in bezier_points:
                    pos_x, pos_y = point.get_position()
                    coord = BezierPlot.get_coord(pos_x, pos_y)
                    f.write("{0},{1}\n".format(coord[0], coord[1]))

        self.drawing_plot = DrawingPlot.DrawingPlot(self.graphSizeInt,
                                                    self.amplitudeMinInt / 10,
                                                    self.amplitudeMaxInt / 10,
                                                    self.amplitudeLerpSpeedInt / 100,
                                                    self.xSquishInt,
                                                    self.ySquishInt,
                                                    self.bezierCurveVisibilityBool,
                                                    self.invertColorBool,
                                                    self.constantIncreaseBool,
                                                    self.animateBool,
                                                    self.frequencyFloat
                                                    )

        self.drawing_plot.main()


class BezierPoint:
    def __init__(self, master, mouse_x, mouse_y, point_number):
        self.master = master
        self.x_pos = mouse_x
        self.y_pos = mouse_y
        self.point_number = point_number

        self.tag = "bezier_point_" + str(self.point_number)

        self.number = background.create_text(mouse_x, mouse_y - 15, text=self.point_number, fill="white")
        self.marker = background.create_polygon(self.get_marker_coords(self.x_pos, self.y_pos), fill="cyan", tag=self.tag)

        self.bind_input()

    @staticmethod
    def get_marker_coords(x, y):
        return [x + 5, y, x, y + 5, x - 5, y, x, y - 5]

    def update_point(self, x, y):
        self.x_pos = x
        self.y_pos = y

    def delete_point(self, event):
        global bezier_points
        global bezier_plot

        background.delete(self.marker)
        background.delete(self.number)
        bezier_points.pop(self.point_number)
        bezier_plot.set_point_number(bezier_plot.get_point_number() - 1)

        for i in range(self.point_number, len(bezier_points)):
            bezier_points[i].unbind_input()
            bezier_points[i].set_point_number(bezier_points[i].get_point_number() - 1)
            bezier_points[i].bind_input()

    def bind_input(self):
        self.tag = "bezier_point_" + str(self.point_number)
        background.itemconfig(self.marker, tag=self.tag)

        background.tag_bind(self.tag, "<ButtonPress-1>", self.down)
        background.tag_bind(self.tag, "<ButtonRelease-1>", self.up)
        background.tag_bind(self.tag, "<ButtonPress-3>", self.delete_point)

    def unbind_input(self):
        self.tag = "bezier_point_" + str(self.point_number)
        background.itemconfig(self.marker, tag=self.tag)

        background.tag_unbind(self.tag, "<ButtonPress-1>")
        background.tag_unbind(self.tag, "<ButtonRelease-1>")
        background.tag_unbind(self.tag, "<ButtonPress-3>")

    def set_point_number(self, point_number):
        background.itemconfig(self.number, text=point_number)
        self.point_number = point_number

    def get_point_number(self):
        return self.point_number

    def down(self, event):
        event.widget.bind("<Motion>", self.motion)

    def motion(self, event):
        # Constrain marker to stay inside bezier plot
        if plot_pad_x < event.x < plot_pad_x + plot_width and plot_pad_y < event.y < plot_pad_y + plot_height:
            background.coords(self.marker, self.get_marker_coords(event.x, event.y))
            background.coords(self.number, [event.x, event.y - 15])

    def up(self, event):
        event.widget.unbind("<Motion>")
        self.update_point(event.x, event.y)

    def get_position(self):
        return self.x_pos, self.y_pos


class BezierPlot:
    def __init__(self, master):
        self.master = master
        self.point_number = 0

        self.point_objects = []

        background.create_rectangle(plot_pad_x, plot_pad_y, plot_pad_x + plot_width, plot_pad_y + plot_height, fill="#23272A", width=1, tags="bezierPlot")
        background.tag_bind("bezierPlot", "<ButtonPress-1>", self.place_point)

    def place_point(self, event):
        global bezier_points

        mouse_x = event.x
        mouse_y = event.y

        bezier_points.append(BezierPoint(self.master, mouse_x, mouse_y, self.point_number))
        self.point_number += 1

    def set_point_number(self, point_number):
        self.point_number = point_number

    def get_point_number(self):
        return self.point_number

    @staticmethod
    def get_coord(x, y):
        # Clamp between 0 and 21
        ratio = 21 / plot_width
        x = (x - plot_pad_x - 1) * ratio
        y = (y - plot_pad_y - 1) * ratio

        # Make 0;0 center instead of top left corner
        x = int(float((x - 10) / 10) * 20)
        y = -int(float((y - 10) / 10) * 20)

        return x, y

    def reset_plot(self):
        global bezier_points

        self.point_number = 0

        for obj in bezier_points:
            obj.remove_point()

        bezier_points.clear()


# Main Program
root = Tk()

height = 250
padX = 50
padY = 50
sizeY = str(padY*3 + height*2)
size = str(890)+"x"+sizeY

root.title("Drawing GUI")
root.geometry(size)
root.resizable(False, False)
root.update()

# Setup global static variables
mainWidth = root.winfo_width()
mainHeight = root.winfo_height()
length = mainWidth - padX*2

# Bezier Plot
plot_width = 450
plot_height = 450
plot_pad_y = padY + 50
plot_pad_x = padX + 300

# Create background
background = Canvas(root, width=mainWidth, height=mainHeight, highlightthickness=0, bg="#2f3136")
background.pack()
background.create_text(mainWidth / 2, padY / 2, text="THE DRAWING BOT", font="Neoteric 30", fill="#00ffff", anchor=CENTER)

# Create error bar
errorBG = background.create_rectangle(0, mainHeight - 1, mainWidth - 1, mainHeight + padY / 2, fill="#9d1c1c")
errorText = background.create_text(mainWidth / 2, mainHeight + padY / 4 - 1, text="Invalid directory selected!", fill="white", font="Neoteric 11 bold")

# Global vars
bezier_points = []

# Load Separate GUIs
Program()
bezier_plot = BezierPlot(root)

root.mainloop()
