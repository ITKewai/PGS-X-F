from __future__ import annotations

import ipaddress
import os
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class AutoIpAddresses:
    """Indirizzi ricavati dalla porta Ethernet attiva."""

    pc_ip: str
    hmi_ip: str
    plc_ip: str


_PRIVATE_NETWORKS = (
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.168.0.0/16"),
)


def derive_hmi_plc_addresses(pc_ip: str) -> AutoIpAddresses:
    """
    Applica la convenzione di rete della macchina all'ultimo ottetto:

        PC  = x.y.z.N
        HMI = x.y.z.(N - 10)
        PLC = x.y.z.(N - 12)  # altri 2 nodi sotto l'HMI

    Esempio: 10.3.45.13 -> HMI 10.3.45.3 -> PLC 10.3.45.1.
    """
    try:
        ip = ipaddress.IPv4Address(pc_ip.strip())
    except ipaddress.AddressValueError as exc:
        raise ValueError(f"Indirizzo IPv4 non valido: {pc_ip!r}") from exc

    octets = [int(part) for part in str(ip).split(".")]
    pc_node = octets[3]

    if pc_node < 13:
        raise ValueError(
            f"Impossibile calcolare HMI e PLC da {ip}: "
            "l'ultimo ottetto deve essere almeno 13."
        )

    prefix = ".".join(str(part) for part in octets[:3])
    hmi_ip = f"{prefix}.{pc_node - 10}"
    plc_ip = f"{prefix}.{pc_node - 12}"

    return AutoIpAddresses(pc_ip=str(ip), hmi_ip=hmi_ip, plc_ip=plc_ip)


def _parse_ipv4_lines(text: str) -> list[str]:
    result: list[str] = []
    for raw_line in text.splitlines():
        value = raw_line.strip().strip('"').strip()
        if not value:
            continue
        try:
            ip = ipaddress.IPv4Address(value)
        except ipaddress.AddressValueError:
            continue
        result.append(str(ip))
    return result


def _run_command(command: list[str], timeout: float = 6.0) -> str:
    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            creationflags=creationflags,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""

    if completed.returncode != 0:
        return ""
    return completed.stdout or ""


def _windows_active_ethernet_ipv4() -> list[str]:
    """Legge gli IPv4 delle schede Ethernet fisiche attive tramite PowerShell."""
    scripts = (
        # Percorso principale: MediaType 802.3 identifica Ethernet cablata.
        """
        Get-NetIPConfiguration |
          Where-Object {
            $_.NetAdapter.Status -eq 'Up' -and
            $_.NetAdapter.HardwareInterface -eq $true -and
            $_.NetAdapter.MediaType -eq '802.3' -and
            $_.IPv4Address
          } |
          ForEach-Object {
            $_.IPv4Address | ForEach-Object { $_.IPAddress }
          }
        """,
        # Fallback per driver che non valorizzano MediaType correttamente.
        """
        Get-NetAdapter -Physical |
          Where-Object {
            $_.Status -eq 'Up' -and
            $_.InterfaceDescription -notmatch 'Wireless|Wi-Fi|WLAN|Bluetooth'
          } |
          ForEach-Object {
            Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
              Where-Object { $_.AddressState -eq 'Preferred' } |
              Select-Object -ExpandProperty IPAddress
          }
        """,
    )

    for script in scripts:
        output = _run_command(
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ]
        )
        addresses = _parse_ipv4_lines(output)
        if addresses:
            return addresses

    return []


def _linux_active_ethernet_ipv4() -> list[str]:
    """Fallback Linux: interfacce UP non loopback e non wireless."""
    sys_net = Path("/sys/class/net")
    if not sys_net.exists():
        return []

    result: list[str] = []
    for interface in sorted(sys_net.iterdir()):
        name = interface.name
        if name == "lo" or (interface / "wireless").exists():
            continue

        try:
            if (interface / "operstate").read_text(encoding="utf-8").strip() != "up":
                continue
        except OSError:
            continue

        output = _run_command(
            ["ip", "-o", "-4", "addr", "show", "dev", name, "scope", "global"]
        )
        for line in output.splitlines():
            parts = line.split()
            try:
                inet_index = parts.index("inet")
                result.append(parts[inet_index + 1].split("/", 1)[0])
            except (ValueError, IndexError):
                continue

    return result


def _generic_ipv4_fallback() -> list[str]:
    """Ultimo fallback senza dipendenze esterne."""
    result: list[str] = []

    # L'UDP connect non invia pacchetti: serve solo a chiedere allo stack IP
    # quale indirizzo locale userebbe per una destinazione privata.
    for destination in (("10.255.255.255", 9), ("192.168.255.255", 9)):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(destination)
            result.append(sock.getsockname()[0])
        except OSError:
            pass
        finally:
            sock.close()

    try:
        for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            result.append(item[4][0])
    except OSError:
        pass

    return result


def _is_usable_ipv4(value: str) -> bool:
    try:
        ip = ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        return False

    return not (
        ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_unspecified
        or ip.is_reserved
    )


def _deduplicate(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not _is_usable_ipv4(value):
            continue
        normalized = str(ipaddress.IPv4Address(value))
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def discover_active_ethernet_ipv4() -> list[str]:
    """
    Restituisce gli IPv4 candidati della porta Ethernet attiva.

    Su Windows usa le API di rete via PowerShell; su Linux legge le interfacce
    fisiche UP. Solo come ultimo fallback usa gli indirizzi locali generici.
    """
    if os.name == "nt":
        addresses = _windows_active_ethernet_ipv4()
    elif os.name == "posix":
        addresses = _linux_active_ethernet_ipv4()
    else:
        addresses = []

    if not addresses:
        addresses = _generic_ipv4_fallback()

    return _deduplicate(addresses)


def _private_rank(ip_value: str) -> int:
    ip = ipaddress.IPv4Address(ip_value)
    for index, network in enumerate(_PRIVATE_NETWORKS):
        if ip in network:
            return index
    return len(_PRIVATE_NETWORKS)


def _plc_is_reachable(ip_value: str, timeout: float = 0.35) -> bool:
    for port in (443, 80):
        try:
            with socket.create_connection((ip_value, port), timeout=timeout):
                return True
        except OSError:
            continue
    return False


def get_auto_ip_addresses() -> AutoIpAddresses:
    """
    Seleziona la scheda Ethernet più probabile e calcola PC/HMI/PLC.

    Se ci sono più schede, preferisce un PLC raggiungibile su HTTPS/HTTP e poi
    gli indirizzi di rete privata nell'ordine 10/8, 172.16/12, 192.168/16.
    """
    candidates = discover_active_ethernet_ipv4()
    if not candidates:
        raise RuntimeError("Nessuna porta Ethernet attiva con indirizzo IPv4 trovata.")

    derived: list[AutoIpAddresses] = []
    errors: list[str] = []
    for candidate in candidates:
        try:
            derived.append(derive_hmi_plc_addresses(candidate))
        except ValueError as exc:
            errors.append(str(exc))

    if not derived:
        detail = f" Dettagli: {'; '.join(errors)}" if errors else ""
        raise RuntimeError(f"Nessun indirizzo Ethernet utilizzabile.{detail}")

    derived.sort(
        key=lambda item: (
            0 if _plc_is_reachable(item.plc_ip) else 1,
            _private_rank(item.pc_ip),
            tuple(int(part) for part in item.pc_ip.split(".")),
        )
    )
    return derived[0]
