# recon2023-resources

# Tools

- [Ghidra 10.3](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_10.3_build) 
  - [Install Instructions](https://github.com/NationalSecurityAgency/ghidra/tree/master#install)
- Ghidra Extensions:
  - [PatchDiffCorrelator](https://github.com/clearbluejar/ghidra-patchdiff-correlator/releases)
    - [Install Instructions](https://github.com/clearbluejar/ghidra-patchdiff-correlator#how-do-i-install-it)
- [VS code](https://code.visualstudio.com/download)
- [VS Code Diff settings.json](vscode/settings.json)
- [ghidra_scripts](ghidra_scripts/)

## VM Option

- [lubuntu-22.04-patch-diff-dark.ova](https://drive.google.com/file/d/1047X50u3XLSRwwI6L2XeNu2YvZe1sko8/view?usp=sharing)

# Exercise 1 - CVE-2023-21768

- vulnerable (N-1): [afd.sys.10.0.22621.1028](CVE-2023-21768/afd.sys.10.0.22621.1028)
- patched: [afd.sys.10.0.22621.1415](CVE-2023-21768/afd.sys.10.0.22621.1415)
- Ghidra Analyzed Project
  - [CVE-2023-21768.gar](https://github.com/clearbluejar/recon2023-resources/releases/download/v1.0.0/CVE-2023-21768.gar)

# Exercise 2 - CVE-2022-34690

- vulnerable (N-1): [fxsroute.dll.x64.10.0.22000.795](CVE-2022-34690/fxsroute.dll.x64.10.0.22000.795)
- patched: [fxsroute.dll.x64.10.0.22000.856](CVE-2022-34690/fxsroute.dll.x64.10.0.22000.856)
- Ghidra Analyzed Project
  - [CVE-2022-34690.gar](https://github.com/clearbluejar/recon2023-resources/releases/download/v1.0.0/CVE-2022-34690.gar)

# Exercise 3 - CVE-2023-28302

- vulnerable (N-1): [mqqm.dll.x64.10.0.17763.3770](CVE-2023-28302/mqqm.dll.x64.10.0.17763.3770)
- patched: [mqqm.dll.x64.10.0.17763.4252](CVE-2023-28302/mqqm.dll.x64.10.0.17763.4252)
- Ghidra Analyzed Project
  - [CVE-2023-28302.gar](https://github.com/clearbluejar/recon2023-resources/releases/download/v1.0.0/CVE-2023-28302.gar)

# Exercise 4 - CVE-2022-36934

- vulnerable (N-1): [com.whatsapp.2.22.16.11.libwhatsapp.so](CVE-2022-36934/com.whatsapp.2.22.16.11.libwhatsapp.so)
- patched: [com.whatsapp.2.22.16.12.libwhatsapp.so](CVE-2022-36934/com.whatsapp.2.22.16.12.libwhatsapp.so)
- Ghidra Analyzed Project
  - [CVE-2022-36934.gar](https://github.com/clearbluejar/recon2023-resources/releases/download/v1.0.0/CVE-2022-36934.gar)