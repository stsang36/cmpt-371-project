import struct
from enum import IntEnum, auto, Enum

class Status(Enum):
    '''
    Types of packets that can be sent to the server.
    
    - SUCCESS: A successful operation.
    - FAILURE: A failed operation.
    - MOVE: when a position is updated.
    - PAUSE: when the game is paused.
    - END: when the game ends.
    - BALL_POS: when the ball position is updated.
    - START: when the game starts.

    '''
    SUCCESS = 'S'
    FAILURE = 'F'
    MOVE = 'M'
    PAUSE = 'P'
    END = '-'
    BALL_POS = 'B'
    START = '+'
    PLAYER_NEW_SLOT = 'N'

def serialize(data, s: Status):
    '''
    tries to format the byte string before sending. Returns a package ready to encode and send.
    ! - network byte order
    c - char
    36s - 36 byte string (for UUID)
    ff - two floats (x, y)
    '''

    if not data:
        raise ValueError("No Data was provided!")
    
    match s:
        case Status.MOVE:
            return struct.pack("!c36sff", Status.MOVE.value.encode(), data["uuid"].encode(), data["x"], data["y"] )
        case Status.PAUSE:
            return struct.pack("!c", Status.PAUSE.value.encode())
        case Status.END:
            return struct.pack("!c", Status.END.value.encode())
        case Status.BALL_POS:
            return struct.pack("!cff", Status.BALL_POS.value.encode(), data["x"], data["y"] )
        case Status.END:
            return struct.pack("!c36s", Status.END.value.encode(), data["uuid"].encode())
        case Status.START:
            return struct.pack("!c36s", Status.START.value.encode(), data["uuid"].encode())
        case Status.PLAYER_NEW_SLOT:
            return struct.pack("!c36sH", Status.PLAYER_NEW_SLOT.value.encode(), data["uuid"].encode(), data["slot"])
        case _:
            raise ValueError("Unknown type.")
        

def unload_packet(recieved):

    '''
    checks the first status then unloads the packet recieved.
    Returns a dictionary with the status and the data.
    '''

    if not recieved:
        raise ValueError("No Data was provided!")
    
    # Check the first byte to determine the packet type
    s = Status(struct.unpack("!c", recieved[:1])[0].decode())

    match s:
        case Status.MOVE:
            uuid, x, y = struct.unpack("!36sff", recieved[1:])
            return {'status': Status.MOVE, 'uuid': uuid.decode(), 'x': x, 'y': y}
        case Status.PAUSE:
            return {'status': Status.PAUSE}
        case Status.END:
            uuid, = struct.unpack("!36s", recieved[1:])
            return {'status': Status.END, 'uuid': uuid.decode()}
        case Status.BALL_POS:
            x, y = struct.unpack("!ff", recieved[1:])
            return {'status': Status.BALL_POS, 'x': x, 'y': y}
        case Status.START:
            uuid, = struct.unpack("!36s", recieved[1:])
            return {'status': Status.START, 'uuid': uuid.decode()}
        case Status.PLAYER_NEW_SLOT:
            uuid, slot = struct.unpack("!36sH", recieved[1:])
            return {'status': Status.PLAYER_NEW_SLOT, 'uuid': uuid.decode(), 'slot': slot}
        
        case _:
            raise ValueError("Unknown packet type.")

    pass

    
    


