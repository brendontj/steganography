import bitarray
import argparse

from PIL import Image
from pathlib import Path


def extract_bit_array(m_string):
    """Extract the bit array(list) of message without encoding"""
    bitarray_ = bitarray.bitarray()
    bitarray_.frombytes(m_string.encode('utf-8'))
    return [int(i) for i in bitarray_]


def generate_test_image(file_name):
    """Generate image to use in execution.
    Return: The name of generated test image"""
    image = Image.open(file_name)

    split_name = file_name.split('.')
    split_name[0] = split_name[0] + '_testing'
    test_image_name = split_name[0] + '.' + split_name[1]

    image.save(test_image_name)

    return test_image_name


def add_bit_least_significant(pixel_part, bit):
    """Change least significant bit of a byte"""
    pixel_part_binary = bin(pixel_part)
    last_bit = int(pixel_part_binary[-1])
    calculated_last_bit = last_bit & bit
    return int(pixel_part_binary[:-1]+str(calculated_last_bit), 2)


def calculate_new_pixels(pixels, width, height, bit_list):
    """Calculate channels of new pixels with the new least significant bit representing a bit of hidden message"""
    bit_list_idx = 0
    for i in range(height):
        if len(bit_list) == bit_list_idx:
            break
            
        for j in range(width):
            r, g, b = pixels[j, i]
            generated_red = 255
            generated_green = 255
            generated_blue = 255

            if bit_list_idx < len(bit_list):  # R
                generated_red = add_bit_least_significant(r, bit_list[bit_list_idx])
                bit_list_idx += 1

            if bit_list_idx < len(bit_list):  # G
                generated_green = add_bit_least_significant(g, bit_list[bit_list_idx])
                bit_list_idx += 1

            if bit_list_idx < len(bit_list):  # B
                generated_blue = add_bit_least_significant(b, bit_list[bit_list_idx])
                bit_list_idx += 1

            pixels[j, i] = (generated_red, generated_green, generated_blue)


def hide_bits_image(bit_array, image_file):
    """Hide all bits of message in the bytes of image"""
    test_image_name = generate_test_image(image_file)
    image_test = Image.open(test_image_name)
    width, height = image_test.size
    print("Image created for test size: Width = {}, Height = {}".format(width, height))
    image_pixels = image_test.load()
    calculate_new_pixels(image_pixels, width,height, bit_array)
    image_test.save("output.png")


def compare_file_size(file1, file2):
    """Compare sizes of original image with the steganography process resulted image"""
    if Path(file1).stat().st_size == Path(file2).stat().st_size:
        print("File {} and file {} has the same size in bytes.".format(file1, file2))
    else:
        print("File {} and file {} has different sizes in bytes.".format(file1, file2))

    print("Size of {} in bytes: {}".format(file1, Path(file1).stat().st_size))
    print("Size of {} in bytes: {}".format(file2, Path(file2).stat().st_size))


def is_same_height(h1, h2):
    """Return true if is the same height of images else return false"""
    if h1 == h2:
        return True
    return False


def is_same_width(w1, w2):
    """Return true if is the same width of images else return false"""
    if w1 == w2:
        return True
    return False


def extract_lsb(n):
    """Extract thee least significant bit"""
    byte_string = bin(n)
    return byte_string[-1]


def extract_message_lsb(image):
    """Extract the message hidden in a image"""
    im = Image.open(image)

    width, height = im.size
    print("Image size: Width = {}, Height = {}".format(width, height))

    pxs = im.load()

    bit_string = ""
    for i in range(height):
        for j in range(width):
            r, g, b = pxs[j, i]

            bit_string += extract_lsb(r)
            bit_string += extract_lsb(g)
            bit_string += extract_lsb(b)

    return bit_string


def to_str(bit_str):
    """Transform bit string in a string of characters"""
    chars = []
    for i in range(int(len(bit_str) / 8)):
        byte = bit_str[i * 8:(i + 1) * 8]
        if byte == "11111111":
            break
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)


def parser():
    """Parse command line arguments"""
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--Message", required=False,
                    help="Message to put in a image")
    ap.add_argument("-f", "--OriginalImage", required=True,
                    help="Original image to put a message or compare with result of steganography image")
    ap.add_argument("-o", "--ResultImage", required=False,
                    help="Image used to compare and extract the message hidden")
    ap.add_argument("-s", "--PutMessageMode", required=False,
                    help="Mode to insert a message in a image", action="store_true")
    ap.add_argument("-r", "--ReverseMode", required=False,
                    help="Mode to extract the message of an image comparing with original", action="store_true")
    return vars(ap.parse_args())


def main():
    args = parser()

    if args['PutMessageMode']:
        message = args.get('Message')
        if message is None:
            print("Insert a message after -m to be used in steganography process")
            return
        else:
            print("Number of bits in the message: {}".format(len(message) * 8))
            bit_array = extract_bit_array(message)
            print("Size of bit array: {}".format(len(bit_array)))
            hide_bits_image(bit_array, args.get('OriginalImage'))
            print("Steganography process done with success!")
            return
    elif args['ReverseMode']:
        result_image = args.get('ResultImage')
        if result_image is None:
            print("Insert the resulted image of steganography process to extract the message")
            return
        else:
            original_image = args.get('OriginalImage')
            compare_file_size(original_image, result_image)
            message_bit_string = extract_message_lsb(result_image)
            print(to_str(message_bit_string))


if __name__ == '__main__':
    main()
