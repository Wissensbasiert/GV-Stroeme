"""Windows-DPAPI lesen; Schlüssel bleibt ausschließlich im Arbeitsspeicher."""
import ctypes
import json
import os
from pathlib import Path
from ctypes import wintypes


class Blob(ctypes.Structure):
    _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]


def load_local_requesty():
    if os.name != 'nt':
        raise RuntimeError('Lokale DPAPI-Konfiguration ist nur unter Windows verfügbar')
    folder = Path(os.environ['LOCALAPPDATA']) / 'WBP-Solutions/Gueterstroeme/Requesty'
    config = json.loads((folder / 'config.json').read_text(encoding='utf-8'))
    if config.get('eu_routing_confirmed') is not True:
        raise RuntimeError('EU-Routing ist nicht bestätigt')
    encrypted = (folder / 'key.dpapi').read_bytes()
    buffer = (ctypes.c_ubyte * len(encrypted)).from_buffer_copy(encrypted)
    source, target = Blob(len(encrypted), buffer), Blob()
    crypt = ctypes.WinDLL('crypt32', use_last_error=True)
    crypt.CryptUnprotectData.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                                       ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    crypt.CryptUnprotectData.restype = wintypes.BOOL
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if not crypt.CryptUnprotectData(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise RuntimeError('Requesty-Schlüssel lässt sich mit diesem Windows-Konto nicht entschlüsseln')
    try:
        key = ctypes.string_at(target.data, target.size).decode('utf-8')
    finally:
        ctypes.memset(target.data, 0, target.size)
        kernel.LocalFree(target.data)
    from .requesty import Requesty
    return Requesty(model=config['model'], base_url=config['base_url'], api_key=key,
                    timeout_seconds=config['timeout_seconds'], max_tokens=config['max_tokens'])
