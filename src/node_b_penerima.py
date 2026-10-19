import RNS, time
APP_NAME = "tugas5"

def on_packet(data, packet):
    RNS.log("Pesan diterima: " + data.decode("utf-8"))

reticulum = RNS.Reticulum()
identity = RNS.Identity()
dest = RNS.Destination(identity, RNS.Destination.IN,
                       RNS.Destination.SINGLE, APP_NAME, "pesan")
dest.set_packet_callback(on_packet)
dest.set_proof_strategy(RNS.Destination.PROVE_ALL)
RNS.log("Node B siap, hash tujuan: " + RNS.prettyhexrep(dest.hash))
while True:
    dest.announce()
    RNS.log("Announce dikirim")
    time.sleep(30)
