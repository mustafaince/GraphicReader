import cv2
import numpy as np
import pytesseract
from tkinter import *
from PIL import ImageTk, Image

pytesseract.pytesseract.tesseract_cmd= r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

root=Tk()
root.title("GraphicReader")

global headerLabel
global requestLabel
global inputReceiver
global output_label
global state
global result_Str

headerLabel = Label(root,text="Image Captioning For Graphics").grid(row=0, column=0, columnspan=3)

requestLabel = Label(root,text="Enter the path:").grid(row=1, column=0, columnspan=3)

inputReceiver = Entry(root,width=35, borderwidth=5)
inputReceiver.grid(row=2, column=0, columnspan=3)

output_label = Label(root, text="RESULT")
output_label.grid(row=6, column=0, columnspan=3)

def isThereThisColor(pixel, colors):
    for i in range(len(colors)):
        if np.array_equal(pixel, colors[i]):
            return 1
    return 0

def isThisBarChart(x, y, chart):
    pixel= chart[x, y]
    for i in range(30):
        x= x+1
        if np.array_equal(pixel, chart[x, y])== 0:
            return 0
    return 1

def findLastBarColumnValue(locations):
    column= -1
    for i in range(len(locations)):
        if locations[i, 1] > column:
            column= locations[i, 1]
    return column

def findTextOfColors(lastBarColumnValue, colors, chart):
    newImg= chart[:, lastBarColumnValue+80: ]
    controlColor= [0, 0, 0]
    x, y, _ = newImg.shape
    textImg=0
    texts=[]

    for color in colors:
        for i in range(x):
            for j in range(y):
                if np.array_equal(color, newImg[i, j])== 1 and np.array_equal(controlColor, newImg[i, j])!= 1:
                    controlColor= newImg[i, j]
                    textImg = newImg[i-5:i+35, j+25:]
                    text = pytesseract.image_to_string(textImg)
                    texts.append(text)
                    break
    return texts

def findValueOfBars(chart, locations):
    yAxisOfChart= 0
    numbers=[]
    x = locations[0, 0]
    y = locations[0, 1]
    while True:
        y= y-1
        if np.array_equal(chart[x, y], [0,0,0])== 1:
            yAxisOfChart= y
            break
    for i in locations:
        a= i[0]

        textImg = chart[a - 18:a + 15, :y-8]
        value = pytesseract.image_to_string(textImg)
        numbers.append(value)
    return numbers

def center():
    image_to_resize = Image.open(inputReceiver.get())
    new_image = image_to_resize.resize((600, 388)) ## The (250, 250) is (column, row)

    img = ImageTk.PhotoImage(new_image)
    img_label = Label(image=img)
    img_label.image = img
    img_label.grid(row=7, column=0, columnspan=3)

    state ="Show"
    colors = np.array([[0, 0, 0], [255, 255, 255]], dtype=np.int64)
    chart = cv2.imread(inputReceiver.get())

    locations = np.array([[1, 1]], dtype=np.int)
    x, y, _ = chart.shape

    for i in range(x):
        for j in range(y):
            if isThereThisColor(chart[i, j], colors)== 0:
                if(isThisBarChart(i, j, chart))== 1:
                    colors = np.append(colors, [chart[i, j]], axis=0) #in this array, color of every bar chart is stored
                    locations = np.append(locations, [[i, j]], axis=0) # in this array, location of every bar chart starting pixel is stored

    colors = np.delete(colors, 0, 0)
    colors = np.delete(colors, 0, 0)
    locations = np.delete(locations, 0, 0)

    lastBarColumnValue= findLastBarColumnValue(locations)
    texts= findTextOfColors(lastBarColumnValue, colors, chart)
    values= findValueOfBars(chart, locations)

    result_Str =''
    for i in range(len(texts)):
        result_Str = result_Str + str(texts[i]) + " " +str(values[i]) + "\r"
    output_label.configure(text=result_Str)

button_analyze = Button(root,text="Analyze The Picture",bg="blue",fg="white",command = center).grid(row=5, column=0, columnspan=3)

button_quit = Button(root, text="Exit Program", command = root.quit)
button_quit.grid(row=8, column=0, columnspan=3)

root.mainloop()