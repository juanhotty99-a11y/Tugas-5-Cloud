import RNS, sys, time
APP_NAME = "tugas5"

reticulum = RNS.Reticulum()
dest_hash = bytes.fromhex(sys.argv[1])   # hash tujuan dari Node B
pesan     = sys.argv[2] if len(sys.argv) > 2 else "Halo dari Node A!"

if not RNS.Transport.has_path(dest_hash):
    RNS.log("Path belum ada, mengirim path request...")
    RNS.Transport.request_path(dest_hash)
    while not RNS.Transport.has_path(dest_hash):
        time.sleep(0.1)

identity_b = RNS.Identity.recall(dest_hash)
dest_b = RNS.Destination(identity_b, RNS.Destination.OUT,
                         RNS.Destination.SINGLE, APP_NAME, "pesan")
packet = RNS.Packet(dest_b, pesan.encode("utf-8"))
receipt = packet.send()
RNS.log("Pesan dikirim ke " + RNS.prettyhexrep(dest_hash))

def delivered(r):
    RNS.log("Pesan terkonfirmasi diterima Node B (RTT %.3f s)" % r.get_rtt())
receipt.set_delivery_callback(delivered)
time.sleep(5)
