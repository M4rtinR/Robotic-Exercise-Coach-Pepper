import time

from policy import Policy
import random
import numpy as np

def constrainedSumSamplePos(n, total, rangeGap):
    """Return a randomly chosen list of n positive integers summing to total.
    Each such list is equally likely to occur."""
    numpyRange = np.arange(0.0, total, rangeGap)
    range = np.ndarray.tolist(numpyRange)
    dividers = sorted(random.sample(range, n - 1))
    return [a - b for a, b in zip(dividers + [total], [0.0] + dividers)]

def constrainedSumSampleNonneg(n, total, rangeGap):
    """Return a randomly chosen list of n nonnegative integers summing to total.
    Each such list is equally likely to occur."""

    return [x - rangeGap for x in constrainedSumSamplePos(n, total + (n * rangeGap), rangeGap)]

def getStateName(code):
    # STATES
    statesDict = {
        # STYLE 1
        0: 'START_0',
        1: 'PREINSTRUCTION_0',
        2: 'CONCURRENTINSTRUCTIONPOSITIVE_0',
        3: 'CONCURRENTINSTRUCTIONNEGATIVE_0',
        4: 'POSTINSTRUCTIONPOSITIVE_0',
        5: 'POSTINSTRUCTIONNEGATIVE_0',
        6: 'MANUALMANIPULATION_0',
        7: 'QUESTIONING_0',
        8: 'POSITIVEMODELING_0',
        9: 'NEGATIVEMODELING_0',
        10: 'FIRSTNAME_0',
        11: 'HUSTLE_0',
        12: 'PRAISE_0',
        13: 'SCOLD_0',
        14: 'CONSOLE_0',
        15: 'PREINSTRUCTION_MANUALMANIPULATION_0',
        16: 'PREINSTRUCTION_QUESTIONING_0',
        17: 'PREINSTRUCTION_POSITIVEMODELING_0',
        18: 'PREINSTRUCTION_NEGATIVEMODELING_0',
        19: 'PREINSTRUCTION_PRAISE_0',
        20: 'CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING_0',
        21: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_0',
        22: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_0',
        23: 'POSTINSTRUCTIONPOSITIVE_QUESTIONING_0',
        24: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_0',
        25: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_0',
        26: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_0',
        27: 'POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_0',
        28: 'POSTINSTRUCTIONNEGATIVE_QUESTIONING_0',
        29: 'POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING_0',
        30: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_0',
        31: 'POSTINSTRUCTIONNEGATIVE_PRAISE_0',
        32: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_0',
        33: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_0',
        34: 'QUESTIONING_NEGATIVEMODELING_0',
        35: 'QUESTIONING_FIRSTNAME_0',
        36: 'POSITIVEMODELING_PREINSTRUCTION_0',
        37: 'POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE_0',
        38: 'NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE_0',
        39: 'HUSTLE_FIRSTNAME_0',
        40: 'PRAISE_FIRSTNAME_0',
        41: 'SCOLD_POSITIVEMODELING_0',
        42: 'SCOLD_FIRSTNAME_0',
        43: 'CONSOLE_FIRSTNAME_0',
        44: 'END_0',

        # STYLE 2
        45: 'START_1',
        46: 'PREINSTRUCTION_1',
        47: 'CONCURRENTINSTRUCTIONPOSITIVE_1',
        48: 'CONCURRENTINSTRUCTIONNEGATIVE_1',
        49: 'POSTINSTRUCTIONPOSITIVE_1',
        50: 'POSTINSTRUCTIONNEGATIVE_1',
        51: 'MANUALMANIPULATION_1',
        52: 'QUESTIONING_1',
        53: 'POSITIVEMODELING_1',
        54: 'NEGATIVEMODELING_1',
        55: 'FIRSTNAME_1',
        56: 'HUSTLE_1',
        57: 'PRAISE_1',
        58: 'SCOLD_1',
        59: 'CONSOLE_1',
        60: 'PREINSTRUCTION_MANUALMANIPULATION_1',
        61: 'PREINSTRUCTION_QUESTIONING_1',
        62: 'PREINSTRUCTION_POSITIVEMODELING_1',
        63: 'PREINSTRUCTION_NEGATIVEMODELING_1',
        64: 'PREINSTRUCTION_PRAISE_1',
        65: 'CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING_1',
        66: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_1',
        67: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_1',
        68: 'POSTINSTRUCTIONPOSITIVE_QUESTIONING_1',
        69: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_1',
        70: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_1',
        71: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_1',
        72: 'POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_1',
        73: 'POSTINSTRUCTIONNEGATIVE_QUESTIONING_1',
        74: 'POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING_1',
        75: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_1',
        76: 'POSTINSTRUCTIONNEGATIVE_PRAISE_1',
        77: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_1',
        78: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_1',
        79: 'QUESTIONING_NEGATIVEMODELING_1',
        80: 'QUESTIONING_FIRSTNAME_1',
        81: 'POSITIVEMODELING_PREINSTRUCTION_1',
        82: 'POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE_1',
        83: 'NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE_1',
        84: 'HUSTLE_FIRSTNAME_1',
        85: 'PRAISE_FIRSTNAME_1',
        86: 'SCOLD_POSITIVEMODELING_1',
        87: 'SCOLD_FIRSTNAME_1',
        88: 'CONSOLE_FIRSTNAME_1',
        89: 'END_1',

        # STYLE 3
        90: 'START_2',
        91: 'PREINSTRUCTION_2',
        92: 'CONCURRENTINSTRUCTIONPOSITIVE_2',
        93: 'CONCURRENTINSTRUCTIONNEGATIVE_2',
        94: 'POSTINSTRUCTIONPOSITIVE_2',
        95: 'POSTINSTRUCTIONNEGATIVE_2',
        96: 'MANUALMANIPULATION_2',
        97: 'QUESTIONING_2',
        98: 'POSITIVEMODELING_2',
        99: 'NEGATIVEMODELING_2',
        100: 'FIRSTNAME_2',
        101: 'HUSTLE_2',
        102: 'PRAISE_2',
        103: 'SCOLD_2',
        104: 'CONSOLE_2',
        105: 'PREINSTRUCTION_MANUALMANIPULATION_2',
        106: 'PREINSTRUCTION_QUESTIONING_2',
        107: 'PREINSTRUCTION_POSITIVEMODELING_2',
        108: 'PREINSTRUCTION_NEGATIVEMODELING_2',
        109: 'PREINSTRUCTION_PRAISE_2',
        110: 'CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING_2',
        111: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_2',
        112: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_2',
        113: 'POSTINSTRUCTIONPOSITIVE_QUESTIONING_2',
        114: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_2',
        115: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_2',
        116: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_2',
        117: 'POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_2',
        118: 'POSTINSTRUCTIONNEGATIVE_QUESTIONING_2',
        119: 'POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING_2',
        120: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_2',
        121: 'POSTINSTRUCTIONNEGATIVE_PRAISE_2',
        122: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_2',
        123: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_2',
        124: 'QUESTIONING_NEGATIVEMODELING_2',
        125: 'QUESTIONING_FIRSTNAME_2',
        126: 'POSITIVEMODELING_PREINSTRUCTION_2',
        127: 'POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE_2',
        128: 'NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE_2',
        129: 'HUSTLE_FIRSTNAME_2',
        130: 'PRAISE_FIRSTNAME_2',
        131: 'SCOLD_POSITIVEMODELING_2',
        132: 'SCOLD_FIRSTNAME_2',
        133: 'CONSOLE_FIRSTNAME_2',
        134: 'END_2',

        # STYLE 4
        135: 'START_3',
        136: 'PREINSTRUCTION_3',
        137: 'CONCURRENTINSTRUCTIONPOSITIVE_3',
        138: 'CONCURRENTINSTRUCTIONNEGATIVE_3',
        139: 'POSTINSTRUCTIONPOSITIVE_3',
        140: 'POSTINSTRUCTIONNEGATIVE_3',
        141: 'MANUALMANIPULATION_3',
        142: 'QUESTIONING_3',
        143: 'POSITIVEMODELING_3',
        144: 'NEGATIVEMODELING_3',
        145: 'FIRSTNAME_3',
        146: 'HUSTLE_3',
        147: 'PRAISE_3',
        148: 'SCOLD_3',
        149: 'CONSOLE_3',
        150: 'PREINSTRUCTION_MANUALMANIPULATION_3',
        151: 'PREINSTRUCTION_QUESTIONING_3',
        152: 'PREINSTRUCTION_POSITIVEMODELING_3',
        153: 'PREINSTRUCTION_NEGATIVEMODELING_3',
        154: 'PREINSTRUCTION_PRAISE_3',
        155: 'CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING_3',
        156: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_3',
        157: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_3',
        158: 'POSTINSTRUCTIONPOSITIVE_QUESTIONING_3',
        159: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_3',
        160: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_3',
        161: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_3',
        162: 'POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_3',
        163: 'POSTINSTRUCTIONNEGATIVE_QUESTIONING_3',
        164: 'POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING_3',
        165: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_3',
        166: 'POSTINSTRUCTIONNEGATIVE_PRAISE_3',
        167: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_3',
        168: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_3',
        169: 'QUESTIONING_NEGATIVEMODELING_3',
        170: 'QUESTIONING_FIRSTNAME_3',
        171: 'POSITIVEMODELING_PREINSTRUCTION_3',
        172: 'POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE_3',
        173: 'NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE_3',
        174: 'HUSTLE_FIRSTNAME_3',
        175: 'PRAISE_FIRSTNAME_3',
        176: 'SCOLD_POSITIVEMODELING_3',
        177: 'SCOLD_FIRSTNAME_3',
        178: 'CONSOLE_FIRSTNAME_3',
        179: 'END_3',

        # STYLE 5
        180: 'START_4',
        181: 'PREINSTRUCTION_4',
        182: 'CONCURRENTINSTRUCTIONPOSITIVE_4',
        183: 'CONCURRENTINSTRUCTIONNEGATIVE_4',
        184: 'POSTINSTRUCTIONPOSITIVE_4',
        185: 'POSTINSTRUCTIONNEGATIVE_4',
        186: 'MANUALMANIPULATION_4',
        187: 'QUESTIONING_4',
        188: 'POSITIVEMODELING_4',
        189: 'NEGATIVEMODELING_4',
        190: 'FIRSTNAME_4',
        191: 'HUSTLE_4',
        192: 'PRAISE_4',
        193: 'SCOLD_4',
        194: 'CONSOLE_4',
        195: 'PREINSTRUCTION_MANUALMANIPULATION_4',
        196: 'PREINSTRUCTION_QUESTIONING_4',
        197: 'PREINSTRUCTION_POSITIVEMODELING_4',
        198: 'PREINSTRUCTION_NEGATIVEMODELING_4',
        199: 'PREINSTRUCTION_PRAISE_4',
        200: 'CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING_4',
        201: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_4',
        202: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_4',
        203: 'POSTINSTRUCTIONPOSITIVE_QUESTIONING_4',
        204: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_4',
        205: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_4',
        206: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_4',
        207: 'POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_4',
        208: 'POSTINSTRUCTIONNEGATIVE_QUESTIONING_4',
        209: 'POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING_4',
        210: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_4',
        211: 'POSTINSTRUCTIONNEGATIVE_PRAISE_4',
        212: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_4',
        213: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_4',
        214: 'QUESTIONING_NEGATIVEMODELING_4',
        215: 'QUESTIONING_FIRSTNAME_4',
        216: 'POSITIVEMODELING_PREINSTRUCTION_4',
        217: 'POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE_4',
        218: 'NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE_4',
        219: 'HUSTLE_FIRSTNAME_4',
        220: 'PRAISE_FIRSTNAME_4',
        221: 'SCOLD_POSITIVEMODELING_4',
        222: 'SCOLD_FIRSTNAME_4',
        223: 'CONSOLE_FIRSTNAME_4',
        224: 'END_4',

        # STYLE 6
        225: 'START_5',
        226: 'PREINSTRUCTION_5',
        227: 'CONCURRENTINSTRUCTIONPOSITIVE_5',
        228: 'CONCURRENTINSTRUCTIONNEGATIVE_5',
        229: 'POSTINSTRUCTIONPOSITIVE_5',
        230: 'POSTINSTRUCTIONNEGATIVE_5',
        231: 'MANUALMANIPULATION_5',
        232: 'QUESTIONING_5',
        233: 'POSITIVEMODELING_5',
        234: 'NEGATIVEMODELING_5',
        235: 'FIRSTNAME_5',
        236: 'HUSTLE_5',
        237: 'PRAISE_5',
        238: 'SCOLD_5',
        239: 'CONSOLE_5',
        240: 'PREINSTRUCTION_MANUALMANIPULATION_5',
        241: 'PREINSTRUCTION_QUESTIONING_5',
        242: 'PREINSTRUCTION_POSITIVEMODELING_5',
        243: 'PREINSTRUCTION_NEGATIVEMODELING_5',
        244: 'PREINSTRUCTION_PRAISE_5',
        245: 'CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING_5',
        246: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_5',
        247: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_5',
        248: 'POSTINSTRUCTIONPOSITIVE_QUESTIONING_5',
        249: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_5',
        250: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_5',
        251: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_5',
        252: 'POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_5',
        253: 'POSTINSTRUCTIONNEGATIVE_QUESTIONING_5',
        254: 'POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING_5',
        255: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_5',
        256: 'POSTINSTRUCTIONNEGATIVE_PRAISE_5',
        257: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_5',
        258: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_5',
        259: 'QUESTIONING_NEGATIVEMODELING_5',
        260: 'QUESTIONING_FIRSTNAME_5',
        261: 'POSITIVEMODELING_PREINSTRUCTION_5',
        262: 'POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE_5',
        263: 'NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE_5',
        264: 'HUSTLE_FIRSTNAME_5',
        265: 'PRAISE_FIRSTNAME_5',
        266: 'SCOLD_POSITIVEMODELING_5',
        267: 'SCOLD_FIRSTNAME_5',
        268: 'CONSOLE_FIRSTNAME_5',
        269: 'END_5',

        # STYLE 7
        270: 'START_6',
        271: 'PREINSTRUCTION_6',
        272: 'CONCURRENTINSTRUCTIONPOSITIVE_6',
        273: 'CONCURRENTINSTRUCTIONNEGATIVE_6',
        274: 'POSTINSTRUCTIONPOSITIVE_6',
        275: 'POSTINSTRUCTIONNEGATIVE_6',
        276: 'MANUALMANIPULATION_6',
        277: 'QUESTIONING_6',
        278: 'POSITIVEMODELING_6',
        279: 'FIRSTNAME_6',
        280: 'HUSTLE_6',
        281: 'PRAISE_6',
        282: 'SCOLD_6',
        283: 'CONSOLE_6',
        284: 'PREINSTRUCTION_MANUALMANIPULATION_6',
        285: 'PREINSTRUCTION_POSITIVEMODELING_6',
        286: 'PREINSTRUCTION_NEGATIVEMODELING_6',
        287: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_6',
        288: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_6',
        289: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_6',
        290: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_6',
        291: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_6',
        292: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_6',
        293: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_6',
        294: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_6',
        295: 'QUESTIONING_NEGATIVEMODELING_6',
        296: 'QUESTIONING_FIRSTNAME_6',
        297: 'HUSTLE_FIRSTNAME_6',
        298: 'PRAISE_FIRSTNAME_6',
        299: 'PREINSTRUCTION_FIRSTNAME_6',
        300: 'CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE_6',
        301: 'CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_6',
        302: 'CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING_6',
        303: 'CONCURRENTINSTRUCTIONPOSITIVE_PRAISE_6',
        304: 'CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_6',
        305: 'CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_6',
        306: 'CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME_6',
        307: 'POSTINSTRUCTIONNEGATIVE_FIRSTNAME_6',
        308: 'MANUALMANIPULATION_PREINSTRUCTION_6',
        309: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE_6',
        310: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE_6',
        311: 'MANUALMANIPULATION_QUESTIONING_6',
        312: 'MANUALMANIPULATION_POSITIVEMODELING_6',
        313: 'MANUALMANIPULATION_FIRSTNAME_6',
        314: 'MANUALMANIPULATION_HUSTLE_6',
        315: 'MANUALMANIPULATION_PRAISE_6',
        316: 'MANUALMANIPULATION_CONSOLE_6',
        317: 'QUESTIONING_POSITIVEMODELING_6',
        318: 'POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE_6',
        319: 'POSITIVEMODELING_QUESTIONING_6',
        320: 'POSITIVEMODELLING_HUSTLE_6',
        321: 'POSITIVEMODELING_PRAISE_6',
        322: 'END_6',

        # STYLE 8
        323: 'START_7',
        324: 'PREINSTRUCTION_7',
        325: 'CONCURRENTINSTRUCTIONPOSITIVE_7',
        326: 'CONCURRENTINSTRUCTIONNEGATIVE_7',
        327: 'POSTINSTRUCTIONPOSITIVE_7',
        328: 'POSTINSTRUCTIONNEGATIVE_7',
        329: 'MANUALMANIPULATION_7',
        330: 'QUESTIONING_7',
        331: 'POSITIVEMODELING_7',
        332: 'FIRSTNAME_7',
        333: 'HUSTLE_7',
        334: 'PRAISE_7',
        335: 'SCOLD_7',
        336: 'CONSOLE_7',
        337: 'PREINSTRUCTION_MANUALMANIPULATION_7',
        338: 'PREINSTRUCTION_POSITIVEMODELING_7',
        339: 'PREINSTRUCTION_NEGATIVEMODELING_7',
        340: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_7',
        341: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_7',
        342: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_7',
        343: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_7',
        344: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_7',
        345: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_7',
        346: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_7',
        347: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_7',
        348: 'QUESTIONING_NEGATIVEMODELING_7',
        349: 'QUESTIONING_FIRSTNAME_7',
        350: 'HUSTLE_FIRSTNAME_7',
        351: 'PRAISE_FIRSTNAME_7',
        352: 'PREINSTRUCTION_FIRSTNAME_7',
        353: 'CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE_7',
        354: 'CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_7',
        355: 'CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING_7',
        356: 'CONCURRENTINSTRUCTIONPOSITIVE_PRAISE_7',
        357: 'CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_7',
        358: 'CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_7',
        359: 'CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME_7',
        360: 'POSTINSTRUCTIONNEGATIVE_FIRSTNAME_7',
        361: 'MANUALMANIPULATION_PREINSTRUCTION_7',
        362: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE_7',
        363: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE_7',
        364: 'MANUALMANIPULATION_QUESTIONING_7',
        365: 'MANUALMANIPULATION_POSITIVEMODELING_7',
        366: 'MANUALMANIPULATION_FIRSTNAME_7',
        367: 'MANUALMANIPULATION_HUSTLE_7',
        368: 'MANUALMANIPULATION_PRAISE_7',
        369: 'MANUALMANIPULATION_CONSOLE_7',
        370: 'QUESTIONING_POSITIVEMODELING_7',
        371: 'POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE_7',
        372: 'POSITIVEMODELING_QUESTIONING_7',
        373: 'POSITIVEMODELLING_HUSTLE_7',
        374: 'POSITIVEMODELING_PRAISE_7',
        375: 'END_7',

        # STYLE 9
        376: 'START_8',
        377: 'PREINSTRUCTION_8',
        378: 'CONCURRENTINSTRUCTIONPOSITIVE_8',
        379: 'CONCURRENTINSTRUCTIONNEGATIVE_8',
        380: 'POSTINSTRUCTIONPOSITIVE_8',
        381: 'POSTINSTRUCTIONNEGATIVE_8',
        382: 'MANUALMANIPULATION_8',
        383: 'QUESTIONING_8',
        384: 'POSITIVEMODELING_8',
        385: 'FIRSTNAME_8',
        386: 'HUSTLE_8',
        387: 'PRAISE_8',
        388: 'SCOLD_8',
        389: 'CONSOLE_8',
        390: 'PREINSTRUCTION_MANUALMANIPULATION_8',
        391: 'PREINSTRUCTION_POSITIVEMODELING_8',
        392: 'PREINSTRUCTION_NEGATIVEMODELING_8',
        393: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_8',
        394: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_8',
        395: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_8',
        396: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_8',
        397: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_8',
        398: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_8',
        399: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_8',
        400: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_8',
        401: 'QUESTIONING_NEGATIVEMODELING_8',
        402: 'QUESTIONING_FIRSTNAME_8',
        403: 'HUSTLE_FIRSTNAME_8',
        404: 'PRAISE_FIRSTNAME_8',
        405: 'PREINSTRUCTION_FIRSTNAME_8',
        406: 'CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE_8',
        407: 'CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_8',
        408: 'CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING_8',
        409: 'CONCURRENTINSTRUCTIONPOSITIVE_PRAISE_8',
        410: 'CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_8',
        411: 'CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_8',
        412: 'CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME_8',
        413: 'POSTINSTRUCTIONNEGATIVE_FIRSTNAME_8',
        414: 'MANUALMANIPULATION_PREINSTRUCTION_8',
        415: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE_8',
        416: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE_8',
        417: 'MANUALMANIPULATION_QUESTIONING_8',
        418: 'MANUALMANIPULATION_POSITIVEMODELING_8',
        419: 'MANUALMANIPULATION_FIRSTNAME_8',
        420: 'MANUALMANIPULATION_HUSTLE_8',
        421: 'MANUALMANIPULATION_PRAISE_8',
        422: 'MANUALMANIPULATION_CONSOLE_8',
        423: 'QUESTIONING_POSITIVEMODELING_8',
        424: 'POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE_8',
        425: 'POSITIVEMODELING_QUESTIONING_8',
        426: 'POSITIVEMODELLING_HUSTLE_8',
        427: 'POSITIVEMODELING_PRAISE_8',
        428: 'END_8',

        # STYLE 10
        429: 'START_9',
        430: 'PREINSTRUCTION_9',
        431: 'CONCURRENTINSTRUCTIONPOSITIVE_9',
        432: 'CONCURRENTINSTRUCTIONNEGATIVE_9',
        433: 'POSTINSTRUCTIONPOSITIVE_9',
        434: 'POSTINSTRUCTIONNEGATIVE_9',
        435: 'MANUALMANIPULATION_9',
        436: 'QUESTIONING_9',
        437: 'POSITIVEMODELING_9',
        438: 'FIRSTNAME_9',
        439: 'HUSTLE_9',
        440: 'PRAISE_9',
        441: 'SCOLD_9',
        442: 'CONSOLE_9',
        443: 'PREINSTRUCTION_MANUALMANIPULATION_9',
        444: 'PREINSTRUCTION_POSITIVEMODELING_9',
        445: 'PREINSTRUCTION_NEGATIVEMODELING_9',
        446: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_9',
        447: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_9',
        448: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_9',
        449: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_9',
        450: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_9',
        451: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_9',
        452: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_9',
        453: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_9',
        454: 'QUESTIONING_NEGATIVEMODELING_9',
        455: 'QUESTIONING_FIRSTNAME_9',
        456: 'HUSTLE_FIRSTNAME_9',
        457: 'PRAISE_FIRSTNAME_9',
        458: 'PREINSTRUCTION_FIRSTNAME_9',
        459: 'CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE_9',
        460: 'CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_9',
        461: 'CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING_9',
        462: 'CONCURRENTINSTRUCTIONPOSITIVE_PRAISE_9',
        463: 'CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_9',
        464: 'CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_9',
        465: 'CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME_9',
        466: 'POSTINSTRUCTIONNEGATIVE_FIRSTNAME_9',
        467: 'MANUALMANIPULATION_PREINSTRUCTION_9',
        468: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE_9',
        469: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE_9',
        470: 'MANUALMANIPULATION_QUESTIONING_9',
        471: 'MANUALMANIPULATION_POSITIVEMODELING_9',
        472: 'MANUALMANIPULATION_FIRSTNAME_9',
        473: 'MANUALMANIPULATION_HUSTLE_9',
        474: 'MANUALMANIPULATION_PRAISE_9',
        475: 'MANUALMANIPULATION_CONSOLE_9',
        476: 'QUESTIONING_POSITIVEMODELING_9',
        477: 'POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE_9',
        478: 'POSITIVEMODELING_QUESTIONING_9',
        479: 'POSITIVEMODELLING_HUSTLE_9',
        480: 'POSITIVEMODELING_PRAISE_9',
        481: 'END_9',

        # STYLE 11
        482: 'START_10',
        483: 'PREINSTRUCTION_10',
        484: 'CONCURRENTINSTRUCTIONPOSITIVE_10',
        485: 'CONCURRENTINSTRUCTIONNEGATIVE_10',
        486: 'POSTINSTRUCTIONPOSITIVE_10',
        487: 'POSTINSTRUCTIONNEGATIVE_10',
        488: 'MANUALMANIPULATION_10',
        489: 'QUESTIONING_10',
        490: 'POSITIVEMODELING_10',
        491: 'FIRSTNAME_10',
        492: 'HUSTLE_10',
        493: 'PRAISE_10',
        494: 'SCOLD_10',
        495: 'CONSOLE_10',
        496: 'PREINSTRUCTION_MANUALMANIPULATION_10',
        497: 'PREINSTRUCTION_POSITIVEMODELING_10',
        498: 'PREINSTRUCTION_NEGATIVEMODELING_10',
        499: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_10',
        500: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_10',
        501: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_10',
        502: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_10',
        503: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_10',
        504: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_10',
        505: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_10',
        506: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_10',
        507: 'QUESTIONING_NEGATIVEMODELING_10',
        508: 'QUESTIONING_FIRSTNAME_10',
        509: 'HUSTLE_FIRSTNAME_10',
        510: 'PRAISE_FIRSTNAME_10',
        511: 'PREINSTRUCTION_FIRSTNAME_10',
        512: 'CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE_10',
        513: 'CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_10',
        514: 'CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING_10',
        515: 'CONCURRENTINSTRUCTIONPOSITIVE_PRAISE_10',
        516: 'CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_10',
        517: 'CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_10',
        518: 'CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME_10',
        519: 'POSTINSTRUCTIONNEGATIVE_FIRSTNAME_10',
        520: 'MANUALMANIPULATION_PREINSTRUCTION_10',
        521: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE_10',
        522: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE_10',
        523: 'MANUALMANIPULATION_QUESTIONING_10',
        524: 'MANUALMANIPULATION_POSITIVEMODELING_10',
        525: 'MANUALMANIPULATION_FIRSTNAME_10',
        526: 'MANUALMANIPULATION_HUSTLE_10',
        527: 'MANUALMANIPULATION_PRAISE_10',
        528: 'MANUALMANIPULATION_CONSOLE_10',
        529: 'QUESTIONING_POSITIVEMODELING_10',
        530: 'POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE_10',
        531: 'POSITIVEMODELING_QUESTIONING_10',
        532: 'POSITIVEMODELLING_HUSTLE_10',
        533: 'POSITIVEMODELING_PRAISE_10',
        534: 'END_10',

        # STYLE 12
        535: 'START_11',
        536: 'PREINSTRUCTION_11',
        537: 'CONCURRENTINSTRUCTIONPOSITIVE_11',
        538: 'CONCURRENTINSTRUCTIONNEGATIVE_11',
        539: 'POSTINSTRUCTIONPOSITIVE_11',
        540: 'POSTINSTRUCTIONNEGATIVE_11',
        541: 'MANUALMANIPULATION_11',
        542: 'QUESTIONING_11',
        543: 'POSITIVEMODELING_11',
        544: 'FIRSTNAME_11',
        545: 'HUSTLE_11',
        546: 'PRAISE_11',
        547: 'SCOLD_11',
        548: 'CONSOLE_11',
        549: 'PREINSTRUCTION_MANUALMANIPULATION_11',
        550: 'PREINSTRUCTION_POSITIVEMODELING_11',
        551: 'PREINSTRUCTION_NEGATIVEMODELING_11',
        552: 'CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME_11',
        553: 'POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_11',
        554: 'POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING_11',
        555: 'POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING_11',
        556: 'POSTINSTRUCTIONPOSITIVE_FIRSTNAME_11',
        557: 'POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_11',
        558: 'MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE_11',
        559: 'MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE_11',
        560: 'QUESTIONING_NEGATIVEMODELING_11',
        561: 'QUESTIONING_FIRSTNAME_11',
        562: 'HUSTLE_FIRSTNAME_11',
        563: 'PRAISE_FIRSTNAME_11',
        564: 'PREINSTRUCTION_FIRSTNAME_11',
        565: 'CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE_11',
        566: 'CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION_11',
        567: 'CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING_11',
        568: 'CONCURRENTINSTRUCTIONPOSITIVE_PRAISE_11',
        569: 'CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION_11',
        570: 'CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING_11',
        571: 'CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME_11',
        572: 'POSTINSTRUCTIONNEGATIVE_FIRSTNAME_11',
        573: 'MANUALMANIPULATION_PREINSTRUCTION_11',
        574: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE_11',
        575: 'MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE_11',
        576: 'MANUALMANIPULATION_QUESTIONING_11',
        577: 'MANUALMANIPULATION_POSITIVEMODELING_11',
        578: 'MANUALMANIPULATION_FIRSTNAME_11',
        579: 'MANUALMANIPULATION_HUSTLE_11',
        580: 'MANUALMANIPULATION_PRAISE_11',
        581: 'MANUALMANIPULATION_CONSOLE_11',
        582: 'QUESTIONING_POSITIVEMODELING_11',
        583: 'POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE_11',
        584: 'POSITIVEMODELING_QUESTIONING_11',
        585: 'POSITIVEMODELLING_HUSTLE_11',
        586: 'POSITIVEMODELING_PRAISE_11',
        587: 'END_11'}

    return statesDict[code]


def getActionName(code):
    # ACTIONS
    actionsDict = {
       0: 'A_START',
       1: 'A_PREINSTRUCTION',
       2: 'A_CONCURRENTINSTRUCTIONPOSITIVE',
       3: 'A_CONCURRENTINSTRUCTIONNEGATIVE',
       4: 'A_POSTINSTRUCTIONPOSITIVE',
       5: 'A_POSTINSTRUCTIONNEGATIVE',
       6: 'A_MANUALMANIPULATION',
       7: 'A_QUESTIONING',
       8: 'A_POSITIVEMODELING',
       9: 'A_NEGATIVEMODELING',
       10: 'A_FIRSTNAME',
       11: 'A_HUSTLE',
       12: 'A_PRAISE',
       13: 'A_SCOLD',
       14: 'A_CONSOLE',
       15: 'A_PREINSTRUCTION_MANUALMANIPULATION',
       16: 'A_PREINSTRUCTION_QUESTIONING',
       17: 'A_PREINSTRUCTION_POSITIVEMODELING',
       18: 'A_PREINSTRUCTION_NEGATIVEMODELING',
       19: 'A_PREINSTRUCTION_PRAISE',
       20: 'A_CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING',
       21: 'A_CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME',
       22: 'A_POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION',
       23: 'A_POSTINSTRUCTIONPOSITIVE_QUESTIONING',
       24: 'A_POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING',
       25: 'A_POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING',
       26: 'A_POSTINSTRUCTIONPOSITIVE_FIRSTNAME',
       27: 'A_POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION',
       28: 'A_POSTINSTRUCTIONNEGATIVE_QUESTIONING',
       29: 'A_POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING',
       30: 'A_POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING',
       31: 'A_POSTINSTRUCTIONNEGATIVE_PRAISE',
       32: 'A_MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE',
       33: 'A_MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE',
       34: 'A_QUESTIONING_NEGATIVEMODELING',
       35: 'A_QUESTIONING_FIRSTNAME',
       36: 'A_POSITIVEMODELING_PREINSTRUCTION',
       37: 'A_POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE',
       38: 'A_NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE',
       39: 'A_HUSTLE_FIRSTNAME',
       40: 'A_PRAISE_FIRSTNAME',
       41: 'A_SCOLD_POSITIVEMODELING',
       42: 'A_SCOLD_FIRSTNAME',
       43: 'A_CONSOLE_FIRSTNAME',
       44: 'A_PREINSTRUCTION_FIRSTNAME',
       45: 'A_CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE',
       46: 'A_CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION',
       47: 'A_CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING',
       48: 'A_CONCURRENTINSTRUCTIONPOSITIVE_PRAISE',
       49: 'A_CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION',
       50: 'A_CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING',
       51: 'A_CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME',
       52: 'A_POSTINSTRUCTIONNEGATIVE_FIRSTNAME',
       53: 'A_MANUALMANIPULATION_PREINSTRUCTION',
       54: 'A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE',
       55: 'A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE',
       56: 'A_MANUALMANIPULATION_QUESTIONING',
       57: 'A_MANUALMANIPULATION_POSITIVEMODELING',
       58: 'A_MANUALMANIPULATION_FIRSTNAME',
       59: 'A_MANUALMANIPULATION_HUSTLE',
       60: 'A_MANUALMANIPULATION_PRAISE',
       61: 'A_MANUALMANIPULATION_CONSOLE',
       62: 'A_QUESTIONING_POSITIVEMODELING',
       63: 'A_POSITIVEMODELING_CONCURRENTINSTRUCTIONNEGATIVE',
       64: 'A_POSITIVEMODELING_QUESTIONING',
       65: 'A_POSITIVEMODELLING_HUSTLE',
       66: 'A_POSITIVEMODELING_PRAISE',
       67: 'A_END'}

    return actionsDict[code]


if __name__ == '__main__':
    style_distribution = [x / 100 for x in constrainedSumSamplePos(12, 100, 0.001)]
    print('style_distribution =', style_distribution, '\n\n')
    p = Policy(style_distribution)

    # change to start in max of style_distribution
    observation = 0

    for i in range(15):
        action = p.sample_action(observation)
        print('timestep', i)
        print('action =', getActionName(action))
        observation = p.sample_observation(observation, action)
        print('observation =', getStateName(observation))
        print('\n\n')
        time.sleep(3)
