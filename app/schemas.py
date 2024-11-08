from pydantic import BaseModel

class Message(BaseModel):
        from_node : int
        to_node   : int

        fromId    : str   | None
        toId      : str

        rxTime    : int   | None
        rxRssi    : int   | None
        rxSnr     : float | None

        hopStart  : int   | None
        hopLimit  : int   | None

        message_id: int
        priority  : str   | None

        portnum   : str
        bitfield  : int   | None

class Telemetry(Message):
        time              : int
        batteryLevel      : int   | None # 76
        voltage           : float | None # 3.956
        channelUtilization: float | None # 5.8016667
        airUtilTx         : float | None # 4.323389
        uptimeSeconds     : int   | None # 51470
        numPacketsTx      : int   | None # 62
        numPacketsRx      : int   | None # 103
        numOnlineNodes    : int   | None # 3
        numTotalNodes     : int   | None # 3
        lux               : float | None # 0.0
        temperature       : float | None # 25.240046

class NodeInfo(Message):
        user_id   : str # !a
        longName  : str # M
        shortName : str # M
        macaddr   : str # 8Z
        hwModel   : str # TRACKER_T1000_E
        role      : str # TRACKER
        publicKey : str # S3

class Position(Message):
        latitudeI           : int   # 52
        longitudeI          : int   # 48
        altitude            : int   # 11
        time                : int   # 17
        PDOP                : int   # 272
        groundSpeed         : int   # 1
        groundTrack         : int   # 16
        satsInView          : int   # 6
        precisionBits       : int   # 32
        latitude            : float # 52
        longitude           : float #  4

class TextMessage(Message):
        payload     : bytes       # b'Hi'
        text        : str         # 'Hi'
        channel     : int  | None # 1     - Public Broadcast
        wantAck     : bool | None # True, - Direct Message
        publicKey   : str  | None # 'zd9' - Direct Message
        pkiEncrypted: bool | None # True  - Direct Message

class RangeTest(Message):
        payload             : bytes     # b'Hi'
        text                : str       # 'Hi'


#https://fastapi.tiangolo.com/tutorial/sql-databases/#hero-the-table-model
#from sqlmodel import Field, Session, SQLModel, create_engine, select

#class Nodes(SQLModel, table=True):


class Nodes(BaseModel):
        hopsAway            : int   | None  # 0
        lastHeard           : int           # 1700000000
        num                 : int           # 24
        snr                 : float         # 16.0
        isFavorite          : bool  | None  # True

        airUtilTx           : float         # 3.1853054
        batteryLevel        : int           # 64
        channelUtilization  : float         # 0.0
        uptimeSeconds       : int           # 16792
        voltage             : float         # 3.836

        altitude            : int   | None  # 18
        latitude            : float | None  # 52.0000000
        latitudeI           : int   | None  #  520000000
        longitude           : float | None  #  4.0000000
        longitudeI          : int   | None  #   48000000
        time                : int   | None  #  170000000

        hwModel             : str           # TRACKER_T1000_E
        user_id             : str           # !8fffffff
        longName            : str           # Aaaaaaa
        macaddr             : str           # 3Fffffff
        publicKey           : str           # Ia
        role                : str           # TRACKER
        shortName           : str           # AAAA
