import sys
import pickle
import numpy as np
import tkinter as tk
from operator import xor
from functools import reduce
from PIL import Image, ImageDraw
from scipy.ndimage import center_of_mass

# name
memofile = 'variables_and_memories.binaryfile'
outfile = 'out.png'

# size
window_width, window_height = 300, 300
canvas_width, canvas_height = 280, 280
button_width, button_height = 5, 1
image_width, image_height = 28, 28
normalized_size = 20
threshold = 128
BAR_SPACE = 3
BAR_WIDTH = 30

# color depth
draw_depth = int(90 / 100 * 255)  # 90%

# load memories data
with open(memofile, 'rb') as f:
    variables, memories = pickle.load(f)
realizations = len(variables) // 45

# pick necessary variables up
def reduce_vector(vector, variable):
    vector = ''.join(str(reduce(xor, [vector[x] for x in y])) for y in variable)
    return int(vector, 2)

class Demo():

    def __init__(self):
        self.window = self.create_window()
        # set canvas
        self.image = Image.new('L', (window_width, window_height))
        self.draw = ImageDraw.Draw(self.image)

    def create_window(self):
        window = tk.Tk()
        window.title('demo')

        # canvas frame
        canvas_frame = tk.LabelFrame(
            window, bg='white',
            text='canvas',
            width=window_width, height=window_height,
            relief='groove', borderwidth=4
        )
        canvas_frame.pack(side=tk.LEFT)
        self.canvas = tk.Canvas(canvas_frame, bg='white',
                                width=canvas_width, height=canvas_height,
                                relief='groove', borderwidth=4)
        self.canvas.pack()
        quit_button = tk.Button(canvas_frame, text='exit',
                                command=window.quit)
        quit_button.pack(side=tk.RIGHT)
        judge_button = tk.Button(canvas_frame, text='judge',
                                 width=button_width, height=button_height,
                                 command=self.judge)
        judge_button.pack(side=tk.LEFT)
        clear_button = tk.Button(canvas_frame, text='clear',
                                 command=self.clear)
        clear_button.pack(side=tk.LEFT)
        self.canvas.bind('<ButtonPress-1>', self.on_pressed)
        self.canvas.bind('<B1-Motion>', self.on_dragged)

        # result frame
        result_frame = tk.LabelFrame(window, bg='white', text='result',
                                     width=window_width, height=window_height,
                                     relief='groove', borderwidth=4)
        result_frame.pack(side=tk.RIGHT)
        self.result = tk.Canvas(result_frame, bg='white',
                                width=window_width, height=window_height)
        self.result.pack()

        return window

    def on_pressed(self, event):
        self.sx, self.sy = event.x, event.y

    def on_dragged(self, event):
        # draw surface canvas
        self.canvas.create_line(self.sx, self.sy, event.x, event.y,
                                width=5, tag='draw')
        self.draw.line(((self.sx, self.sy), (event.x, event.y)),
                       draw_depth, int(window_width / 20 * 3))

        # store the position in the buffer
        self.sx, self.sy = event.x, event.y

    def judge(self):
        # save png
        # self.image.save(outfile)
        # convert to values
        im = Image.new('L', (image_width, image_height))

        # normalize
        im.paste(self.image.resize((normalized_size, normalized_size)), (4, 4))

        # translate the image so as to position center of mass at the center
        y_center, x_center = center_of_mass(np.array(im))
        y_move, x_move = y_center - image_height // 2, x_center - image_width // 2
        im = im.transform((image_width, image_height), Image.AFFINE, (1, 0, x_move, 0, 1, y_move))

        # binarize
        vector = [1 if x >= threshold else 0 for x in im.getdata()]

        # output the binarized image
        for i in range(image_height):
            print(''.join(map(str, vector[i * image_width:(i + 1) * image_width])))
        print()

        # judge
        popcounts = [0] * 10
        for i in range(10):
            for j in range(i + 1, 10):
                for k in range(1, realizations + 1):
                    variable = variables[i, j, k]
                    memory = memories[i, j, k]
                    new_vector = reduce_vector(vector, variable)
                    if new_vector in memory:
                        if memory[new_vector] == 0:
                            popcounts[i] += 1
                        elif memory[new_vector] == 1:
                            popcounts[j] += 1
        max_value = max(popcounts)

        # show the result
        self.result.delete('result')  # clear the previous data

        for i in range(10):
            fill = 'red' if popcounts[i] == max_value else None
            # show the bar
            self.result.create_rectangle(
                30, i * BAR_WIDTH + BAR_SPACE,
                30 + (window_width - 60) * popcounts[i] / 9 / realizations,
                (i + 1) * BAR_WIDTH, tag='result', fill=fill
            )
            # show the number
            self.result.create_text(
                15, i * BAR_WIDTH + BAR_SPACE + BAR_WIDTH / 2,
                text=str(i), tag='result', fill=fill
            )
            # show the recognition rate
            self.result.create_text(
                window_width - 15,
                i * BAR_WIDTH + BAR_SPACE + BAR_WIDTH / 2,
                text=f'{popcounts[i] / 9 / realizations:.1%}', tag='result',
                fill=fill
            )

    def clear(self):
        # clear the canvas
        self.canvas.delete('draw')
        self.image = Image.new('L', (window_width, window_height))
        self.draw = ImageDraw.Draw(self.image)

        # clear the result
        self.result.delete('result')

    def run(self):
        self.window.mainloop()

def main():
    Demo().run()

if __name__ == '__main__':
    main()
