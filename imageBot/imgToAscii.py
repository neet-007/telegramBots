from PIL import Image
import numpy as np


def resize_img(img: Image.Image):
    w, h = img.size

    if w > h:
        ratio = w / h
        w = int((w // 8) * ratio)
        h = h // 8
    elif h > w:
        ratio = h / w
        h = int((h // 8) * ratio)
        w = w // 8
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
    img = Image.open("./static/uploads/uploaded_img.jpeg")
    img = resize_img(img)

    img_ = np.array(img)
    img_ = togray(img_)

    img_ = quantize_luminance(img_)
    img__ = Image.fromarray(img_)


    res = img_to_ascii(img_)
    with open("./static/uploads/ascii.txt", 'w') as f:
        lines = res.splitlines()
        for line in lines:
            f.write(line + "\n")
    print(res)





