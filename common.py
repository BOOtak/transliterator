# coding=utf-8
from __future__ import unicode_literals
import requests

__author__ = 'kirill'

methods = {'GET': requests.get,
           'POST': requests.post,
           'PUT': requests.put,
           'HEAD': requests.head,
           'OPTIONS': requests.options}

PORT = 34106

max_attempts = 3

connection_timeout = 1  # s

transliter = {
    "а": b"a",
    "б": b"b",
    "в": b"v",
    "г": b"g",
    "д": b"d",
    "е": b"e",
    "ё": b"yo",
    "ж": b"zh",
    "з": b"z",
    "и": b"i",
    "й": b"j",
    "к": b"k",
    "л": b"l",
    "м": b"m",
    "н": b"n",
    "о": b"o",
    "п": b"p",
    "р": b"r",
    "с": b"s",
    "т": b"t",
    "у": b"u",
    "ф": b"f",
    "х": b"h",
    "ц": b"ts",
    "ч": b"ch",
    "ш": b"sh",
    "щ": b"sh\'",
    "ъ": b"\'",
    "ы": b"y",
    "ь": b"\'",
    "э": b"e",
    "ю": b"yu",
    "я": b"ya",
    "А": b"A",
    "Б": b"B",
    "В": b"V",
    "Г": b"G",
    "Д": b"D",
    "Е": b"E",
    "Ё": b"Yo",
    "Ж": b"Zh",
    "З": b"Z",
    "И": b"I",
    "Й": b"J",
    "К": b"K",
    "Л": b"L",
    "М": b"M",
    "Н": b"N",
    "О": b"O",
    "П": b"P",
    "Р": b"R",
    "С": b"S",
    "Т": b"T",
    "У": b"U",
    "Ф": b"F",
    "Х": b"H",
    "Ц": b"Ts",
    "Ч": b"Ch",
    "Ш": b"Sh",
    "Щ": b"Sh\'",
    "Ъ": b"\'",
    "Ы": b"Y",
    "Ь": b"\'",
    "Э": b"E",
    "Ю": b"Yu",
    "Я": b"Ya"
}