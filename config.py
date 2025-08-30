# config.py
import os

# --- GitHub Configuration ---
# Base URL for the raw content of the repository on GitHub.
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/SamNotLazy/KDLProject/master/INDIAN-SHAPEFILES-master/"
# GitHub API URL to get directory contents.
GITHUB_API_BASE_URL = "https://api.github.com/repos/SamNotLazy/KDLProject/contents/"

# --- Local Data Configuration ---
# Base directory for the project's data.
BASE_DIR = 'Data/INDIAN-SHAPEFILES-master'

# --- Map Display Configuration ---
MAP_CONFIG = {'scrollZoom': True, 'displayModeBar': True, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']}

# --- Cache Configuration ---
CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
}

PLOTLY_CUSTOM_MAP_LAYOUTS={
    "ANDAMAN & NICOBAR": {
        "mapbox_center": {
            "lat": 10.213683897850284,
            "lon": 93.0733647662899
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 89.26811720708137,
            "south": 6.408436338641755,
            "east": 96.87861232549842,
            "north": 14.018931457058814
        }
    },
    "ANDHRA PRADESH": {
        "mapbox_center": {
            "lat": 15.895937511014829,
            "lon": 80.76266863810739
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 76.36038751673513,
            "south": 11.493656389642577,
            "east": 85.16494975947964,
            "north": 20.29821863238708
        }
    },
    "ARUNACHAL PRADESH": {
        "mapbox_center": {
            "lat": 28.05627870812826,
            "lon": 94.47897847944078
        },
        "mapbox_zoom": 5.5,
        "mapbox_bounds": {
            "west": 91.25320671897833,
            "south": 24.830506947665818,
            "east": 97.70475023990323,
            "north": 31.282050468590704
        }
    },
    "ASSAM": {
        "mapbox_center": {
            "lat": 26.05390371756694,
            "lon": 92.85819162698331
        },
        "mapbox_zoom": 5.5,
        "mapbox_bounds": {
            "west": 89.38264334354311,
            "south": 22.578355434126728,
            "east": 96.33373991042352,
            "north": 29.52945200100715
        }
    },
    "BIHAR": {
        "mapbox_center": {
            "lat": 25.90390673336631,
            "lon": 85.81037949445235
        },
        "mapbox_zoom": 6,
        "mapbox_bounds": {
            "west": 83.07122379883157,
            "south": 23.164751037745525,
            "east": 88.54953519007313,
            "north": 28.643062428987093
        }
    },
    "CHANDIGARH": {
        "mapbox_center": {
            "lat": 30.730840331824915,
            "lon": 76.77728773590867
        },
        "mapbox_zoom": 10.5,
        "mapbox_bounds": {
            "west": 76.6979380345037,
            "south": 30.65149063041994,
            "east": 76.85663743731365,
            "north": 30.81019003322989
        }
    },
    "CHHATTISGARH": {
        "mapbox_center": {
            "lat": 20.94432551150004,
            "lon": 82.32030588950005
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 78.84214015615004,
            "south": 17.46615977815003,
            "east": 85.79847162285006,
            "north": 24.42249124485005
        }
    },
    "DADRA & NAGAR HAVELI": {
        "districts": {}
    },
    "DAMAN & DIU": {
        "mapbox_center": {
            "lat": 20.56484639800806,
            "lon": 71.89011867438012
        },
        "mapbox_zoom": 7,
        "mapbox_bounds": {
            "west": 70.77464596322122,
            "south": 19.449373686849164,
            "east": 73.00559138553902,
            "north": 21.68031910916696
        }
    },
    "DELHI": {
        "mapbox_center": {
            "lat": 28.644249610845087,
            "lon": 77.09325179754202
        },
        "mapbox_zoom": 8.5,
        "mapbox_bounds": {
            "west": 76.81351427486662,
            "south": 28.364512088169676,
            "east": 77.37298932021743,
            "north": 28.923987133520498
        }
    },
    "GOA": {
        "mapbox_center": {
            "lat": 15.350710066776884,
            "lon": 74.00599581971676
        },
        "mapbox_zoom": 8,
        "mapbox_bounds": {
            "west": 73.51092065941307,
            "south": 14.855634906473204,
            "east": 74.50107098002044,
            "north": 15.845785227080563
        }
    },
    "GUJARAT": {
        "mapbox_center": {
            "lat": 22.41579081660557,
            "lon": 71.28502304898697
        },
        "mapbox_zoom": 5.5,
        "mapbox_bounds": {
            "west": 67.77432250297247,
            "south": 18.905090270591064,
            "east": 74.79572359500148,
            "north": 25.926491362620073
        }
    },
    "HARYANA": {
        "mapbox_center": {
            "lat": 29.290599162042746,
            "lon": 76.03898859292548
        },
        "mapbox_zoom": 6,
        "mapbox_bounds": {
            "west": 74.237188871026,
            "south": 27.48879944014327,
            "east": 77.84078831482495,
            "north": 31.09239888394222
        }
    },
    "HIMACHAL PRADESH": {
        "mapbox_center": {
            "lat": 31.817324728174313,
            "lon": 77.301577980448
        },
        "mapbox_zoom": 6,
        "mapbox_bounds": {
            "west": 75.42350712483976,
            "south": 29.939253872566066,
            "east": 79.17964883605624,
            "north": 33.695395583782556
        }
    },
    "JAMMU & KASHMIR": {
        "mapbox_center": {
            "lat": 33.69714475179461,
            "lon": 75.08489888641364
        },
        "mapbox_zoom": 6,
        "mapbox_bounds": {
            "west": 73.22059309969924,
            "south": 31.832838965080217,
            "east": 76.94920467312804,
            "north": 35.56145053850901
        }
    },
    "JHARKHAND": {
        "mapbox_center": {
            "lat": 23.659898869964586,
            "lon": 85.64596669917654
        },
        "mapbox_zoom": 6,
        "mapbox_bounds": {
            "west": 83.09801393696235,
            "south": 21.111946107750388,
            "east": 88.19391946139073,
            "north": 26.207851632178784
        }
    },
    "KARNATAKA": {
        "mapbox_center": {
            "lat": 15.02671157114138,
            "lon": 76.33668383985705
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 72.56134430800479,
            "south": 11.251372039289127,
            "east": 80.1120233717093,
            "north": 18.802051102993634
        }
    },
    "KERALA": {
        "mapbox_center": {
            "lat": 10.544048997177274,
            "lon": 76.13998834436055
        },
        "mapbox_zoom": 5.5,
        "mapbox_bounds": {
            "west": 73.66327199521876,
            "south": 8.067332648035498,
            "east": 78.61670469350233,
            "north": 13.02076534631905
        }
    },
    "LADAKH": {
        "mapbox_center": {
            "lat": 34.70762106350245,
            "lon": 76.42788585872768
        },
        "mapbox_zoom": 5.5,
        "mapbox_bounds": {
            "west": 72.13888541857429,
            "south": 30.418620623349064,
            "east": 80.71688629888106,
            "north": 38.99662150365584
        }
    },
    "LAKSHADWEEP": {
        "mapbox_center": {
            "lat": 9.983975537988918,
            "lon": 72.93328975091376
        },
        "mapbox_zoom": 6,
        "mapbox_bounds": {
            "west": 71.04132056889397,
            "south": 8.092006355969124,
            "east": 74.82525893293355,
            "north": 11.875944720008713
        }
    },
    "MADHYA PRADESH": {
        "mapbox_center": {
            "lat": 23.969570225381066,
            "lon": 78.42001148892685
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 73.59066399852776,
            "south": 19.140222734981975,
            "east": 83.24935897932593,
            "north": 28.798917715780156
        }
    },
    "MAHARASHTRA": {
        "mapbox_center": {
            "lat": 18.820028081431783,
            "lon": 76.77648264643727
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 72.24242095783944,
            "south": 14.285966392833952,
            "east": 81.3105443350351,
            "north": 23.354089770029614
        }
    },
    "MANIPUR": {
        "mapbox_center": {
            "lat": 24.762341884374862,
            "lon": 93.8575860596851
        },
        "mapbox_zoom": 6.5,
        "mapbox_bounds": {
            "west": 92.83518461636167,
            "south": 23.739940441051438,
            "east": 94.87998750300854,
            "north": 25.784743327698287
        }
    },
    "MEGHALAYA": {
        "mapbox_center": {
            "lat": 25.57432776697629,
            "lon": 91.30842112210038
        },
        "mapbox_zoom": 6.5,
        "mapbox_bounds": {
            "west": 89.66458031766456,
            "south": 23.93048696254046,
            "east": 92.95226192653621,
            "north": 27.218168571412118
        }
    },
    "MIZORAM": {
        "mapbox_center": {
            "lat": 23.231213167500044,
            "lon": 92.84658941400008
        },
        "mapbox_zoom": 6.5,
        "mapbox_bounds": {
            "west": 91.4275465761501,
            "south": 21.812170329650066,
            "east": 94.26563225185005,
            "north": 24.650256005350023
        }
    },
    "NAGALAND": {
        "mapbox_center": {
            "lat": 26.117305547880434,
            "lon": 94.2845397702286
        },
        "mapbox_zoom": 6.5,
        "mapbox_bounds": {
            "west": 93.23079771594777,
            "south": 25.063563493599606,
            "east": 95.33828182450944,
            "north": 27.171047602161263
        }
    },
    "ORISSA": {
        "districts": {}
    },
    "PUDUCHERRY": {
        "mapbox_center": {
            "lat": 13.794099774034748,
            "lon": 78.92021112874917
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 75.18727900047797,
            "south": 10.061167645763554,
            "east": 82.65314325702037,
            "north": 17.527031902305943
        }
    },
    "PUNJAB": {
        "mapbox_center": {
            "lat": 31.027415897975676,
            "lon": 75.4096331242582
        },
        "mapbox_zoom": 6,
        "mapbox_bounds": {
            "west": 73.7268698408915,
            "south": 29.34465261460896,
            "east": 77.09239640762492,
            "north": 32.71017918134239
        }
    },
    "RAJASTHAN": {
        "mapbox_center": {
            "lat": 26.629673915003995,
            "lon": 73.87824022005802
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 69.04482551787264,
            "south": 21.79625921281861,
            "east": 78.7116549222434,
            "north": 31.463088617189378
        }
    },
    "SIKKIM": {
        "mapbox_center": {
            "lat": 27.604182125326616,
            "lon": 88.46680899294111
        },
        "mapbox_zoom": 7.5,
        "mapbox_bounds": {
            "west": 87.88960268135622,
            "south": 27.026975813741725,
            "east": 89.044015304526,
            "north": 28.181388436911508
        }
    },
    "TAMIL NADU": {
        "mapbox_center": {
            "lat": 10.82116630670658,
            "lon": 78.28976492701142
        },
        "mapbox_zoom": 5.5,
        "mapbox_bounds": {
            "west": 75.27195684693052,
            "south": 7.803358226625688,
            "east": 81.30757300709232,
            "north": 13.838974386787472
        }
    },
    "TELANGANA": {
        "mapbox_center": {
            "lat": 17.876415400847236,
            "lon": 79.27927319564478
        },
        "mapbox_zoom": 5.5,
        "mapbox_bounds": {
            "west": 77.0315765366234,
            "south": 15.628718741825866,
            "east": 81.52696985466615,
            "north": 20.124112059868608
        }
    },
    "TRIPURA": {
        "mapbox_center": {
            "lat": 23.733414020606503,
            "lon": 91.74082183159868
        },
        "mapbox_zoom": 7,
        "mapbox_bounds": {
            "west": 90.86716851674225,
            "south": 22.85976070575007,
            "east": 92.6144751464551,
            "north": 24.607067335462936
        }
    },
    "UTTAR PRADESH": {
        "mapbox_center": {
            "lat": 27.138230096399496,
            "lon": 80.85933548883872
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 76.70640858910541,
            "south": 22.985303196666187,
            "east": 85.01226238857204,
            "north": 31.291156996132806
        }
    },
    "UTTARAKHAND": {
        "mapbox_center": {
            "lat": 30.089510836782647,
            "lon": 79.30879380903048
        },
        "mapbox_zoom": 6,
        "mapbox_bounds": {
            "west": 77.39865090701275,
            "south": 28.17936793476492,
            "east": 81.2189367110482,
            "north": 31.999653738800376
        }
    },
    "WEST BENGAL": {
        "mapbox_center": {
            "lat": 24.35238645951029,
            "lon": 87.8469307509705
        },
        "mapbox_zoom": 5,
        "mapbox_bounds": {
            "west": 84.69134855812031,
            "south": 21.196804266660095,
            "east": 91.00251294382069,
            "north": 27.507968652360482
        }
    }
}


