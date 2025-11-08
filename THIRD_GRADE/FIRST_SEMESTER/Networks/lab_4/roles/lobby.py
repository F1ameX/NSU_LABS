from snakes_proto import snakes_pb2 as pb

def build_discover():
    return pb.GameMessage(discover=pb.GameMessage.DiscoverMsg(), msg_seq=1)