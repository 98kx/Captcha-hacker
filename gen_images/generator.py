# coding:utf-8
import functools
import os
import random

from PIL import Image, ImageDraw, ImageFont

"""
基本：
1 图片size
2 字符个数
3 字符区域（重叠、等分）
4 字符位置（固定、随机）
5 字符size（所占区域大小的百分比）
6 字符fonts
7 字符 type （数字、字母、汉字、数学符号）
8 字符颜色
9 背景颜色

高级：
10 字符旋转
11 字符扭曲
12 噪音（点、线段、圈）
"""


def randRGB():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def cha_draw(cha, text_color, font, rotate, size_cha):
    im = Image.new(mode='RGBA', size=(size_cha * 2, size_cha * 2))
    drawer = ImageDraw.Draw(im)
    drawer.text(xy=(0, 0), text=cha, fill=text_color, font=font)  # text 内容，fill 颜色， font 字体（包括大小）
    if rotate:
        max_angle = 60  # to be tuned
        angle = random.randint(-max_angle, max_angle)
        im = im.rotate(angle, Image.BILINEAR, expand=1)
    im = im.crop(im.getbbox())
    return im


def captcha_draw(size_im, nb_cha, set_cha, fonts=None, overlap=0.0,
                 rd_bg_color=False, rd_text_color=False, rd_text_pos=False, rd_text_size=False,
                 rotate=False, noise=None, dir_path=''):
    """
        overlap: 字符之间区域可重叠百分比, 重叠效果和图片宽度字符宽度有关
        字体大小 目前长宽认为一致！！！
        所有字大小一致
        扭曲暂未实现
        noise 可选：point, line , circle
        fonts 中分中文和英文字体
        label全保存在label.txt 中，文件第i行对应"i.jpg"的图片标签，i从1开始
    """
    rate_cha = 0.8  # rate to be tuned
    width_im, height_im = size_im
    width_cha = int(width_im / max(nb_cha - overlap, 1))  # 字符区域宽度
    height_cha = height_im  # 字符区域高度
    bg_color = 'white'
    text_color = 'black'
    derx = 0
    dery = 0

    if rd_text_size:
        rate_cha = random.uniform(rate_cha - 0.1, rate_cha + 0.1)  # to be tuned
    size_cha = int(rate_cha * min(width_cha, height_cha))  # 字符大小

    if rd_bg_color:
        bg_color = randRGB()
    im = Image.new(mode='RGB', size=size_im, color=bg_color)  # color 背景颜色，size 图片大小

    drawer = ImageDraw.Draw(im)
    contents = []
    for i in range(nb_cha):
        if rd_text_color:
            text_color = randRGB()
        if rd_text_pos:
            derx = random.randint(0, max(width_cha - size_cha - 5, 0))
            dery = random.randint(0, max(height_cha - size_cha - 5, 0))

        # font = ImageFont.truetype("arial.ttf", size_cha)
        cha = random.choice(set_cha)
        font = ImageFont.truetype(fonts['eng'], size_cha)
        contents.append(cha)
        im_cha = cha_draw(cha, text_color, font, rotate, size_cha)
        im.paste(im_cha, (int(max(i - overlap, 0) * width_cha) + derx, dery), im_cha)  # 字符左上角位置

    if 'point' in noise:
        nb_point = 30
        color_point = randRGB()
        for i in range(nb_point):
            x = random.randint(0, width_im)
            y = random.randint(0, height_im)
            drawer.point(xy=(x, y), fill=color_point)
    if 'line' in noise:
        nb_line = 10
        for i in range(nb_line):
            color_line = randRGB()
            sx = random.randint(0, width_im)
            sy = random.randint(0, height_im)
            ex = random.randint(0, width_im)
            ey = random.randint(0, height_im)
            drawer.line(xy=(sx, sy, ex, ey), fill=color_line)
    if 'circle' in noise:
        nb_circle = 5
        color_circle = randRGB()
        for i in range(nb_circle):
            sx = random.randint(0, width_im - 50)
            sy = random.randint(0, height_im - 20)
            ex = sx + random.randint(15, 25)
            ey = sy + random.randint(10, 15)
            drawer.arc((sx, sy, ex, ey), 0, 360, fill=color_circle)

    if os.path.exists(dir_path) == False:  # 如果文件夹不存在，则创建对应的文件夹
        os.makedirs(dir_path)
        pic_id = 1
    else:
        pathList = (os.listdir(dir_path))
        pic_names = {}
        for it in pathList:
            fun1 = lambda x: x.split('.')[0]
            key = fun1(it)
            pic_names[key] = it

        # pic_names = map(lambda x: x.split('.')[0], os.listdir(dir_path))
        # if 'label' in pic_names:
        # pic_names.pop('label')
        del pic_names['label']

        pic_id = max(map(int, pic_names.keys())) + 1  # 找到所有图片的最大标号，方便命名

    img_name = str(pic_id) + '.jpg'
    img_path = dir_path + img_name
    label_path = dir_path + 'label.txt'
    with open(label_path, 'a') as f:
        f.write(''.join(contents) + '\n')  # 在label文件末尾添加新图片的text内容
    print(img_path)
    im.save(img_path)


def captcha_generator():
    size_im = (200, 50)
    overlaps = [0.0, 0.3, 0.6]
    rd_text_poss = [True, False]
    rd_text_sizes = [True, False]
    rd_text_colors = [True, False]  # false 代表字体颜色全一致，但都是黑色
    rd_bg_color = True
    set_chas = ["0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "0123456789", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    noises = [[], ['point'], ['line'], ['line', 'point']]
    rotates = [True, False]
    nb_chas = [4, 6]
    nb_image = 50000
    font_dir = 'fonts/english'
    font_paths = []
    for dirpath, dirnames, filenames in os.walk(font_dir):
        for filename in filenames:
            filepath = dirpath + os.sep + filename
            font_paths.append({'eng': filepath})

        for i in range(nb_image):
            overlap = random.choice(overlaps)
            rd_text_pos = random.choice(rd_text_poss)
            rd_text_size = random.choice(rd_text_sizes)
            rd_text_color = random.choice(rd_text_colors)
            set_cha = random.choice(set_chas)
            noise = random.choice(noises)
            rotate = random.choice(rotates)
            nb_cha = random.choice(nb_chas)
            font_path = random.choice(font_paths)
            dir_name = 'all'
            dir_path = 'img_data/' + dir_name + '/'
            captcha_draw(size_im=size_im, nb_cha=nb_cha, set_cha=set_cha,
                         overlap=overlap, rd_text_pos=rd_text_pos, rd_text_size=rd_text_size,
                         rd_text_color=rd_text_color, rd_bg_color=rd_bg_color, noise=noise,
                         rotate=rotate, dir_path=dir_path, fonts=font_path)


def test():
    size_im = (200, 50)  # width, height
    set_cha = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # 字符集
    nb_image = 3  # 生成图片数
    font_dir = 'fonts/english'
    fonts_path = []
    for dirpath, dirnames, filenames in os.walk(font_dir):
        for filename in filenames:
            filepath = dirpath + os.sep + filename
            fonts_path.append(filepath)
    for i in range(nb_image):
        for font_path in fonts_path:
            nb_cha = random.choice([4, 6])  # 图片字符个数
            captcha_draw(size_im=size_im, nb_cha=nb_cha, set_cha=set_cha,
                         overlap=0.3,
                         rd_text_pos=True,
                         rd_text_size=True,
                         rd_text_color=True,
                         rd_bg_color=True,
                         noise=['line', 'point'],
                         rotate=True,
                         dir_path='img_data/tmp/',
                         fonts={'eng': font_path})


if __name__ == "__main__":
    # test()
    captcha_generator()
