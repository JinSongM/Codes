import numpy as np

COLORS_DICT = {
    "msl": {
        "colors": ["#0D4EA9", "#2882F0", "#50A5F5", "#96D2FA", "#B4F0FA", "#E1FFFF", "#FFFFFF", "#B4FAAA", "#78F573",
                   "#37D23C", "#1EB41E", "#0FA00F"],
        "levels": [950, 980, 985, 990, 995, 1000, 1005, 1020, 1025, 1030, 1035, 1040, 1090]

    },
    "wind_speed": {
        "colors": ["#ffffff", "#00D28C", "#00DC00", "#A0E632", "#E6AF2D", "#F08228", "#FA3C3C", "#F00082"],
        "levels": [0] + list(range(12, 33, 3)) + [99]

    }
}
CONTOUR_DICT = {
    "gh_500": {"levels": np.arange(400, 664, 4), "colors": "blue"}
}
