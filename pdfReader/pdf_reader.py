
import os
import zlib

import pdfReader.pattern_constants as pt
from pdfReader.utf16_decoder import ar_decoder, ar_size


def reverse_text(text):
    """
    Reverse the order of a text characters.
    :param text: string
    :return: string
    """
    if len(text) <= 1:
        return text
    result = ""
    i = len(text) - 1
    while i >= 0:
        result += text[i]
        i -= 1
    return result


def process_file(path, mode, content=''):
    """
    Open or close a file depending on 'mode'.
    :param path: string
    :param mode: string
    :param content: string
    :return: binary or string
    """
    file = None
    if "r" in mode:
        if not os.path.exists(path):
            open(path, "w").close()
        file = open(path, mode)
        content = file.read()
    elif "w" in mode or "a" in mode:
        file = open(path, mode)
        file.write(content)
    if file is not None:
        file.close()
    return content


class PDFReader:
    def __init__(self, filename):

        self.__pdf_binary = process_file(filename, "rb")
        try:
            self.__direction = pt.direction_pattern.findall(self.__pdf_binary)[0]
        except:
            pass

        self.__objects = self.__get_object_all()
        self.__content_id_all, self.__font_id_all = self.__process_kid_all()
        self.text = self.__get_text()
        # filename = filename.split(".")[0] + ".txt"
        # process_file(filename, "wb", content=file.encode())

    def __get_object_all(self):
        tmp = pt.object_pattern.findall(self.__pdf_binary)
        size = None
        objects = []
        for obj in tmp:
            stream_all = pt.stream_pattern.findall(obj[1])
            if len(stream_all) > 0:
                content = b''
                for stream in stream_all:
                    try:
                        content += zlib.decompress(stream.strip(b'\r\n'))
                    except:
                        pass

                font_all = pt.bfchar_pattern.findall(content)
                if len(font_all) > 0:
                    decoder, size = self.__get_decoder(font_all)
                    objects.append((obj[0], decoder, size))
                else:
                    objects.append((obj[0], content))
            else:
                objects.append((obj[0], obj[1]))

        return objects

    def __get_decoder(self, font):
        decoder_dict = dict()
        for f in font:
            char_all = pt.char_pattern.findall(f)
            for char in char_all:
                char_0 = str(char[0])[2:-1]
                if char_0 not in decoder_dict:
                    char_1 = str(char[1])[2:-1]
                    decoder_dict[char_0] = self.__decode_sequence(char_1, ar_decoder, ar_size)

        size = 0
        for d in decoder_dict:
            size = len(d)
            break
        return decoder_dict, size

    def __get_kid_id_all(self):
        """
        Extract object id of kids that present a page in PDF file.
        :return: list[number]
        """
        kids = pt.kids_pattern.findall(self.__pdf_binary)
        kid_id_all = []
        for kid in kids:
            kid_id_all += pt.kids_id_pattern.findall(kid)

        return kid_id_all

    def __get_object(self, object_id):
        """
        Get the content of an object found by id.
        :param object_id: number
        :return:binary
        """
        for o in self.__objects:
            if object_id == o[0]:
                if len(o) > 2:
                    return o[1], o[2]
                return o[1]

    def __get_font_id_all(self, kid_object):
        """
        Extract name and object id of a kid fonts.
        :param kid_object: binary
        :return: list[(font_name, object_id)]
        """
        font_all = pt.font_pattern.findall(kid_object)
        font_id = []
        for f in font_all:
            font_id += pt.font_id_pattern.findall(f)
        to_unicode_id = []
        for f in font_id:
            obj = self.__get_object(f[1])
            try:
                to_unicode_id.append((f[0], pt.to_unicode_id_pattern.findall(obj)[0]))
            except:
                pass
        return to_unicode_id

    def __process_kid_all(self):
        """
        Extract Content and Fonts of each kid.
        :return: list[binary], list[(font_name, object_id)]
        """
        kid_id_all = self.__get_kid_id_all()
        content_id_all = []
        font_id_all = []
        for kid_id in kid_id_all:
            kid = self.__get_object(kid_id)
            try:
                content_id_all.append(pt.contents_pattern.findall(kid)[0])
            except:
                pass
            font_id_all.append(self.__get_font_id_all(kid))
        return content_id_all, font_id_all

    def __get_line_all(self, content):
        """
        Extract line by line from a page text.
        :return: dictionary
        """
        text_all = pt.text_pattern.findall(content)
        line_all = dict()
        for text in text_all:
            sequence_all = pt.sequence_pattern.findall(text[2])
            if text[1] in line_all:
                line_all[text[1]].append((text[0], sequence_all))
            else:
                line_all[text[1]] = [(text[0], sequence_all)]
        return line_all

    def __get_text(self):
        """
        Extract text from content objects.
        :return: string
        """
        file = ""
        for i in range(len(self.__content_id_all)):
            content = self.__get_object(self.__content_id_all[i])
            font_all = self.__font_id_all[i]
            line_all = self.__get_line_all(content)
            page = ""
            for line in line_all:
                line_text = []
                for sequence in line_all[line]:
                    font = dict()
                    size = 0
                    for f in font_all:
                        if f[0] == sequence[0]:
                            font, size = self.__get_object(f[1])
                            break

                    s = 0
                    while s < len(sequence[1]):
                        # direct char (154 abc)
                        direct_char = pt.direct_pattern.findall(sequence[1][s])
                        char = "".join([str(d)[2:-1] for d in direct_char])
                        if char:
                            line_text.append(char)

                        # octal char ( \\226)
                        octal_char = pt.octal_pattern.findall(sequence[1][s])
                        char = "".join(["".join(hex(int(c, 8)).split("0x")) for c in octal_char])
                        if char:
                            line_text.append(self.__decode_sequence(char, font, size))

                        # utf16 encoded char <001200de...>
                        encoded_char = pt.encoded_pattern.findall(sequence[1][s])
                        char = str(b"".join(encoded_char))[2:-1]
                        if char[:size] == "FEFF":
                            char_next = str(b"".join(pt.encoded_pattern.findall(sequence[1][s + 1])))[2:-1]
                            if len(char[size:]) > len(char_next):
                                j = 0
                                for j in range(size, len(char[size:]), 8):
                                    line_text.append(self.__decode_sequence(char[j:j + 8], ar_decoder, size))
                                line_text.append(self.__decode_sequence(char[j + 8:], ar_decoder, size))
                            else:
                                line_text.append(reverse_text(self.__decode_sequence(char[4:], ar_decoder, size)))
                            s += 1
                        elif char:
                            line_text.append(reverse_text(self.__decode_sequence(char, font, size)))
                        s += 1
                p = len(line_text) - 1
                while p >= 0:
                    page += line_text[p]
                    p -= 1
                page += "\n"
            file += page
        return file

    def __decode_sequence(self, sequence, decoder, size):
        """
        Decode a hex sequence to letters.
        :param sequence: binary
        :param decoder: dictionary
        :param size: number
        :return: string
        """
        decode = ''
        i = 0
        while i <= len(sequence) - size:
            if sequence[i:i + size] in decoder:
                if self.__direction == b'R2L':
                    decode += reverse_text(decoder[sequence[i:i + size]])
                else:
                    decode += decoder[sequence[i:i + size]]
            else:
                decode += sequence[i:i + size]
            i += size
        return decode
