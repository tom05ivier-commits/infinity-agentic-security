// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
//
// Aturan YARA untuk deteksi laboratorium. File ini bersifat contoh dan aman.

rule EICAR_Test_File
{
    meta:
        description = "Deteksi berkas uji antivirus standar EICAR"
        severity = "critical"
        license = "Tom05ivier-commits-1.0"
    strings:
        $eicar = "EICAR-STANDARD-ANTIVIRUS-TEST-FILE"
    condition:
        $eicar
}

rule Suspicious_Script_Patterns
{
    meta:
        description = "Pola skrip mencurigakan untuk tinjauan analyst"
        severity = "medium"
    strings:
        $a = "os.system("
        $b = "subprocess.Popen("
        $c = "/dev/tcp/"
        $d = "base64.b64decode("
    condition:
        2 of them
}
