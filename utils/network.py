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
    """Indirizzi PC, HMI e PLC ricavati dalla porta Ethernet attiva."""

    pc_ip: str
    hmi_ip: str
    plc_ip: str


@dataclass(frozen=True)
class _EthernetCandidate:
    """Indirizzo rilevato su una specifica scheda Ethernet."""

    ip: str
    has_dns: bool


_PRIVATE_NETWORKS = (
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.168.0.0/16"),
)


def derive_hmi_plc_addresses(
    ip_value: str,
    *,
    input_is_hmi: bool = False,
) -> AutoIpAddresses:
    """
    Calcola gli indirizzi PC, HMI e PLC.

    Convenzione della macchina:

        PC  = x.y.z.N
        HMI = x.y.z.(N - 10)
        PLC = x.y.z.(N - 12)

    Se ``input_is_hmi`` è False, l'indirizzo ricevuto è quello del PC:

        IP scheda = PC
        HMI = PC - 10
        PLC = PC - 12

    Se ``input_is_hmi`` è True, l'indirizzo ricevuto è quello dell'HMI:

        IP scheda = HMI
        PC  = HMI + 10
        PLC = HMI - 2

    Esempi:

        10.3.45.13, input_is_hmi=False
        PC  = 10.3.45.13
        HMI = 10.3.45.3
        PLC = 10.3.45.1

        10.3.45.3, input_is_hmi=True
        PC  = 10.3.45.13
        HMI = 10.3.45.3
        PLC = 10.3.45.1
    """
    try:
        interface_ip = ipaddress.IPv4Address(ip_value.strip())
    except ipaddress.AddressValueError as exc:
        raise ValueError(
            f"Indirizzo IPv4 non valido: {ip_value!r}"
        ) from exc

    octets = [int(part) for part in str(interface_ip).split(".")]
    interface_node = octets[3]

    if input_is_hmi:
        if interface_node < 3:
            raise ValueError(
                f"Impossibile calcolare il PLC da {interface_ip}: "
                "l'ultimo ottetto dell'HMI deve essere almeno 3."
            )

        if interface_node > 244:
            raise ValueError(
                f"Impossibile calcolare il PC da {interface_ip}: "
                "l'ultimo ottetto dell'HMI deve essere al massimo 244."
            )

        hmi_node = interface_node
        pc_node = interface_node + 10
        plc_node = interface_node - 2

    else:
        if interface_node < 13:
            raise ValueError(
                f"Impossibile calcolare HMI e PLC da {interface_ip}: "
                "l'ultimo ottetto del PC deve essere almeno 13."
            )

        pc_node = interface_node
        hmi_node = interface_node - 10
        plc_node = interface_node - 12

    prefix = ".".join(str(part) for part in octets[:3])

    return AutoIpAddresses(
        pc_ip=f"{prefix}.{pc_node}",
        hmi_ip=f"{prefix}.{hmi_node}",
        plc_ip=f"{prefix}.{plc_node}",
    )


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


def _parse_ipv4_dns_lines(text: str) -> list[_EthernetCandidate]:
    """
    Legge righe nel formato:

        10.3.45.3|True
        192.168.1.20|False
    """
    result: list[_EthernetCandidate] = []

    for raw_line in text.splitlines():
        value = raw_line.strip().strip('"').strip()
        if not value:
            continue

        ip_text, separator, dns_text = value.partition("|")
        if not separator:
            continue

        try:
            ip = ipaddress.IPv4Address(ip_text.strip())
        except ipaddress.AddressValueError:
            continue

        has_dns = dns_text.strip().lower() in {
            "true",
            "1",
            "yes",
            "si",
            "sì",
        }

        result.append(
            _EthernetCandidate(
                ip=str(ip),
                has_dns=has_dns,
            )
        )

    return result


def _run_command(
    command: list[str],
    timeout: float = 6.0,
) -> str:
    creationflags = 0

    if os.name == "nt":
        creationflags = getattr(
            subprocess,
            "CREATE_NO_WINDOW",
            0,
        )

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


def _windows_active_ethernet_ipv4() -> list[_EthernetCandidate]:
    """
    Legge gli IPv4 delle schede Ethernet fisiche attive tramite PowerShell.

    Per ogni scheda verifica se è configurato almeno un server DNS IPv4.

    Regola applicata successivamente:

    - DNS presente: l'IP della scheda è considerato quello dell'HMI;
    - DNS assente: l'IP della scheda è considerato quello del PC.
    """
    scripts = (
        # Percorso principale:
        # MediaType 802.3 identifica normalmente Ethernet cablata.
        r"""
        Get-NetIPConfiguration |
          Where-Object {
            $_.NetAdapter.Status -eq 'Up' -and
            $_.NetAdapter.HardwareInterface -eq $true -and
            $_.NetAdapter.MediaType -eq '802.3' -and
            $_.IPv4Address
          } |
          ForEach-Object {
            $config = $_
            $interfaceIndex = $config.NetAdapter.ifIndex

            $dnsServers = @(
              Get-DnsClientServerAddress `
                -InterfaceIndex $interfaceIndex `
                -AddressFamily IPv4 `
                -ErrorAction SilentlyContinue |
              ForEach-Object {
                $_.ServerAddresses
              } |
              Where-Object {
                $_ -and
                $_ -ne '0.0.0.0' -and
                $_ -notmatch '^127\.'
              }
            )

            $hasDns = $dnsServers.Count -gt 0

            $config.IPv4Address |
              ForEach-Object {
                "{0}|{1}" -f $_.IPAddress, $hasDns
              }
          }
        """,
        # Fallback per driver che non valorizzano MediaType.
        r"""
        Get-NetAdapter -Physical |
          Where-Object {
            $_.Status -eq 'Up' -and
            $_.InterfaceDescription -notmatch
              'Wireless|Wi-Fi|WLAN|Bluetooth'
          } |
          ForEach-Object {
            $adapter = $_
            $interfaceIndex = $adapter.ifIndex

            $dnsServers = @(
              Get-DnsClientServerAddress `
                -InterfaceIndex $interfaceIndex `
                -AddressFamily IPv4 `
                -ErrorAction SilentlyContinue |
              ForEach-Object {
                $_.ServerAddresses
              } |
              Where-Object {
                $_ -and
                $_ -ne '0.0.0.0' -and
                $_ -notmatch '^127\.'
              }
            )

            $hasDns = $dnsServers.Count -gt 0

            Get-NetIPAddress `
              -InterfaceIndex $interfaceIndex `
              -AddressFamily IPv4 `
              -ErrorAction SilentlyContinue |
              Where-Object {
                $_.AddressState -eq 'Preferred'
              } |
              ForEach-Object {
                "{0}|{1}" -f $_.IPAddress, $hasDns
              }
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

        candidates = _parse_ipv4_dns_lines(output)
        if candidates:
            return candidates

    return []


def _linux_interface_has_dns(interface_name: str) -> bool:
    """
    Verifica se una specifica interfaccia Linux ha almeno un DNS IPv4.

    Prova prima resolvectl e poi NetworkManager tramite nmcli.
    """
    output = _run_command(
        ["resolvectl", "dns", interface_name],
        timeout=2.0,
    )

    for token in output.replace(":", " ").split():
        try:
            dns_ip = ipaddress.IPv4Address(token.strip())
        except ipaddress.AddressValueError:
            continue

        if not dns_ip.is_unspecified and not dns_ip.is_loopback:
            return True

    output = _run_command(
        [
            "nmcli",
            "-g",
            "IP4.DNS",
            "device",
            "show",
            interface_name,
        ],
        timeout=2.0,
    )

    for raw_line in output.splitlines():
        value = raw_line.strip()
        if not value:
            continue

        try:
            dns_ip = ipaddress.IPv4Address(value)
        except ipaddress.AddressValueError:
            continue

        if not dns_ip.is_unspecified and not dns_ip.is_loopback:
            return True

    return False


def _linux_active_ethernet_ipv4() -> list[_EthernetCandidate]:
    """
    Legge gli IPv4 delle interfacce Linux attive, non loopback
    e non wireless.
    """
    sys_net = Path("/sys/class/net")
    if not sys_net.exists():
        return []

    result: list[_EthernetCandidate] = []

    for interface in sorted(sys_net.iterdir()):
        name = interface.name

        if name == "lo":
            continue

        if (interface / "wireless").exists():
            continue

        try:
            operstate = (
                interface / "operstate"
            ).read_text(
                encoding="utf-8"
            ).strip()
        except OSError:
            continue

        if operstate != "up":
            continue

        has_dns = _linux_interface_has_dns(name)

        output = _run_command(
            [
                "ip",
                "-o",
                "-4",
                "addr",
                "show",
                "dev",
                name,
                "scope",
                "global",
            ]
        )

        for line in output.splitlines():
            parts = line.split()

            try:
                inet_index = parts.index("inet")
                ip_value = parts[inet_index + 1].split("/", 1)[0]
            except (ValueError, IndexError):
                continue

            result.append(
                _EthernetCandidate(
                    ip=ip_value,
                    has_dns=has_dns,
                )
            )

    return result


def _generic_ipv4_fallback() -> list[str]:
    """Ultimo fallback senza dipendenze esterne."""
    result: list[str] = []

    # UDP connect non invia necessariamente pacchetti.
    # Serve per chiedere allo stack quale indirizzo locale
    # userebbe per raggiungere la destinazione.
    destinations = (
        ("10.255.255.255", 9),
        ("192.168.255.255", 9),
    )

    for destination in destinations:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        try:
            sock.connect(destination)
            result.append(sock.getsockname()[0])
        except OSError:
            pass
        finally:
            sock.close()

    try:
        addresses = socket.getaddrinfo(
            socket.gethostname(),
            None,
            socket.AF_INET,
        )

        for item in addresses:
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


def _deduplicate_candidates(
    values: Iterable[_EthernetCandidate],
) -> list[_EthernetCandidate]:
    """
    Rimuove i duplicati mantenendo l'informazione DNS.

    Se lo stesso IP viene trovato più volte, has_dns è True
    quando almeno uno dei rilevamenti ha un DNS.
    """
    result: dict[str, _EthernetCandidate] = {}

    for candidate in values:
        if not _is_usable_ipv4(candidate.ip):
            continue

        normalized = str(
            ipaddress.IPv4Address(candidate.ip)
        )

        existing = result.get(normalized)

        result[normalized] = _EthernetCandidate(
            ip=normalized,
            has_dns=(
                candidate.has_dns
                or (
                    existing.has_dns
                    if existing is not None
                    else False
                )
            ),
        )

    return list(result.values())


def _discover_active_ethernet_candidates(
) -> list[_EthernetCandidate]:
    """
    Restituisce gli indirizzi Ethernet insieme allo stato DNS.
    """
    if os.name == "nt":
        candidates = _windows_active_ethernet_ipv4()
    elif os.name == "posix":
        candidates = _linux_active_ethernet_ipv4()
    else:
        candidates = []

    if not candidates:
        candidates = [
            _EthernetCandidate(
                ip=value,
                has_dns=False,
            )
            for value in _generic_ipv4_fallback()
        ]

    return _deduplicate_candidates(candidates)


def discover_active_ethernet_ipv4() -> list[str]:
    """
    Restituisce gli IPv4 candidati della porta Ethernet attiva.

    Su Windows usa PowerShell.
    Su Linux legge le interfacce fisiche UP.
    Come ultimo fallback usa gli indirizzi locali generici.

    Questa funzione restituisce solo gli IP per mantenere
    compatibilità con il codice precedente.
    """
    return [
        candidate.ip
        for candidate in _discover_active_ethernet_candidates()
    ]


def _private_rank(ip_value: str) -> int:
    ip = ipaddress.IPv4Address(ip_value)

    for index, network in enumerate(_PRIVATE_NETWORKS):
        if ip in network:
            return index

    return len(_PRIVATE_NETWORKS)


def _plc_is_reachable(
    ip_value: str,
    timeout: float = 0.35,
) -> bool:
    """
    Controlla se il PLC risponde sulle porte HTTP o HTTPS.
    """
    for port in (443, 80):
        try:
            with socket.create_connection(
                (ip_value, port),
                timeout=timeout,
            ):
                return True
        except OSError:
            continue

    return False


def get_auto_ip_addresses() -> AutoIpAddresses:
    """
    Seleziona la scheda Ethernet più probabile e calcola PC/HMI/PLC.

    Regola:

    - se la scheda ha un DNS configurato, il suo IP è quello dell'HMI;
    - se la scheda non ha DNS, il suo IP è quello del PC.

    Se ci sono più schede:

    1. preferisce quella il cui PLC è raggiungibile;
    2. preferisce reti private nell'ordine:
       10/8, 172.16/12, 192.168/16;
    3. usa l'IP numericamente più basso.
    """
    candidates = _discover_active_ethernet_candidates()

    if not candidates:
        raise RuntimeError(
            "Nessuna porta Ethernet attiva con indirizzo IPv4 trovata."
        )

    derived: list[AutoIpAddresses] = []
    errors: list[str] = []

    for candidate in candidates:
        try:
            addresses = derive_hmi_plc_addresses(
                candidate.ip,
                input_is_hmi=candidate.has_dns,
            )
            derived.append(addresses)

        except ValueError as exc:
            dns_state = (
                "DNS presente"
                if candidate.has_dns
                else "DNS assente"
            )

            errors.append(
                f"{candidate.ip} ({dns_state}): {exc}"
            )

    if not derived:
        detail = (
            f" Dettagli: {'; '.join(errors)}"
            if errors
            else ""
        )

        raise RuntimeError(
            f"Nessun indirizzo Ethernet utilizzabile.{detail}"
        )

    derived.sort(
        key=lambda item: (
            0 if _plc_is_reachable(item.plc_ip) else 1,
            _private_rank(item.pc_ip),
            tuple(
                int(part)
                for part in item.pc_ip.split(".")
            ),
        )
    )

    return derived[0]


if __name__ == "__main__":
    try:
        addresses = get_auto_ip_addresses()

        print(f"PC:  {addresses.pc_ip}")
        print(f"HMI: {addresses.hmi_ip}")
        print(f"PLC: {addresses.plc_ip}")

    except RuntimeError as exc:
        print(f"Errore: {exc}")