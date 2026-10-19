"""
Soal 2.d - Node B (penerima)
Membuat destinasi IN, melakukan announce secara berkala, dan menampilkan
setiap pesan yang masuk. Hash tujuan disimpan ke data/node_b_hash.txt
agar Node A bisa langsung membacanya.

Jalankan: python src/node_b_penerima.py   (hentikan dengan Ctrl+C)
"""
import os, signal, time
import RNS

APP_NAME = "tugas5"
ANNOUNCE_INTERVAL = 30  # detik

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
IDENTITY_FILE = os.path.join(DATA_DIR, "node_b_identity")
HASH_FILE = os.path.join(DATA_DIR, "node_b_hash.txt")


def muat_identity():
    # Identity disimpan ke file supaya hash tujuan Node B tetap sama
    # setiap kali program dijalankan ulang.
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.isfile(IDENTITY_FILE):
        return RNS.Identity.from_file(IDENTITY_FILE)
    identity = RNS.Identity()
    identity.to_file(IDENTITY_FILE)
    return identity


def hapus_hash_file():
    if os.path.isfile(HASH_FILE):
        os.remove(HASH_FILE)


def berhenti(signum, frame):
    # RNS keluar lewat os._exit, jadi file hash dihapus di sini dulu
    hapus_hash_file()
    RNS.log("Node B dihentikan")
    RNS.exit()


def on_packet(data, packet):
    RNS.log("Pesan diterima: " + data.decode("utf-8"))


def main():
    # Hapus hash lama; Node A menunggu sampai file ini dibuat ulang,
    # yaitu setelah Reticulum di Node B sudah siap.
    hapus_hash_file()
    RNS.Reticulum()
    signal.signal(signal.SIGINT, berhenti)
    signal.signal(signal.SIGTERM, berhenti)

    identity = muat_identity()
    dest = RNS.Destination(identity, RNS.Destination.IN,
                           RNS.Destination.SINGLE, APP_NAME, "pesan")
    dest.set_packet_callback(on_packet)
    dest.set_proof_strategy(RNS.Destination.PROVE_ALL)

    with open(HASH_FILE, "w") as f:
        f.write(dest.hash.hex())

    RNS.log("Node B siap, hash tujuan: " + RNS.prettyhexrep(dest.hash))
    RNS.log("Hash juga disimpan di " + os.path.normpath(HASH_FILE))
    while True:
        dest.announce()
        RNS.log("Announce dikirim")
        time.sleep(ANNOUNCE_INTERVAL)


if __name__ == "__main__":
    main()
