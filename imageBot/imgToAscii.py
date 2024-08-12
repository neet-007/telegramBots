from PIL import Image
import numpy as np


def resize_img(img: Image.Image):
    w, h = img.size
  
    reducers = 8
    if w > 2000 or h > 2000:
        reducers = 16
    if w > h:
        ratio = w / h
        w = int((w // reducers) * ratio)
        h = h // reducers
    elif h > w:
        ratio = h / w
        h = int((h // reducers) * ratio)
        w = w // reducers
    img = img.resize((w, h))

    return img

def togray(img: np.ndarray, format: str="rgb"):
    if format.lower() == 'bgr':
        b, g, r = img[..., 0], img[..., 1], img[..., 2]
        return 0.2989 * r + 0.5870 * g + 0.1140 * b
    elif format.lower() == 'rgb':
        r, g, b = img[..., 0], img[..., 1], img[..., 2]
        return 0.2989 * r + 0.5870 * g + 0.1140 * b
    else:
        raise Exception('Unsupported value in parameter \'format\'')

def quantize_luminance(img: np.ndarray):

    img_normalized = img / 255.0

    quantized = np.floor(img_normalized * 10) / 10

    output = (quantized * 255).astype(np.uint8)
    return output.squeeze()

def img_to_ascii(img: np.ndarray):
    letters = [' ', '.', ':', 'c', 'o', 'P', 'O', '?', '%', '#']

    y, x = img.shape

    output = [['' for _ in range(x)] for _ in range(y)]
    for i in range(y):
        for j in range(x):
            luminance_index = img[i, j]   
            pos_index = ((i % 8) // 8) + ((j % 8) // 8)
            index = (luminance_index + pos_index) % len(letters)

            output[i][j] = letters[index]

    return '\n'.join(''.join(row) for row in output)


if __name__ == "__main__":
    img = Image.open("./static/uploads/rome3.jpg")
    img = resize_img(img)

    img_ = np.array(img)
    img_ = togray(img_)

    img_ = quantize_luminance(img_)
    img__ = Image.fromarray(img_)


    res = img_to_ascii(img_)
    print(res)






