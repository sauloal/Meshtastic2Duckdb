from ._message    import MessageClass
from ._base       import SharedFilterQuery, TimedFilterQuery

from .nodeinfo    import *
from .nodes       import *
from .position    import *
from .rangetest   import *
from .telemetry   import *
from .textmessage import *


def decode_packet(packet) -> "TelemetryClass|NodeInfoClass|PositionClass|TextMessageClass|RangeTestClass":
    message = MessageClass.from_packet(packet)

    if   message.portnum == "TELEMETRY_APP":
        return TelemetryClass.from_packet(packet)
    elif message.portnum == "NODEINFO_APP":
        return NodeInfoClass.from_packet(packet)
    elif message.portnum == "POSITION_APP":
        return PositionClass.from_packet(packet)
    elif message.portnum == "TEXT_MESSAGE_APP":
        return TextMessageClass.from_packet(packet)
    elif message.portnum == "RANGE_TEST_APP":
        return RangeTestClass.from_packet(packet)
    else:
        raise ValueError(f"Unknown portnum {message.portnum}. {packet}")

def decode_node(node: dict[str, typing.Any]) -> "NodesClass":
    inst = NodesClass.from_packet(node)
    return inst

def decode_nodes(nodes: dict[str, dict]) -> "list[NodesClass]":
    instances = [None] * len(nodes)
    for pos, (node_id, node) in enumerate(sorted(nodes.items())):
        #print("node_id", node_id)
        #print("data", data)
        #print(inst)
        inst = decode_node(node)
        instances[pos] = inst
    return instances

def class_to_ORM(cls):
    orm_class_name = cls.__ormclass__
    # print("orm_class_name", orm_class_name)

    orm_class      = globals().get(orm_class_name)
    # print("orm_class     ", orm_class)

    orm_inst       = orm_class(**cls.toDICT())
    # print("orm_inst      ", orm_inst)

    return orm_inst

