import requests
from tkinter import Tk, Label, Button, Entry, filedialog, Canvas, Frame, OptionMenu, StringVar
from PIL import Image, ImageTk
from io import BytesIO
import os

def select_image():
    """选择图片并显示在左侧区域"""
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
    )
    if not file_path:
        return  # 如果未选择文件，直接返回

    image_path_entry.delete(0, "end")
    image_path_entry.insert(0, file_path)

    # 显示原图
    display_image(file_path, canvas_left)

def display_image(file_path, canvas):
    """在指定 Canvas 上显示图片"""
    image = Image.open(file_path)
    image.thumbnail((300, 300))  # 调整图片大小
    photo = ImageTk.PhotoImage(image)
    canvas.image = photo  # 保存引用，避免被垃圾回收
    canvas.create_image(150, 150, image=photo)

def remove_background():
    """调用 Remove.bg API 来去除背景并显示处理后的图片"""
    api_key = api_key_entry.get()  # 获取用户输入的 API Key
    if not api_key:
        result_label.config(text="请输入 API Key！")
        return

    file_path = image_path_entry.get()
    if not file_path:
        result_label.config(text="请先选择图片！")
        return

    try:
        # 发送请求到 Remove.bg API
        with open(file_path, "rb") as image_file:
            response = requests.post(
                "https://api.remove.bg/v1.0/removebg",
                files={"image_file": image_file},
                data={"size": "auto"},
                headers={"X-Api-Key": api_key},
            )

        if response.status_code == requests.codes.ok:
            # 处理成功，显示处理后的图片
            image_data = response.content
            result_image = Image.open(BytesIO(image_data))

            # 获取背景颜色
            bg_color = background_var.get()

            if bg_color == "红色":
                result_image = add_background_color(result_image, (255, 0, 0))
            elif bg_color == "蓝色":
                result_image = add_background_color(result_image, (0, 0, 255))
            elif bg_color == "白色":
                result_image = add_background_color(result_image, (255, 255, 255))
            elif bg_color == "蓝色渐变":
                result_image = add_gradient_background(result_image)

            result_image.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(result_image)

            canvas_right.image = photo  # 保存引用
            canvas_right.create_image(150, 150, image=photo)

            # 保存处理后的图片数据
            canvas_right.image_data = result_image

            # 显示保存按钮
            save_button.pack()
            result_label.config(text="背景替换成功！")
        else:
            result_label.config(text=f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        result_label.config(text=f"Error: {str(e)}")

def add_background_color(image, color):
    """为图片添加背景颜色"""
    width, height = image.size
    new_image = Image.new("RGBA", (width, height), color)
    new_image.paste(image, (0, 0), image)
    return new_image

def add_gradient_background(image):
    """为图片添加蓝色渐变背景"""
    width, height = image.size
    new_image = Image.new("RGBA", (width, height))
    for y in range(height):
        for x in range(width):
            new_image.putpixel((x, y), (0, 0, int(255 * (y / height)), 255))
    new_image.paste(image, (0, 0), image)
    return new_image

def save_result():
    """保存处理后的图片"""
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png", filetypes=[("PNG Files", "*.png")]
    )
    if save_path:
        canvas_right.image_data.save(save_path)
        result_label.config(text="图片已保存！")

# 创建 GUI 界面
root = Tk()
root.title("证件照背景替换工具")
root.geometry("800x670")

# 顶部标题栏
header_frame = Frame(root)
header_frame.pack(pady=10)

Label(header_frame, text="证件照背景替换工具", font=("Arial", 20, "bold")).pack()

# API Key 输入框
api_key_frame = Frame(root)
api_key_frame.pack(pady=10)

Label(api_key_frame, text="API Key:").grid(row=0, column=0, padx=10, pady=5)
api_key_entry = Entry(api_key_frame, width=50)
api_key_entry.grid(row=0, column=1, padx=10, pady=5)

# 图片路径输入栏
image_path_frame = Frame(root)
image_path_frame.pack(pady=10)

Label(image_path_frame, text="图片路径:").grid(row=0, column=0, padx=10, pady=5)
image_path_entry = Entry(image_path_frame, width=50)
image_path_entry.grid(row=0, column=1, padx=10, pady=5)
Button(image_path_frame, text="选择图片", command=select_image).grid(row=0, column=2, padx=10)

# 左右两侧图片展示区域
canvas_frame = Frame(root)
canvas_frame.pack(pady=10)

canvas_left = Canvas(canvas_frame, width=300, height=300, bg="gray")
canvas_left.grid(row=0, column=0, padx=20, pady=10)

canvas_right = Canvas(canvas_frame, width=300, height=300, bg="gray")
canvas_right.grid(row=0, column=1, padx=20, pady=10)

# 背景颜色选择
color_frame = Frame(root)
color_frame.pack(pady=20)

background_var = StringVar(root)
background_var.set("透明")  # 默认选项

background_options = ["透明", "红色", "蓝色", "白色", "蓝色渐变"]
background_menu = OptionMenu(color_frame, background_var, *background_options)
background_menu.grid(row=0, column=0, padx=10)

Button(color_frame, text="替换背景", command=remove_background).grid(row=0, column=1, padx=10)

# 结果状态提示
result_label = Label(root, text="", fg="green", font=("Arial", 12))
result_label.pack(pady=10)

# 保存结果按钮
save_button = Button(root, text="保存结果", command=save_result)
save_button.pack_forget()  # 初始隐藏保存按钮

# 运行 GUI 主循环
root.mainloop()