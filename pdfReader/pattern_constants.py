import re

direction_pattern = re.compile(rb'</Direction/(.+?)>', re.S)
object_pattern = re.compile(rb'\r\n(\d+)\s\d+\sobj\r\n(.*?)\r\nendobj', re.S)
kids_pattern = re.compile(rb"/Kids\[(.*?)\]/Type/Pages>>", re.S)
kids_id_pattern = re.compile(rb"\s(\d+)\s\d+\sR\s", re.S)
contents_pattern = re.compile(rb"/Contents\s(\d+)\s\d+\sR\s", re.S)
stream_pattern = re.compile(rb'.*?FlateDecode.*?stream(.*?)endstream', re.S)
font_pattern = re.compile(rb"/Font<<(.*?)>>", re.S)
font_id_pattern = re.compile(rb"/([\w_]+)\s(\d+)\s\d+\sR\s", re.S)
char_pattern = re.compile(rb'<(\w+?)>\s<(\w+?)>', re.S)
to_unicode_id_pattern = re.compile(rb"/ToUnicode\s(\d+?)\s\d+\sR\s", re.S)
bfchar_pattern = re.compile(rb'beginbfchar(.*?)endbfchar', re.S)
text_pattern = re.compile(rb"/Span <</MCID\s.+?>>BDC.*?BT\n.*?/([^\s]+)\s\d+\sTf\n.*?\s([\.\d]+?)\sTm(.*?)ET", re.DOTALL)
sequence_pattern = re.compile(rb"([\(<][^<]+?[>\)])")
direct_pattern = re.compile(rb"\(([^\\]+?)\)", re.S)
octal_pattern = re.compile(rb"\(\s\\+(\d+?)\)", re.S)
encoded_pattern = re.compile(rb"<(\w+?)>", re.S)