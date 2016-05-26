#!/usr/bin/env python
# encoding: utf-8

import re


class SimHash(object):
    @classmethod
    def hash_of(cls, tokens, bits):
        """
        Return simhash for n bits by tokens.

        :param tokens: token with weight:[(weight, token), ...]
        :param bits: bits of simhash
        """
        # init the vector
        v_range = tuple(range(bits))
        v_result = [0 for i in v_range]

        # iterate every item of tokens
        for weight, word in tokens:
            # calc the simple hash of word
            word_hash = hash(word)
            # mask to check each bit of word_hash
            bmask = 1
            for i in v_range:
                # when there is 1 on this bit then add
                # the weight of this word to the v_result
                if word_hash & bmask:
                    v_result[i] += weight
                else:
                    v_result[i] -= weight
                # left shift the bmask to check next bit
                bmask <<= 1

        # make fingerprint from v_result
        return tuple(
            1 if i > 0 else 0
            for i in v_result
        )

    def __init__(self, tokens, bits):
        self.hash_result = self.hash_of(tokens, bits)
        self.tokens = tokens
        self.bits = bits

    def raw(self):
        return int("".join(str(i) for i in self.hash_result), 2)

    def hex(self):
        hex_step = 4
        hex_numbers = "0123456789ABCDEF"
        additional_bits = hex_step - self.bits % hex_step
        if additional_bits < hex_step:
            hash_result = [0] * additional_bits
        else:
            hash_result = []
        hash_result.extend(self.hash_result)

        str_result = []
        for i in range(0, self.bits, hex_step):
            nums = hash_result[i: i + hex_step]
            str_result.append(hex_numbers[reduce(
                lambda n, i: n << 1 | i,
                nums, 0
            )])
        return "".join(str_result)


def simhash(words, bits=128, spliter=None):
    """
    Return simple simhash which weight all is 1 of each item.

    :param words: string words
    :param bits: bits of simhash
    :param spliter: spliter to split words
    """
    if spliter is not None:
        words = spliter(words)
    return SimHash(((1, i) for i in words), bits).raw()


class Spliter(object):
    @classmethod
    def by_space(cls, words):
        return words.split()

    @classmethod
    def by_sep(cls, seps):
        def wrapper(words):
            return words.split(seps)
        return wrapper

    @classmethod
    def by_punctuations(cls, words):
        return re.split(r"\W", words)

    @classmethod
    def by_step(cls, step):
        def wrapper(words):
            word_len = len(words)
            start = 0
            end = step
            while start < word_len:
                yield words[start:end]
                start = end
                end += step

        return wrapper
