"""
Module de pré-analyse statique de la configuration réseau Cisco.
Extrait les méta-données clés (VLANs, interfaces, ACL, routes) AVANT
d'envoyer la config au LLM, pour enrichir l'affichage et valider l'entrée.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class NetworkMeta:
    """Méta-données extraites statiquement de la config Cisco."""
    hostname: str = ""
    vlans: list[dict] = field(default_factory=list)          # [{id, name}]
    interfaces: list[dict] = field(default_factory=list)     # [{name, mode, vlan}]
    acl_ids: list[str] = field(default_factory=list)
    static_routes: list[str] = field(default_factory=list)
    is_empty: bool = True


def parse_cisco_config(config: str) -> NetworkMeta:
    """
    Parse une configuration Cisco (show running-config) et extrait les éléments
    importants sans appel réseau.

    Parameters
    ----------
    config: Texte brut de la configuration Cisco.

    Returns
    -------
    NetworkMeta avec les champs extraits.
    """
    meta = NetworkMeta()

    if not config or not config.strip():
        return meta

    meta.is_empty = False
    lines = config.splitlines()

    current_iface: dict | None = None
    current_vlan_id: str | None = None

    for line in lines:
        stripped = line.strip()

        # Hostname
        m = re.match(r"^hostname\s+(\S+)", stripped, re.IGNORECASE)
        if m:
            meta.hostname = m.group(1)
            continue

        # Début de bloc VLAN (global)
        m = re.match(r"^vlan\s+(\d+)", stripped, re.IGNORECASE)
        if m:
            current_vlan_id = m.group(1)
            meta.vlans.append({"id": current_vlan_id, "name": ""})
            current_iface = None
            continue

        # Nom du VLAN
        m = re.match(r"^\s*name\s+(\S+)", line, re.IGNORECASE)
        if m and current_vlan_id:
            for v in reversed(meta.vlans):
                if v["id"] == current_vlan_id:
                    v["name"] = m.group(1)
                    break
            continue

        # Début d'interface
        m = re.match(r"^interface\s+(\S+)", stripped, re.IGNORECASE)
        if m:
            current_iface = {"name": m.group(1), "mode": "", "vlan": ""}
            meta.interfaces.append(current_iface)
            current_vlan_id = None
            continue

        # Mode switchport
        if current_iface:
            m = re.match(r"^\s*switchport mode\s+(\S+)", line, re.IGNORECASE)
            if m:
                current_iface["mode"] = m.group(1)
                continue

            m = re.match(r"^\s*switchport access vlan\s+(\d+)", line, re.IGNORECASE)
            if m:
                current_iface["vlan"] = m.group(1)
                continue

            m = re.match(r"^\s*switchport trunk allowed vlan\s+(.+)", line, re.IGNORECASE)
            if m:
                current_iface["vlan"] = f"trunk:{m.group(1).strip()}"
                continue

        # ACL
        m = re.match(r"^(?:ip\s+)?access-list\s+(\S+)", stripped, re.IGNORECASE)
        if m:
            acl_id = m.group(1)
            if acl_id not in meta.acl_ids:
                meta.acl_ids.append(acl_id)
            continue

        # ACL numérotée (access-list 101 ...)
        m = re.match(r"^access-list\s+(\d+)\s+", stripped, re.IGNORECASE)
        if m:
            acl_id = m.group(1)
            if acl_id not in meta.acl_ids:
                meta.acl_ids.append(acl_id)
            continue

        # Routes statiques
        m = re.match(r"^ip route\s+(.+)", stripped, re.IGNORECASE)
        if m:
            meta.static_routes.append(m.group(1).strip())
            continue

    return meta


def format_meta_as_text(meta: NetworkMeta) -> str:
    """Retourne un résumé lisible des méta-données extraites (pour debug/log)."""
    lines = []
    if meta.hostname:
        lines.append(f"Hostname : {meta.hostname}")
    if meta.vlans:
        lines.append(f"VLANs ({len(meta.vlans)}) : " + ", ".join(
            f"{v['id']} ({v['name']})" if v["name"] else v["id"]
            for v in meta.vlans
        ))
    if meta.interfaces:
        lines.append(f"Interfaces ({len(meta.interfaces)}) : " + ", ".join(
            i["name"] for i in meta.interfaces
        ))
    if meta.acl_ids:
        lines.append(f"ACL : {', '.join(meta.acl_ids)}")
    if meta.static_routes:
        lines.append(f"Routes statiques : {len(meta.static_routes)}")
    return "\n".join(lines)
