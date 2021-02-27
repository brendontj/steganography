import sys
import bitarray

from PIL import Image


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
    pixel_part_binary = bin(pixel_part)
    last_bit = int(pixel_part_binary[-1])
    calculated_last_bit = last_bit & bit
    return int(pixel_part_binary[:-1]+str(calculated_last_bit), 2)


def calculate_new_pixels(pixels, width, bit_list):
    bit_list_idx = 0
    for i in range(width):
        r, g, b = pixels[i, 0]
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

        pixels[i, 0] = (generated_red, generated_green, generated_blue)


def main():
    image_file = sys.argv[1]  # Parse command line arguments
    message = "testetestetest"  # Aleatory msg

    print("Size in bits of message: {}".format(len(message) * 8))
    bit_array = extract_bit_array(message)

    print("Size of bit array: {}".format(len(bit_array)))
    test_image_name = generate_test_image(image_file)

    image_test = Image.open(test_image_name)
    width, height = image_test.size
    print("Image created for test size: Width = {}, Height = {}".format(width, height))

    image_pixels = image_test.load()

    calculate_new_pixels(image_pixels, width, bit_array)

    image_test.save("output.png")


if __name__ == '__main__':
    main()
