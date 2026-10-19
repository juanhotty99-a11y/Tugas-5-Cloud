"""
Soal 2.d - Node A (pengirim)
Mencari path ke Node B lalu mengirim pesan dan menunggu bukti diterima.

Jalankan:
    python src/node_a_pengirim.py                          # hash dibaca dari data/node_b_hash.txt
    python src/node_a_pengirim.py <hash_node_b>            # hash diberikan manual
    python src/node_a_pengirim.py <hash_node_b> "Pesan"    # hash dan isi pesan
"""
import os, sys, time
import RNS

APP_NAME = "tugas5"
TIMEOUT = 30  # detik

HASH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "node_b_hash.txt")


def baca_hash_node_b():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip().strip("<>")
    # Tunggu sebentar kalau Node B baru saja dijalankan bersamaan
    batas = time.time() + TIMEOUT
    while not os.path.isfile(HASH_FILE):
        if time.time() > batas:
            sys.exit("Hash Node B tidak ditemukan. Jalankan Node B dulu "
                     "atau berikan hash sebagai argumen.")
        time.sleep(0.5)
    with open(HASH_FILE) as f:
        return f.read().strip()


def main():
    hash_hex = baca_hash_node_b()
    pesan = sys.argv[2] if len(sys.argv) > 2 else "Halo dari Node A!"

    try:
        dest_hash = bytes.fromhex(hash_hex)
    except ValueError:
        sys.exit("Hash tidak valid: " + hash_hex)
    if len(dest_hash) != RNS.Reticulum.TRUNCATED_HASHLENGTH // 8:
        sys.exit("Panjang hash harus 32 karakter heksadesimal: " + hash_hex)

    RNS.Reticulum()

    if not RNS.Transport.has_path(dest_hash):
        RNS.log("Path belum ada, mengirim path request...")
        RNS.Transport.request_path(dest_hash)
        batas = time.time() + TIMEOUT
        while not RNS.Transport.has_path(dest_hash):
            if time.time() > batas:
                sys.exit("Path ke Node B tidak ditemukan. Pastikan Node B sedang berjalan.")
            time.sleep(0.1)

    identity_b = RNS.Identity.recall(dest_hash)
    dest_b = RNS.Destination(identity_b, RNS.Destination.OUT,
                             RNS.Destination.SINGLE, APP_NAME, "pesan")

    selesai = {"status": None}

    def delivered(r):
        RNS.log("Pesan terkonfirmasi diterima Node B (RTT %.3f s)" % r.get_rtt())
        selesai["status"] = True

    def gagal(r):
        RNS.log("Pesan gagal dikirim (timeout)")
        selesai["status"] = False

    packet = RNS.Packet(dest_b, pesan.encode("utf-8"))
    receipt = packet.send()
    receipt.set_delivery_callback(delivered)
    receipt.set_timeout_callback(gagal)
    RNS.log("Pesan dikirim ke " + RNS.prettyhexrep(dest_hash))

    batas = time.time() + TIMEOUT
    while selesai["status"] is None and time.time() < batas:
        time.sleep(0.1)
    sys.exit(0 if selesai["status"] else 1)


if __name__ == "__main__":
    main()
