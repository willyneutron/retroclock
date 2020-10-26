from enum import IntEnum

class Turn_on_mode(IntEnum):
    SECONDS         = 1
    ALWAYS_ON       = 2

class Nixie_mode(IntEnum):
    H24             = 1
    H12             = 2
    COUNTDOWN       = 3
    STOPWATCH       = 4
    CUSTOM          = 5

class HP_mode(IntEnum):
    ROLLING         = 1
    DATE            = 2
    WEATHER         = 3
    NETWORK         = 4
    CUSTOM          = 5

config = {
    "general_config": {
        "api_base_url": "api/v1/",

        # Public general
        # /general
        "general_public": {
            # Turn on mode
            "turn_on_mode": Turn_on_mode.SECONDS,

            # Turn on time in seconds
            "turn_on_time": 60,        
        }
    },

    "nixie_config": {

        # Gpio to enable nixie relay.        
        "nixie_relay_gpio": 23,

        # Information about nixie drivers
        "nixie_driver_a": {
            "i2c_addr": 0x20,
            "digits": [0x9, 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8]
        },

        "nixie_driver_b": {
            "i2c_addr": 0x21,
            "digits": [0x9, 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8]
        },

        # Public config
        # /nixie
        "nixie_public": {

            # Nixie working mode
            "nixie_mode": Nixie_mode.H24,

            # Wether or not dots are activated in 24/12 hour mode
            "nixie_mode_hour_dots": True,
            
            # Nixie h/m/s holders for countdown start, custom text mode and getting
            # nixie value in each time
            "nixie_value_h": 0,
            "nixie_value_m": 0,
            "nixie_value_s": 0,
        },

        # Actions:
        # /nixie/tick  GET    Starts countdown/stopwatch or power on nixies in other mode. 
    },

    "hp_config" : {

        "i2c_addr": 0x23,
        "viewport": [
            (0,3), (0,2), (0,1), (0,0),
            (1,3), (1,2), (1,1), (1,0),
            (2,3), (2,2), (2,1), (2,0),
            (3,3), (3,2), (3,1), (3,0)
        ],

        "viewport_speed": 0.3,
        
        "owm_place": "Madrid,ES",
        "owm_api_key": "<OWM_KEY>",

        # Public config
        # /hp
        "hp_public": {

            # Hp working mode
            "hp_mode": HP_mode.ROLLING,

            # Format for date mode
            "hp_date_format": "%A %d %B, %Y  ",

            # HP text. For free text mode oor getting the current text
            "hp_value": ""
        }

        # Action:
        # /hp/tick  GET    Lights power on HP screen
    }
}