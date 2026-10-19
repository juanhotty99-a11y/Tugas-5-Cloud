"""
Soal 1 - Logical Clock
Menghitung Lamport timestamp (1.a), vector clock (1.b), dan menentukan
apakah event c dan g konkuren atau happens-before (1.c).

Jalankan: python src/soal1_logical_clock.py
"""


# ---------------------------------------------------------------------------
# 1.a Lamport timestamp
# ---------------------------------------------------------------------------
# Setiap proses berisi daftar event berurutan. Event berupa tuple:
#   (nama, jenis, nilai)
#   jenis "init"  : event awal dengan nilai clock yang sudah diketahui
#   jenis "local" : event lokal / kirim  -> LC = LC + 1
#   jenis "recv"  : terima pesan dari event `nilai` -> LC = max(LC, t) + 1
LAMPORT_PROSES = {
    "P0": [("P0_awal", "init", 5), ("a", "local", None), ("b", "recv", "P1_awal")],
    "P1": [("P1_awal", "init", 1), ("c", "recv", "P0_awal"), ("d", "local", None), ("e", "recv", "a")],
    "P2": [("P2_awal", "init", 1), ("f", "recv", "e")],
}


def hitung_lamport(proses):
    ts = {}
    posisi = {p: 0 for p in proses}
    clock = {p: 0 for p in proses}
    langkah = []

    # Proses event secara bergiliran; event "recv" baru bisa diproses
    # setelah event pengirimnya sudah punya timestamp.
    while any(posisi[p] < len(proses[p]) for p in proses):
        maju = False
        for p, events in proses.items():
            if posisi[p] >= len(events):
                continue
            nama, jenis, nilai = events[posisi[p]]
            if jenis == "init":
                clock[p] = nilai
                ket = f"event awal = {nilai}"
            elif jenis == "local":
                lama = clock[p]
                clock[p] += 1
                ket = f"{lama} + 1 = {clock[p]}"
            else:
                if nilai not in ts:
                    continue
                t = ts[nilai]
                lama = clock[p]
                clock[p] = max(lama, t) + 1
                ket = f"terima dari {nilai} (t={t}) -> max({lama}, {t}) + 1 = {clock[p]}"
            ts[nama] = clock[p]
            langkah.append(f"  {p}: {nama:8s} {ket}")
            posisi[p] += 1
            maju = True
        if not maju:
            raise RuntimeError("Diagram tidak valid: ada pesan yang menunggu selamanya")
    return ts, langkah


# ---------------------------------------------------------------------------
# 1.b Vector clock
# ---------------------------------------------------------------------------
# Urutan vektor: [P1, P2, P3]
#   jenis "local" : event lokal / kirim
#   jenis "recv"  : terima pesan dari event `nilai`
VECTOR_PROSES = {
    "P1": [("a", "local", None), ("b", "local", None)],
    "P2": [("c", "recv", "a"), ("d", "recv", "g")],
    "P3": [("e", "local", None), ("f", "recv", "b"), ("g", "local", None)],
}


def hitung_vector_clock(proses):
    nama_proses = list(proses)
    idx = {p: i for i, p in enumerate(nama_proses)}
    vc = {p: [0] * len(nama_proses) for p in proses}
    ts = {}
    posisi = {p: 0 for p in proses}
    langkah = []

    while any(posisi[p] < len(proses[p]) for p in proses):
        maju = False
        for p, events in proses.items():
            if posisi[p] >= len(events):
                continue
            nama, jenis, nilai = events[posisi[p]]
            if jenis == "recv":
                if nilai not in ts:
                    continue
                lama = list(vc[p])
                vc[p] = [max(x, y) for x, y in zip(vc[p], ts[nilai])]
                vc[p][idx[p]] += 1
                ket = f"max({lama}, {ts[nilai]}) lalu {p}+1 = {vc[p]}"
            else:
                vc[p][idx[p]] += 1
                ket = f"{vc[p]}"
            ts[nama] = list(vc[p])
            langkah.append(f"  {p}: {nama}  {ket}")
            posisi[p] += 1
            maju = True
        if not maju:
            raise RuntimeError("Diagram tidak valid: ada pesan yang menunggu selamanya")
    return ts, langkah


# ---------------------------------------------------------------------------
# 1.c Konkuren atau happens-before
# ---------------------------------------------------------------------------
def happens_before(v1, v2):
    return all(x <= y for x, y in zip(v1, v2)) and any(x < y for x, y in zip(v1, v2))


def hubungan(nama1, v1, nama2, v2):
    if happens_before(v1, v2):
        return f"{nama1} -> {nama2} ({nama1} happens-before {nama2})"
    if happens_before(v2, v1):
        return f"{nama2} -> {nama1} ({nama2} happens-before {nama1})"
    return f"{nama1} || {nama2} (KONKUREN)"


def main():
    print("=" * 60)
    print("1.a Lamport timestamp")
    print("=" * 60)
    lamport, langkah = hitung_lamport(LAMPORT_PROSES)
    print("\n".join(langkah))
    print("Hasil:", ", ".join(f"{e} = {lamport[e]}" for e in "abcdef"))

    print()
    print("=" * 60)
    print("1.b Vector clock  (urutan [P1, P2, P3])")
    print("=" * 60)
    vector, langkah = hitung_vector_clock(VECTOR_PROSES)
    print("\n".join(langkah))
    print("Hasil:", ", ".join(f"{e} = {vector[e]}" for e in "abcdefg"))

    print()
    print("=" * 60)
    print("1.c Event c dan event g")
    print("=" * 60)
    vc_c, vc_g = vector["c"], vector["g"]
    print(f"  VC(c) = {vc_c}, VC(g) = {vc_g}")
    for i, (x, y) in enumerate(zip(vc_c, vc_g)):
        tanda = "<" if x < y else (">" if x > y else "=")
        print(f"  P{i + 1}: {x} {tanda} {y}")
    print("  Kesimpulan:", hubungan("c", vc_c, "g", vc_g))


if __name__ == "__main__":
    main()
