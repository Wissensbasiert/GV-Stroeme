"""
pipeline_vp2040.py (High-Speed Multi-Dimensional NUTS-3 Forecast Cube)
Aggregates VP2040 matrices into German NUTS-3 Kreise & European Zones
with full support for Direction, Commodity Groups, Modes, and Metrics.
"""

import os
import json
import time
import shutil
import numpy as np
import pandas as pd

FOREIGN_SEAPORT_COUNTRIES = {
    3160166: "NL", 3160266: "NL", 3160366: "NL",
    3260166: "BE", 3260266: "BE",
    4160166: "FR",
    5360166: "IT", 5360266: "IT", 5360366: "IT", 5360466: "IT", 5360566: "IT",
    5560166: "SI", 5660166: "HR",
    7360166: "PL", 7360266: "PL", 7360366: "PL", 7360466: "PL",
}

def build_vp2040_scenario_bundle(scenario_id, gv_dir):
    """Build the data cube for one VP2040 scenario from its raw matrices."""
    start_time = time.time()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    crosswalk_dir = os.path.join(base_dir, "data", "crosswalks")

    print("[1/5] Loading spatial crosswalks and region names...")
    with open(os.path.join(crosswalk_dir, "crosswalk_spatial_vp2040.json"), 'r', encoding='utf-8') as f:
        spatial_list = json.load(f)

    with open(os.path.join(base_dir, "data", "processed", "web_regions.json"), 'r', encoding='utf-8') as f:
        web_regions = json.load(f)

    with open(os.path.join(crosswalk_dir, "crosswalk_nst_vp2040.json"), 'r', encoding='utf-8') as f:
        nst_list = json.load(f)
    with open(os.path.join(crosswalk_dir, "vp2040_special_cells_nuts3.json"), 'r', encoding='utf-8') as f:
        special_cell_mapping = json.load(f)["cells"]
    gg_to_g7 = {int(item['vp40_code']): str(item['nst2007_group7']) for item in nst_list}
    vp_group_names = {
        str(int(item['vp40_code'])): item['vp40_name']
        for item in nst_list
    }
    vp_group_keys = sorted(vp_group_names, key=int)

    # Map each of the cells to its target NUTS-3 Kreis ID or EU Cell ID
    cell_to_target = {}
    for item in spatial_list:
        cid = int(item['cell_id'])
        nuts = item.get('nuts3_2024') or item.get('nuts3_2016')
        country = item['country_iso2'] or FOREIGN_SEAPORT_COUNTRIES.get(cid, '')
        c_name = item['cell_name']

        if country == 'DE':
            if not nuts:
                mapped_special = special_cell_mapping.get(str(cid))
                if mapped_special:
                    nuts = mapped_special["nuts3_2024"]
                else:
                    s_cid = str(cid)
                    if len(s_cid) == 7 and s_cid.endswith('00'):
                        ags = s_cid[:5]
                        for other in spatial_list:
                            if other.get('ags_5stellig') == ags and (other.get('nuts3_2024') or other.get('nuts3_2016')):
                                nuts = other.get('nuts3_2024') or other.get('nuts3_2016')
                                break
            t_id = nuts or str(cid)
            name = web_regions.get(t_id, {}).get('name', c_name)
            cell_to_target[cid] = {"id": t_id, "name": name, "is_de": True, "country": "DE"}
        else:
            t_id = str(cid)
            name = f"{c_name} ({country})"
            cell_to_target[cid] = {"id": t_id, "name": name, "is_de": False, "country": country}

    # All unique German NUTS-3 districts
    de_nuts_ids = set(web_regions.keys())
    for item in cell_to_target.values():
        if item['is_de']:
            de_nuts_ids.add(item['id'])
    target_names = {str(item['id']): item['name'] for item in cell_to_target.values()}

    unresolved_used_specials = []
    for cell_id, metadata in special_cell_mapping.items():
        target = cell_to_target.get(int(cell_id))
        if not target or target['id'] != metadata['nuts3_2024']:
            unresolved_used_specials.append(cell_id)
    if unresolved_used_specials:
        raise ValueError(f"VP2040-Sonderzellen ohne gültige NUTS-3-Zuordnung: {unresolved_used_specials}")

    scenario_prefixes = {
        "2019_BASE": "2019",
        "2040_P1": "2040P1BP",
    }
    try:
        scenario_prefix = scenario_prefixes[scenario_id]
    except KeyError as exc:
        raise ValueError(f"Unbekanntes VP2040-Szenario: {scenario_id}") from exc

    modes_config = {
        'road': f"VP2040_{scenario_prefix}_GV_Strasse_NUTS3_Matrix_V01.csv",
        'rail': f"VP2040_{scenario_prefix}_GV_Bahn_NUTS3_Matrix_V01.csv",
        'iww': f"VP2040_{scenario_prefix}_GV_Bischi_NUTS3_Matrix_V01.csv"
    }

    print("[2/5] Reading and harmonizing mode matrices...")
    all_dfs = []
    for m_key, fname in modes_config.items():
        fpath = os.path.join(gv_dir, fname)
        if not os.path.isfile(fpath):
            raise FileNotFoundError(f"VP2040-Rohmatrix fehlt: {fpath}")
        print(f"  -> Loading {m_key}: {fname}...")
        df = pd.read_csv(fpath, sep=';', encoding='latin1',
                         usecols=['Quellzelle', 'Zielzelle', 'Guetergruppe', 'VerkArt', 'BehTyp', 'Tonnen', 'Tkm', 'Ladeeinheiten', 'TEU', 'Transportwert'],
                         dtype={'Quellzelle': np.int32, 'Zielzelle': np.int32, 'Guetergruppe': np.int16, 'VerkArt': np.int8, 'BehTyp': np.int8,
                                 'Tonnen': np.float64, 'Tkm': np.float64, 'Ladeeinheiten': np.int32, 'TEU': np.int32, 'Transportwert': np.float64})
        if df.empty:
            raise ValueError(f"VP2040-Rohmatrix enthält keine Datensätze: {fpath}")
        required_measure_columns = ['Quellzelle', 'Zielzelle', 'Guetergruppe', 'Tonnen', 'Tkm']
        if df[required_measure_columns].isna().any().any():
            raise ValueError(f"VP2040-Rohmatrix enthält fehlende Schlüssel- oder Kennzahlwerte: {fpath}")
        
        df['mode'] = m_key
        df['g7'] = df['Guetergruppe'].map(gg_to_g7).fillna("7")
        df['vp_group'] = df['Guetergruppe'].astype(str)
        df['orig_nuts'] = df['Quellzelle'].map(lambda x: cell_to_target.get(x, {}).get('id', str(x)))
        df['dest_nuts'] = df['Zielzelle'].map(lambda x: cell_to_target.get(x, {}).get('id', str(x)))

        all_dfs.append(df)

    full_df = pd.concat(all_dfs, ignore_index=True)
    del all_dfs

    print("[3/5] Computing National Summaries...")
    nat_tonnes_tot = float(full_df['Tonnen'].sum())
    nat_tkm_tot = float(full_df['Tkm'].sum())
    nat_kv_df = full_df[full_df['VerkArt'] == 2]
    nat_kv_tonnes = float(nat_kv_df['Tonnen'].sum())
    nat_le = int(full_df['Ladeeinheiten'].sum())
    nat_teu = int(full_df['TEU'].sum())

    national = {
        "total_tonnes": round(nat_tonnes_tot, 1),
        "total_tkm": round(nat_tkm_tot, 1),
        "total_kv_tonnes": round(nat_kv_tonnes, 1),
        "total_kv_share_pct": round(nat_kv_tonnes / nat_tonnes_tot * 100, 2) if nat_tonnes_tot > 0 else 0,
        "total_ladeeinheiten": nat_le,
        "total_teu": nat_teu,
        "modes": {},
        "modes_by_group": {},
        "nst_groups_7": {},
        "vp2040_groups": {},
        "behtyp_breakdown": {},
        "top_relations": []
    }
    # Modes breakdown national
    for m_key in ['road', 'rail', 'iww']:
        m_df = full_df[full_df['mode'] == m_key]
        m_t = float(m_df['Tonnen'].sum())
        m_tkm = float(m_df['Tkm'].sum())
        m_kv_t = float(m_df[m_df['VerkArt'] == 2]['Tonnen'].sum())
        m_le = int(m_df['Ladeeinheiten'].sum())
        m_teu = int(m_df['TEU'].sum())
        
        national["modes"][m_key] = {
            "tonnes": round(m_t, 1),
            "tkm": round(m_tkm, 1),
            "share_tonnes_pct": round(m_t / nat_tonnes_tot * 100, 1),
            "share_tkm_pct": round(m_tkm / nat_tkm_tot * 100, 1),
            "kv_tonnes": round(m_kv_t, 1),
            "kv_share_pct": round(m_kv_t / m_t * 100, 2) if m_t > 0 else 0,
            "ladeeinheiten": m_le,
            "teu": m_teu
        }

    # The source matrices carry mode and goods group on every row.  Retain
    # their intersection so that a selected NST-7 group can show its actual
    # modal composition instead of the unfiltered all-goods mode totals.
    for g7 in map(str, range(1, 8)):
        national["modes_by_group"][g7] = {
            mode: {"tonnes": 0.0, "tkm": 0.0}
            for mode in ("road", "rail", "iww")
        }
    national_mode_groups = full_df.groupby(["g7", "mode"])[["Tonnen", "Tkm"]].sum().reset_index()
    for row in national_mode_groups.itertuples(index=False):
        group = str(row.g7)
        mode = str(row.mode)
        if group in national["modes_by_group"] and mode in national["modes_by_group"][group]:
            national["modes_by_group"][group][mode] = {
                "tonnes": round(float(row.Tonnen), 1),
                "tkm": round(float(row.Tkm), 1)
            }

    # National NST 7
    for g7_code, g_df in full_df.groupby('g7'):
        g7_str = str(g7_code)
        name = [v["nst2007_group7_name"] for v in nst_list if str(v["nst2007_group7"]) == g7_str]
        national["nst_groups_7"][g7_str] = {
            "id": g7_str,
            "name": name[0] if name else f"Gruppe {g7_str}",
            "tonnes": round(float(g_df['Tonnen'].sum()), 1),
            "tkm": round(float(g_df['Tkm'].sum()), 1)
        }

    # The detailed forecast view deliberately retains the original VP2040
    # goods groups instead of inventing a finer NST-2007 representation.
    for vp_group, group_df in full_df.groupby('vp_group'):
        group_str = str(vp_group)
        national["vp2040_groups"][group_str] = {
            "id": group_str,
            "name": vp_group_names.get(group_str, f"VP2040-Gruppe {group_str}"),
            "tonnes": round(float(group_df['Tonnen'].sum()), 1),
            "tkm": round(float(group_df['Tkm'].sum()), 1)
        }

    # National BehTyp
    behtyp_labels = {
        1: "Container bis 20ft (beladen)",
        2: "Wechselbehälter 25–30ft (beladen)",
        3: "Großcontainer >30ft / 40ft (beladen)",
        4: "Kranbare Sattelauflieger / RoLa (beladen)",
        5: "Container bis 20ft (leer)",
        6: "Wechselbehälter 25–30ft (leer)",
        7: "Großcontainer >30ft / 40ft (leer)",
        8: "Kranbare Sattelauflieger / RoLa (leer)",
        10: "Container 20ft (Beladungszustand nicht differenziert)"
    }
    for bt_code, b_df in full_df[full_df['BehTyp'] > 0].groupby('BehTyp'):
        s_bt = str(bt_code)
        national["behtyp_breakdown"][s_bt] = {
            "behtyp": int(bt_code),
            "name": behtyp_labels.get(int(bt_code), f"Typ {bt_code}"),
            "tonnes": round(float(b_df['Tonnen'].sum()), 1),
            "ladeeinheiten": int(b_df['Ladeeinheiten'].sum()),
            "teu": int(b_df['TEU'].sum())
        }

    print("[4/5] Aggregating regional NUTS-3 districts (Germany)...")
    regions = {}

    for nuts_id in de_nuts_ids:
        r_name = web_regions.get(nuts_id, {}).get('name', nuts_id)
        regions[nuts_id] = {
            "id": nuts_id,
            "name": r_name,
            "tonnes": {"total": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0, "road": 0.0, "rail": 0.0, "iww": 0.0},
            "tkm": {"total": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0, "road": 0.0, "rail": 0.0, "iww": 0.0},
            "directions_tonnes": {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0},
            "directions_tkm": {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0},
            "modes_tonnes": {"road": 0.0, "rail": 0.0, "iww": 0.0},
            "modes_tkm": {"road": 0.0, "rail": 0.0, "iww": 0.0},
            "modes_direction_tonnes": {
                "road": {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0},
                "rail": {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0},
                "iww": {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0}
            },
            "modes_direction_tkm": {
                "road": {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0},
                "rail": {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0},
                "iww": {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0}
            },
            "modes_by_group_tonnes": {
                str(group): {
                    mode: {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0}
                    for mode in ("road", "rail", "iww")
                }
                for group in range(1, 8)
            },
            "modes_by_group_tkm": {
                str(group): {
                    mode: {"all": 0.0, "outbound": 0.0, "inbound": 0.0, "binnen": 0.0, "balance": 0.0}
                    for mode in ("road", "rail", "iww")
                }
                for group in range(1, 8)
            },
            "groups_7_tonnes": {
                direction: {str(i): 0.0 for i in range(1, 8)}
                for direction in ("all", "outbound", "inbound", "binnen", "balance")
            },
            "groups_7_tkm": {
                direction: {str(i): 0.0 for i in range(1, 8)}
                for direction in ("all", "outbound", "inbound", "binnen", "balance")
            },
            "vp2040_groups_tonnes": {
                "all": {key: 0.0 for key in vp_group_keys},
                "outbound": {key: 0.0 for key in vp_group_keys},
                "inbound": {key: 0.0 for key in vp_group_keys},
                "balance": {key: 0.0 for key in vp_group_keys}
            },
            "vp2040_groups_tkm": {
                "all": {key: 0.0 for key in vp_group_keys},
                "outbound": {key: 0.0 for key in vp_group_keys},
                "inbound": {key: 0.0 for key in vp_group_keys},
                "balance": {key: 0.0 for key in vp_group_keys}
            },
            "kv": {"tonnes": 0.0, "share_pct": 0.0, "ladeeinheiten": 0, "teu": 0, "outbound_tonnes": 0.0, "inbound_tonnes": 0.0, "outbound_teu": 0, "inbound_teu": 0},
            "modal_split_tonnes": {"road": 0.0, "rail": 0.0, "iww": 0.0},
            "modal_split_tkm": {"road": 0.0, "rail": 0.0, "iww": 0.0},
            "nst_7": {str(i): 0.0 for i in range(1, 8)},
            "by_group_relations": {str(i): {"all": [], "outbound": [], "inbound": []} for i in range(1, 8)},
            "relations_overall": {"all": [], "outbound": [], "inbound": []},
            "behtyp": {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0, "6": 0.0, "7": 0.0, "8": 0.0}
        }

    # Binnen flows flag
    full_df['is_binnen'] = (full_df['orig_nuts'] == full_df['dest_nuts'])

    # 1. Outbound sums (orig_nuts)
    print("  -> Computing outbound and mode aggregations...")
    # Final modal totals are derived below from Versand + Empfang + Binnenverkehr.
    # They must not be initialized from Versand alone.
    q_out_mode = full_df.groupby(['orig_nuts', 'mode'])[['Tonnen', 'Tkm']].sum().reset_index()
    for row in q_out_mode.itertuples(index=False):
        pass

    # Outbound total & mode directions
    q_out_mode_bin = full_df.groupby(['orig_nuts', 'mode', 'is_binnen'])[['Tonnen', 'Tkm']].sum().reset_index()
    for row in q_out_mode_bin.itertuples(index=False):
        nuts_id = row.orig_nuts
        if nuts_id in regions:
            t = float(row.Tonnen)
            tkm = float(row.Tkm)
            m = row.mode
            is_b = bool(row.is_binnen)

            regions[nuts_id]["modes_direction_tonnes"][m]["all"] += t
            regions[nuts_id]["modes_direction_tkm"][m]["all"] += tkm

            if is_b:
                regions[nuts_id]["tonnes"]["binnen"] += t
                regions[nuts_id]["tkm"]["binnen"] += tkm
                regions[nuts_id]["directions_tonnes"]["binnen"] += t
                regions[nuts_id]["directions_tkm"]["binnen"] += tkm
                regions[nuts_id]["modes_direction_tonnes"][m]["binnen"] += t
                regions[nuts_id]["modes_direction_tkm"][m]["binnen"] += tkm
            else:
                regions[nuts_id]["tonnes"]["outbound"] += t
                regions[nuts_id]["tkm"]["outbound"] += tkm
                regions[nuts_id]["directions_tonnes"]["outbound"] += t
                regions[nuts_id]["directions_tkm"]["outbound"] += tkm
                regions[nuts_id]["modes_direction_tonnes"][m]["outbound"] += t
                regions[nuts_id]["modes_direction_tkm"][m]["outbound"] += tkm

    # 2. Inbound sums (dest_nuts)
    print("  -> Computing inbound aggregations...")
    q_in_mode_bin = full_df[~full_df['is_binnen']].groupby(['dest_nuts', 'mode'])[['Tonnen', 'Tkm']].sum().reset_index()
    for row in q_in_mode_bin.itertuples(index=False):
        nuts_id = row.dest_nuts
        if nuts_id in regions:
            t = float(row.Tonnen)
            tkm = float(row.Tkm)
            m = row.mode
            regions[nuts_id]["tonnes"]["inbound"] += t
            regions[nuts_id]["tkm"]["inbound"] += tkm
            regions[nuts_id]["directions_tonnes"]["inbound"] += t
            regions[nuts_id]["directions_tkm"]["inbound"] += tkm
            regions[nuts_id]["modes_direction_tonnes"][m]["inbound"] += t
            regions[nuts_id]["modes_direction_tkm"][m]["inbound"] += tkm

    # 3. Commodity Group sums (NST-7) by Direction
    print("  -> Computing NST-7 groups by direction...")
    # Outbound / Binnen groups (orig_nuts)
    q_g7_out = full_df.groupby(['orig_nuts', 'g7', 'mode', 'is_binnen'])[['Tonnen', 'Tkm']].sum().reset_index()
    for row in q_g7_out.itertuples(index=False):
        nuts_id = row.orig_nuts
        if nuts_id in regions:
            g = str(row.g7)
            mode = str(row.mode)
            t = float(row.Tonnen)
            tkm = float(row.Tkm)
            is_b = bool(row.is_binnen)

            regions[nuts_id]["nst_7"][g] += t

            if is_b:
                regions[nuts_id]["groups_7_tonnes"]["binnen"][g] += t
                regions[nuts_id]["groups_7_tkm"]["binnen"][g] += tkm
                regions[nuts_id]["modes_by_group_tonnes"][g][mode]["binnen"] += t
                regions[nuts_id]["modes_by_group_tkm"][g][mode]["binnen"] += tkm
            else:
                regions[nuts_id]["groups_7_tonnes"]["outbound"][g] += t
                regions[nuts_id]["groups_7_tkm"]["outbound"][g] += tkm
                regions[nuts_id]["modes_by_group_tonnes"][g][mode]["outbound"] += t
                regions[nuts_id]["modes_by_group_tkm"][g][mode]["outbound"] += tkm

    # Inbound groups (dest_nuts)
    q_g7_in = full_df[~full_df['is_binnen']].groupby(['dest_nuts', 'g7', 'mode'])[['Tonnen', 'Tkm']].sum().reset_index()
    for row in q_g7_in.itertuples(index=False):
        nuts_id = row.dest_nuts
        if nuts_id in regions:
            g = str(row.g7)
            mode = str(row.mode)
            t = float(row.Tonnen)
            tkm = float(row.Tkm)
            regions[nuts_id]["groups_7_tonnes"]["inbound"][g] += t
            regions[nuts_id]["groups_7_tkm"]["inbound"][g] += tkm
            regions[nuts_id]["modes_by_group_tonnes"][g][mode]["inbound"] += t
            regions[nuts_id]["modes_by_group_tkm"][g][mode]["inbound"] += tkm

    # 3b. Original VP2040 groups by direction. This preserves the source
    # systematics (25 groups) without modelling a non-existent NST detail.
    print("  -> Computing original VP2040 goods groups by direction...")
    q_vp_out = full_df.groupby(['orig_nuts', 'vp_group', 'is_binnen'])[['Tonnen', 'Tkm']].sum().reset_index()
    for row in q_vp_out.itertuples(index=False):
        nuts_id = row.orig_nuts
        if nuts_id in regions:
            vp_group = str(row.vp_group)
            tonnes = float(row.Tonnen)
            tkm = float(row.Tkm)
            regions[nuts_id]["vp2040_groups_tonnes"]["all"][vp_group] += tonnes
            regions[nuts_id]["vp2040_groups_tkm"]["all"][vp_group] += tkm
            if not bool(row.is_binnen):
                regions[nuts_id]["vp2040_groups_tonnes"]["outbound"][vp_group] += tonnes
                regions[nuts_id]["vp2040_groups_tkm"]["outbound"][vp_group] += tkm

    q_vp_in = full_df[~full_df['is_binnen']].groupby(['dest_nuts', 'vp_group'])[['Tonnen', 'Tkm']].sum().reset_index()
    for row in q_vp_in.itertuples(index=False):
        nuts_id = row.dest_nuts
        if nuts_id in regions:
            vp_group = str(row.vp_group)
            regions[nuts_id]["vp2040_groups_tonnes"]["inbound"][vp_group] += float(row.Tonnen)
            regions[nuts_id]["vp2040_groups_tkm"]["inbound"][vp_group] += float(row.Tkm)

    # 4. KV by NUTS-3 (Outbound & Inbound)
    print("  -> Aggregating KV by NUTS-3...")
    kv_out = full_df[full_df['VerkArt'] == 2].groupby('orig_nuts')[['Tonnen', 'Ladeeinheiten', 'TEU']].sum().reset_index()
    for row in kv_out.itertuples(index=False):
        nuts_id = row.orig_nuts
        if nuts_id in regions:
            regions[nuts_id]["kv"]["tonnes"] = float(row.Tonnen)
            regions[nuts_id]["kv"]["outbound_tonnes"] = float(row.Tonnen)
            regions[nuts_id]["kv"]["ladeeinheiten"] = int(row.Ladeeinheiten)
            regions[nuts_id]["kv"]["teu"] = int(row.TEU)
            regions[nuts_id]["kv"]["outbound_teu"] = int(row.TEU)

    kv_in = full_df[(full_df['VerkArt'] == 2) & (~full_df['is_binnen'])].groupby('dest_nuts')[['Tonnen', 'Ladeeinheiten', 'TEU']].sum().reset_index()
    for row in kv_in.itertuples(index=False):
        nuts_id = row.dest_nuts
        if nuts_id in regions:
            regions[nuts_id]["kv"]["inbound_tonnes"] = float(row.Tonnen)
            regions[nuts_id]["kv"]["inbound_teu"] = int(row.TEU)
            regions[nuts_id]["kv"]["tonnes"] += float(row.Tonnen)
            regions[nuts_id]["kv"]["ladeeinheiten"] += int(row.Ladeeinheiten)
            regions[nuts_id]["kv"]["teu"] += int(row.TEU)

    # 5. BehTyp by NUTS-3
    bt_df = full_df[full_df['BehTyp'] > 0].groupby(['orig_nuts', 'BehTyp'])['Tonnen'].sum().reset_index()
    for row in bt_df.itertuples(index=False):
        nuts_id = row.orig_nuts
        if nuts_id in regions:
            regions[nuts_id]["behtyp"][str(row.BehTyp)] = float(row.Tonnen)

    bt_in_df = full_df[(full_df['BehTyp'] > 0) & (~full_df['is_binnen'])].groupby(['dest_nuts', 'BehTyp'])['Tonnen'].sum().reset_index()
    for row in bt_in_df.itertuples(index=False):
        nuts_id = row.dest_nuts
        if nuts_id in regions:
            key = str(row.BehTyp)
            regions[nuts_id]["behtyp"][key] = regions[nuts_id]["behtyp"].get(key, 0.0) + float(row.Tonnen)

    # 6. Directional Top Relations.  The earlier implementation accumulated
    # every relation into nested Python objects before selecting the top rows.
    # The raw matrices are large enough for that to exhaust a normal desktop
    # installation.  The same aggregation now stays in compact DataFrames and
    # processes the seven goods groups one at a time.
    print("  -> Computing directional top relations...")
    def aggregate_relations(data):
        keys = ['orig_nuts', 'dest_nuts']
        totals = data.groupby(keys, sort=False)[['Tonnen', 'Tkm', 'TEU']].sum().reset_index()
        mode_lists = (
            data[keys + ['mode']]
            .drop_duplicates()
            .groupby(keys, sort=False)['mode']
            .agg(lambda values: sorted(values))
            .reset_index(name='modes_list')
        )
        result = totals.merge(mode_lists, on=keys, how='left', validate='one_to_one')
        result['is_binnen'] = result['orig_nuts'] == result['dest_nuts']
        return result

    def make_bilateral(relations):
        reverse = relations.loc[~relations['is_binnen']].copy()
        reverse[['orig_nuts', 'dest_nuts']] = reverse[['dest_nuts', 'orig_nuts']]
        combined = pd.concat([relations, reverse], ignore_index=True)
        totals = combined.groupby(['orig_nuts', 'dest_nuts'], sort=False)[['Tonnen', 'Tkm', 'TEU']].sum().reset_index()
        mode_lists = (
            combined.groupby(['orig_nuts', 'dest_nuts'], sort=False)['modes_list']
            .agg(lambda lists: sorted({mode for item in lists for mode in item}))
            .reset_index()
        )
        result = totals.merge(mode_lists, on=['orig_nuts', 'dest_nuts'], how='left', validate='one_to_one')
        result['is_binnen'] = result['orig_nuts'] == result['dest_nuts']
        return result

    def pack_relation_rows(data, partner_column, group_code="ALL", group_name="Alle Güter"):
        return [{
            "partner_id": str(getattr(row, partner_column)),
            "partner_name": web_regions.get(str(getattr(row, partner_column)), {}).get(
                'name', target_names.get(str(getattr(row, partner_column)), str(getattr(row, partner_column)))
            ),
            "is_binnen": bool(row.is_binnen),
            "group_7": group_code,
            "group_name": group_name,
            "modes_list": list(row.modes_list),
            "tonnes": round(float(row.Tonnen), 1),
            "tkm": round(float(row.Tkm), 1),
            "teu": int(row.TEU)
        } for row in data.itertuples(index=False)]

    def top_relations_for_metrics(rows, count):
        """Keep candidates for both selectable relation measures.

        The browser sorts the retained rows only after a user selects tonnes or
        tonne-kilometres.  A tonnes-only preselection would therefore hide a
        valid top-tkm relation.  The union remains compact (at most twice the
        requested count) and is de-duplicated by O-D pair.
        """
        by_tonnes = rows.nlargest(count, 'Tonnen')
        by_tkm = rows.nlargest(count, 'Tkm')
        return (
            pd.concat([by_tonnes, by_tkm], ignore_index=False)
            .drop_duplicates(['orig_nuts', 'dest_nuts'])
            .sort_values(['Tonnen', 'Tkm'], ascending=False)
        )

    rel_all = aggregate_relations(full_df)
    rel_bilateral = make_bilateral(rel_all)

    for focal_id, rows in rel_bilateral[rel_bilateral['orig_nuts'].isin(regions)].groupby('orig_nuts', sort=False):
        regions[focal_id]["relations_overall"]["all"] = pack_relation_rows(top_relations_for_metrics(rows, 35), 'dest_nuts')
    for focal_id, rows in rel_all[rel_all['orig_nuts'].isin(regions)].groupby('orig_nuts', sort=False):
        regions[focal_id]["relations_overall"]["outbound"] = pack_relation_rows(top_relations_for_metrics(rows, 35), 'dest_nuts')
    for focal_id, rows in rel_all[rel_all['dest_nuts'].isin(regions)].groupby('dest_nuts', sort=False):
        regions[focal_id]["relations_overall"]["inbound"] = pack_relation_rows(top_relations_for_metrics(rows, 35), 'orig_nuts')

    def build_partner_lookup(frame, focal_column, partner_column):
        lookup = {}
        for row in frame[['orig_nuts', 'dest_nuts', 'Tonnen', 'Tkm']].itertuples(index=False):
            focal_id = str(getattr(row, focal_column))
            partner_id = str(getattr(row, partner_column))
            lookup.setdefault(focal_id, {})[partner_id] = {
                "tonnes": float(row.Tonnen),
                "tkm": float(row.Tkm)
            }
        return lookup

    relation_lookups = {
        "all": build_partner_lookup(rel_bilateral, 'orig_nuts', 'dest_nuts'),
        "outbound": build_partner_lookup(rel_all, 'orig_nuts', 'dest_nuts'),
        "inbound": build_partner_lookup(rel_all, 'dest_nuts', 'orig_nuts')
    }

    # 7. Group-specific directional relations, released after each group.
    print("  -> Computing group-specific top relations...")
    for g7 in map(str, range(1, 8)):
        group_name = next(
            (item["nst2007_group7_name"] for item in nst_list if str(item["nst2007_group7"]) == g7),
            f"Gruppe {g7}"
        )
        group_relations = aggregate_relations(full_df[full_df['g7'] == g7])
        group_bilateral = make_bilateral(group_relations)
        for focal_id, rows in group_bilateral[group_bilateral['orig_nuts'].isin(regions)].groupby('orig_nuts', sort=False):
            regions[focal_id]["by_group_relations"][g7]["all"] = pack_relation_rows(top_relations_for_metrics(rows, 25), 'dest_nuts', g7, group_name)
        for focal_id, rows in group_relations[group_relations['orig_nuts'].isin(regions)].groupby('orig_nuts', sort=False):
            regions[focal_id]["by_group_relations"][g7]["outbound"] = pack_relation_rows(top_relations_for_metrics(rows, 25), 'dest_nuts', g7, group_name)
        for focal_id, rows in group_relations[group_relations['dest_nuts'].isin(regions)].groupby('dest_nuts', sort=False):
            regions[focal_id]["by_group_relations"][g7]["inbound"] = pack_relation_rows(top_relations_for_metrics(rows, 25), 'orig_nuts', g7, group_name)
        del group_relations, group_bilateral

    # The relation change column is calculated for the unfiltered (all-goods)
    # top relations.  Detailed goods-group rows remain value-correct but do not
    # claim a percentage where no lightweight comparison record is retained.
    group_relation_lookups = None

    # 8. National Top Relations (Consolidated)
    for row in rel_all.nlargest(50, 'Tonnen').itertuples(index=False):
        national["top_relations"].append({
            "orig_id": str(row.orig_nuts),
            "orig_name": web_regions.get(str(row.orig_nuts), {}).get('name', str(row.orig_nuts)),
            "dest_id": str(row.dest_nuts),
            "dest_name": web_regions.get(str(row.dest_nuts), {}).get('name', str(row.dest_nuts)),
            "is_binnen": bool(row.is_binnen),
            "group_7": "ALL",
            "group_name": "Alle Güter",
            "modes_list": list(row.modes_list),
            "tonnes": round(float(row.Tonnen), 1),
            "tkm": round(float(row.Tkm), 1),
            "teu": int(row.TEU)
        })

    del full_df, rel_all, rel_bilateral

    # 9. Finalize Totals, Balances, Modal Splits and Choropleth Cubes
    choropleth_tonnes = {}
    choropleth_tkm = {}

    for nuts_id, r_data in regions.items():
        # Overall total = outbound + inbound + binnen
        tot_out = r_data["directions_tonnes"]["outbound"]
        tot_in = r_data["directions_tonnes"]["inbound"]
        tot_bin = r_data["directions_tonnes"]["binnen"]
        tot_t = tot_out + tot_in + tot_bin
        
        tkm_out = r_data["directions_tkm"]["outbound"]
        tkm_in = r_data["directions_tkm"]["inbound"]
        tkm_bin = r_data["directions_tkm"]["binnen"]
        tot_tkm = tkm_out + tkm_in + tkm_bin

        r_data["tonnes"]["total"] = round(tot_t, 1)
        r_data["tkm"]["total"] = round(tot_tkm, 1)
        r_data["directions_tonnes"]["all"] = round(tot_t, 1)
        r_data["directions_tkm"]["all"] = round(tot_tkm, 1)

        bal_t = round(tot_out - tot_in, 1)
        bal_tkm = round(tkm_out - tkm_in, 1)
        r_data["tonnes"]["balance"] = bal_t
        r_data["tkm"]["balance"] = bal_tkm
        r_data["directions_tonnes"]["balance"] = bal_t
        r_data["directions_tkm"]["balance"] = bal_tkm

        # Totals, balances and modal values by group.  As with the all-goods
        # totals, a regional total is Versand + Empfang + Binnenverkehr.
        for g in [str(i) for i in range(1, 8)]:
            g_out_t = r_data["groups_7_tonnes"]["outbound"][g]
            g_in_t = r_data["groups_7_tonnes"]["inbound"][g]
            g_bin_t = r_data["groups_7_tonnes"]["binnen"][g]
            r_data["groups_7_tonnes"]["all"][g] = round(g_out_t + g_in_t + g_bin_t, 1)
            r_data["groups_7_tonnes"]["balance"][g] = round(g_out_t - g_in_t, 1)

            g_out_tkm = r_data["groups_7_tkm"]["outbound"][g]
            g_in_tkm = r_data["groups_7_tkm"]["inbound"][g]
            g_bin_tkm = r_data["groups_7_tkm"]["binnen"][g]
            r_data["groups_7_tkm"]["all"][g] = round(g_out_tkm + g_in_tkm + g_bin_tkm, 1)
            r_data["groups_7_tkm"]["balance"][g] = round(g_out_tkm - g_in_tkm, 1)

            for mode in ("road", "rail", "iww"):
                group_mode_tonnes = r_data["modes_by_group_tonnes"][g][mode]
                group_mode_tonnes["all"] = round(
                    group_mode_tonnes["outbound"] + group_mode_tonnes["inbound"] + group_mode_tonnes["binnen"], 1
                )
                group_mode_tonnes["balance"] = round(
                    group_mode_tonnes["outbound"] - group_mode_tonnes["inbound"], 1
                )
                group_mode_tkm = r_data["modes_by_group_tkm"][g][mode]
                group_mode_tkm["all"] = round(
                    group_mode_tkm["outbound"] + group_mode_tkm["inbound"] + group_mode_tkm["binnen"], 1
                )
                group_mode_tkm["balance"] = round(
                    group_mode_tkm["outbound"] - group_mode_tkm["inbound"], 1
                )

        # Balance and clean precision for the original VP2040 goods groups.
        # These are the 25 categories in the source matrix column
        # ``Guetergruppe``; no additional NST category is introduced here.
        for vp_group in vp_group_keys:
            vp_out_t = r_data["vp2040_groups_tonnes"]["outbound"][vp_group]
            vp_in_t = r_data["vp2040_groups_tonnes"]["inbound"][vp_group]
            r_data["vp2040_groups_tonnes"]["balance"][vp_group] = round(vp_out_t - vp_in_t, 1)

            vp_out_tkm = r_data["vp2040_groups_tkm"]["outbound"][vp_group]
            vp_in_tkm = r_data["vp2040_groups_tkm"]["inbound"][vp_group]
            r_data["vp2040_groups_tkm"]["balance"][vp_group] = round(vp_out_tkm - vp_in_tkm, 1)

        for direction_key in ["all", "outbound", "inbound"]:
            r_data["vp2040_groups_tonnes"][direction_key] = {
                key: round(val, 1)
                for key, val in r_data["vp2040_groups_tonnes"][direction_key].items()
            }
            r_data["vp2040_groups_tkm"][direction_key] = {
                key: round(val, 1)
                for key, val in r_data["vp2040_groups_tkm"][direction_key].items()
            }

        # Mode totals & balances
        for m in ['road', 'rail', 'iww']:
            m_out = r_data["modes_direction_tonnes"][m]["outbound"]
            m_in = r_data["modes_direction_tonnes"][m]["inbound"]
            m_bin = r_data["modes_direction_tonnes"][m]["binnen"]
            r_data["modes_direction_tonnes"][m]["all"] = round(m_out + m_in + m_bin, 1)
            r_data["modes_direction_tonnes"][m]["balance"] = round(m_out - m_in, 1)

            m_out_tkm = r_data["modes_direction_tkm"][m]["outbound"]
            m_in_tkm = r_data["modes_direction_tkm"][m]["inbound"]
            m_bin_tkm = r_data["modes_direction_tkm"][m]["binnen"]
            r_data["modes_direction_tkm"][m]["all"] = round(m_out_tkm + m_in_tkm + m_bin_tkm, 1)
            r_data["modes_direction_tkm"][m]["balance"] = round(m_out_tkm - m_in_tkm, 1)
            r_data["modes_tonnes"][m] = r_data["modes_direction_tonnes"][m]["all"]
            r_data["modes_tkm"][m] = r_data["modes_direction_tkm"][m]["all"]
            r_data["tonnes"][m] = r_data["modes_direction_tonnes"][m]["all"]
            r_data["tkm"][m] = r_data["modes_direction_tkm"][m]["all"]

        # Modal split
        m_tot_t = r_data["modes_tonnes"]["road"] + r_data["modes_tonnes"]["rail"] + r_data["modes_tonnes"]["iww"]
        if m_tot_t > 0:
            r_data["modal_split_tonnes"]["road"] = round(r_data["modes_tonnes"]["road"] / m_tot_t * 100, 1)
            r_data["modal_split_tonnes"]["rail"] = round(r_data["modes_tonnes"]["rail"] / m_tot_t * 100, 1)
            r_data["modal_split_tonnes"]["iww"] = round(r_data["modes_tonnes"]["iww"] / m_tot_t * 100, 1)
            r_data["kv"]["share_pct"] = round(r_data["kv"]["tonnes"] / m_tot_t * 100, 1)

        m_tot_tkm = r_data["modes_tkm"]["road"] + r_data["modes_tkm"]["rail"] + r_data["modes_tkm"]["iww"]
        if m_tot_tkm > 0:
            r_data["modal_split_tkm"]["road"] = round(r_data["modes_tkm"]["road"] / m_tot_tkm * 100, 1)
            r_data["modal_split_tkm"]["rail"] = round(r_data["modes_tkm"]["rail"] / m_tot_tkm * 100, 1)
            r_data["modal_split_tkm"]["iww"] = round(r_data["modes_tkm"]["iww"] / m_tot_tkm * 100, 1)

        for k in r_data["tonnes"]: r_data["tonnes"][k] = round(r_data["tonnes"][k], 1)
        for k in r_data["tkm"]: r_data["tkm"][k] = round(r_data["tkm"][k], 1)
        for k in r_data["nst_7"]: r_data["nst_7"][k] = round(r_data["nst_7"][k], 1)
        for k in r_data["behtyp"]: r_data["behtyp"][k] = round(r_data["behtyp"][k], 1)

        choropleth_tonnes[nuts_id] = r_data["tonnes"]["total"]
        choropleth_tkm[nuts_id] = r_data["tkm"]["total"]

    elapsed = time.time() - start_time
    print(f"  -> Scenario {scenario_id} aggregated in {elapsed:.1f}s.")
    return {
        "national": national,
        "regions": regions,
        "choropleth": {
            "tonnes": choropleth_tonnes,
            "tkm": choropleth_tkm
        },
        "_relation_lookups": relation_lookups,
        "_group_relation_lookups": group_relation_lookups
    }


def percentage_change(value, base_value):
    """Return a percentage change only where the base value is meaningful."""
    if base_value is None or abs(base_value) < 1e-9:
        return None
    return round((value - base_value) / abs(base_value) * 100, 1)


def add_comparison_2019(baseline, forecast):
    """Attach exact 2019-to-2040 changes without adding synthetic values."""
    baseline["national"]["comparison_2019"] = {
        "available": True,
        "role": "baseline",
        "method": "Originale VP2040-Matrix für das Basisjahr 2019."
    }
    forecast["national"]["comparison_2019"] = {
        "available": True,
        "role": "comparison",
        "method": "Vergleich der originalen VP2040-Matrizen für das Basisjahr 2019 und die Basisprognose 2040 (P1)."
    }

    baseline_national = baseline["national"]
    forecast_national = forecast["national"]
    for metric in ("tonnes", "tkm"):
        forecast_national[f"growth_2019_{metric}_pct"] = percentage_change(
            forecast_national[f"total_{metric}"],
            baseline_national[f"total_{metric}"]
        )
        for mode in ("road", "rail", "iww"):
            forecast_national["modes"][mode][f"growth_2019_{metric}_pct"] = percentage_change(
                forecast_national["modes"][mode][metric],
                baseline_national["modes"][mode][metric]
            )
        for group, group_modes in forecast_national["modes_by_group"].items():
            baseline_group_modes = baseline_national["modes_by_group"].get(group, {})
            for mode, current_mode in group_modes.items():
                baseline_mode = baseline_group_modes.get(mode)
                current_mode[f"growth_2019_{metric}_pct"] = percentage_change(
                    current_mode[metric],
                    baseline_mode[metric] if baseline_mode else None
                )
        for group in forecast_national["nst_groups_7"].values():
            baseline_group = baseline_national["nst_groups_7"].get(group["id"])
            group[f"growth_2019_{metric}_pct"] = percentage_change(
                group[metric],
                baseline_group[metric] if baseline_group else None
            )
        for group in forecast_national["vp2040_groups"].values():
            baseline_group = baseline_national["vp2040_groups"].get(group["id"])
            group[f"growth_2019_{metric}_pct"] = percentage_change(
                group[metric],
                baseline_group[metric] if baseline_group else None
            )

    for region_id, forecast_region in forecast["regions"].items():
        baseline_region = baseline["regions"].get(region_id)
        if not baseline_region:
            continue

        growth = {}
        for metric in ("tonnes", "tkm"):
            directions_key = f"directions_{metric}"
            modes_key = f"modes_direction_{metric}"
            modes_by_group_key = f"modes_by_group_{metric}"
            groups_key = f"groups_7_{metric}"
            growth[metric] = {
                "directions": {
                    direction: percentage_change(
                        forecast_region[directions_key][direction],
                        baseline_region[directions_key][direction]
                    )
                    for direction in ("all", "outbound", "inbound")
                },
                "modes": {
                    mode: percentage_change(
                        forecast_region[modes_key][mode]["all"],
                        baseline_region[modes_key][mode]["all"]
                    )
                    for mode in ("road", "rail", "iww")
                },
                "modes_by_group": {
                    group: {
                        mode: {
                            direction: percentage_change(
                                forecast_region[modes_by_group_key][group][mode][direction],
                                baseline_region[modes_by_group_key][group][mode][direction]
                            )
                            for direction in ("all", "outbound", "inbound")
                        }
                        for mode in ("road", "rail", "iww")
                    }
                    for group in map(str, range(1, 8))
                },
                "groups_7": {
                    direction: {
                        group: percentage_change(
                            forecast_region[groups_key][direction][group],
                            baseline_region[groups_key][direction][group]
                        )
                        for group in map(str, range(1, 8))
                    }
                    for direction in ("all", "outbound", "inbound")
                }
            }
        forecast_region["growth_2019"] = growth

    def add_relation_growth(forecast_region, baseline_lookups):
        for direction in ("all", "outbound", "inbound"):
            baseline_partners = baseline_lookups[direction].get(forecast_region["id"], {})
            for relation in forecast_region["relations_overall"][direction]:
                baseline_relation = baseline_partners.get(relation["partner_id"])
                relation["growth_2019"] = {
                    metric: percentage_change(
                        relation[metric],
                        baseline_relation[metric] if baseline_relation else None
                    )
                    for metric in ("tonnes", "tkm")
                }

    baseline_lookups = baseline["_relation_lookups"]
    for forecast_region in forecast["regions"].values():
        add_relation_growth(forecast_region, baseline_lookups)


def add_relation_growth_from_raw_matrices(base_dir, forecast):
    """Complete relation changes from the 2019 matrix without a large lookup cube.

    The browser keeps only the displayed top relations.  This function gathers
    exactly those relation keys, streams the 2019 raw matrices once and adds
    comparison values for both the all-goods and goods-group relation views.
    It avoids retaining every possible NUTS-3 pair in Python memory.
    """
    crosswalk_dir = os.path.join(base_dir, "data", "crosswalks")
    with open(os.path.join(crosswalk_dir, "crosswalk_spatial_vp2040.json"), encoding="utf-8") as handle:
        spatial_list = json.load(handle)
    with open(os.path.join(crosswalk_dir, "crosswalk_nst_vp2040.json"), encoding="utf-8") as handle:
        nst_list = json.load(handle)

    gg_to_g7 = {int(item["vp40_code"]): str(item["nst2007_group7"]) for item in nst_list}
    ags_to_nuts = {
        str(item["ags_5stellig"]): item.get("nuts3_2024") or item.get("nuts3_2016")
        for item in spatial_list
        if item.get("ags_5stellig") and (item.get("nuts3_2024") or item.get("nuts3_2016"))
    }
    # The baseline comparison must use the exact same special-cell assignment
    # as the scenario aggregation.  Keeping a second, hand-maintained mapping
    # here had silently assigned ports such as Brunsbüttel differently and
    # therefore corrupted the displayed 2019 comparison for some relations.
    with open(os.path.join(crosswalk_dir, "vp2040_special_cells_nuts3.json"), encoding="utf-8") as handle:
        special_cells = {
            int(cell_id): metadata["nuts3_2024"]
            for cell_id, metadata in json.load(handle)["cells"].items()
        }
    cell_to_target = {}
    for item in spatial_list:
        cell_id = int(item["cell_id"])
        if item["country_iso2"] != "DE":
            cell_to_target[cell_id] = str(cell_id)
            continue
        target = item.get("nuts3_2024") or item.get("nuts3_2016") or special_cells.get(cell_id)
        cell_text = str(cell_id)
        if not target and len(cell_text) == 7 and cell_text.endswith("00"):
            target = ags_to_nuts.get(cell_text[:5])
        cell_to_target[cell_id] = target or cell_text

    # key = direction, goods selection, selected NUTS-3, partner NUTS-3/cell
    baseline_values = {}
    def register_target(direction, group, focal_id, partner_id):
        key = (direction, group, str(focal_id), str(partner_id))
        baseline_values.setdefault(key, {"tonnes": 0.0, "tkm": 0.0})
        return key

    for region in forecast["regions"].values():
        focal_id = region["id"]
        for direction in ("all", "outbound", "inbound"):
            for relation in region["relations_overall"][direction]:
                register_target(direction, "ALL", focal_id, relation["partner_id"])
            for group in map(str, range(1, 8)):
                for relation in region["by_group_relations"][group][direction]:
                    register_target(direction, group, focal_id, relation["partner_id"])

    def add_value(key, tonnes, tkm):
        value = baseline_values.get(key)
        if value is not None:
            value["tonnes"] += tonnes
            value["tkm"] += tkm

    raw_dir = os.path.join(base_dir, "data", "raw", "VP2040", "VP2040_2019_GV_NUTS3")
    files = (
        "VP2040_2019_GV_Strasse_NUTS3_Matrix_V01.csv",
        "VP2040_2019_GV_Bahn_NUTS3_Matrix_V01.csv",
        "VP2040_2019_GV_Bischi_NUTS3_Matrix_V01.csv",
    )
    print(f"  -> Completing 2019 changes for {len(baseline_values):,} displayed relations...")
    for filename in files:
        matrix_path = os.path.join(raw_dir, filename)
        for chunk in pd.read_csv(
            matrix_path,
            sep=";",
            encoding="latin1",
            usecols=["Quellzelle", "Zielzelle", "Guetergruppe", "Tonnen", "Tkm"],
            chunksize=100_000,
            dtype={
                "Quellzelle": np.int32, "Zielzelle": np.int32, "Guetergruppe": np.int16,
                "Tonnen": np.float64, "Tkm": np.float64
            }
        ):
            chunk["origin"] = chunk["Quellzelle"].map(cell_to_target).fillna(chunk["Quellzelle"].astype(str))
            chunk["destination"] = chunk["Zielzelle"].map(cell_to_target).fillna(chunk["Zielzelle"].astype(str))
            chunk["g7"] = chunk["Guetergruppe"].map(gg_to_g7).fillna("7")
            grouped = chunk.groupby(["origin", "destination", "g7"], sort=False)[["Tonnen", "Tkm"]].sum().reset_index()
            for row in grouped.itertuples(index=False):
                origin = str(row.origin)
                destination = str(row.destination)
                group = str(row.g7)
                tonnes = float(row.Tonnen)
                tkm = float(row.Tkm)
                for group_key in ("ALL", str(group)):
                    add_value(("outbound", group_key, origin, destination), tonnes, tkm)
                    add_value(("inbound", group_key, destination, origin), tonnes, tkm)
                    add_value(("all", group_key, origin, destination), tonnes, tkm)
                    if origin != destination:
                        add_value(("all", group_key, destination, origin), tonnes, tkm)

    def write_growth(relation, direction, group, focal_id):
        baseline = baseline_values[(direction, group, str(focal_id), str(relation["partner_id"]))]
        relation["growth_2019"] = {
            metric: percentage_change(relation[metric], baseline[metric])
            for metric in ("tonnes", "tkm")
        }

    for region in forecast["regions"].values():
        focal_id = region["id"]
        for direction in ("all", "outbound", "inbound"):
            for relation in region["relations_overall"][direction]:
                write_growth(relation, direction, "ALL", focal_id)
            for group in map(str, range(1, 8)):
                for relation in region["by_group_relations"][group][direction]:
                    write_growth(relation, direction, group, focal_id)
    return len(baseline_values)


def build_vp2040_bundle():
    """Build the browser bundle from the original 2019 and 2040 VP2040 matrices."""
    start_time = time.time()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vp2040_dir = os.path.join(base_dir, "data", "raw", "VP2040")
    out_json = os.path.join(base_dir, "data", "processed", "web_forecast_2040.json")
    scenario_directories = {
        "2019_BASE": os.path.join(vp2040_dir, "VP2040_2019_GV_NUTS3"),
        "2040_P1": os.path.join(vp2040_dir, "VP2040_2040P1BP_GV_NUTS3"),
    }

    print("[1/3] Building the VP2040 baseline cube for 2019...")
    baseline = build_vp2040_scenario_bundle("2019_BASE", scenario_directories["2019_BASE"])
    print("[2/3] Building the VP2040 forecast cube for 2040 P1...")
    forecast = build_vp2040_scenario_bundle("2040_P1", scenario_directories["2040_P1"])
    print("[3/3] Calculating exact 2019-to-2040 comparisons...")
    add_comparison_2019(baseline, forecast)
    add_relation_growth_from_raw_matrices(base_dir, forecast)

    # The comparison lookups are an ETL-only aid and must not enlarge the
    # delivered browser data.  All displayed values and changes have now been
    # written directly into the corresponding scenario records.
    baseline.pop("_relation_lookups")
    baseline.pop("_group_relation_lookups")
    forecast.pop("_relation_lookups")
    forecast.pop("_group_relation_lookups")

    bundle = {
        "metadata": {
            "title": "Verkehrsprognose 2040 – Güterverkehrsverflechtungen",
            "source": "BMDV / Intraplan / Trimode / ETR / MWP (FKZ VB970423)",
            "vp2040_groups": {
                key: value["name"]
                for key, value in forecast["national"]["vp2040_groups"].items()
            },
            "data_basis": {
                "2019_BASE": {
                    "raw_directory": "data/raw/VP2040/VP2040_2019_GV_NUTS3",
                    "matrix_version": "V01",
                    "source_type": "Basisjahr 2019"
                },
                "2040_P1": {
                    "raw_directory": "data/raw/VP2040/VP2040_2040P1BP_GV_NUTS3",
                    "matrix_version": "V01",
                    "source_type": "Basisprognose 2040 (P1)"
                }
            },
            "available_scenarios": [
                {
                    "id": "2040_P1",
                    "name": "Basisprognose 2040 (Prognosefall 1)",
                    "short_name": "2040 (P1 Basisprognose)",
                    "year": 2040,
                    "is_forecast": True,
                    "available": True
                },
                {
                    "id": "2019_BASE",
                    "name": "Ist-Zustand 2019 (Basisjahr)",
                    "short_name": "2019 (Basisjahr Ist)",
                    "year": 2019,
                    "is_forecast": False,
                    "available": True
                }
            ]
        },
        "scenarios": {
            "2040_P1": forecast,
            "2019_BASE": baseline
        }
    }

    print(f"Writing bundle to {out_json}...")
    temp_dir = os.path.join("C:\\tmp", "gueterstroeme-vp2040")
    os.makedirs(temp_dir, exist_ok=True)
    temp_json = os.path.join(temp_dir, "web_forecast_2040.json")
    try:
        with open(temp_json, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, ensure_ascii=False)
        shutil.copyfile(temp_json, out_json)
    finally:
        if os.path.isfile(temp_json):
            os.remove(temp_json)
        if os.path.isdir(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)

    size_mb = os.path.getsize(out_json) / 1024 / 1024
    write_overview_tooltip_preview(
        bundle,
        os.path.join(base_dir, "data", "processed", "web_forecast_overview_tooltip.json")
    )
    elapsed = time.time() - start_time
    print(f"DONE in {elapsed:.1f}s! Generated web_forecast_2040.json ({size_mb:.2f} MB)")


def write_overview_tooltip_preview(bundle, output_path):
    """Write the compact 2019/2040 cube used by overview-map tooltips.

    Relations, modal details and VP2040's detailed goods system are excluded.
    The retained dimensions mirror the overview filters: metric, direction and
    the seven NST-2007 main groups.
    """
    fields = ("directions_tonnes", "directions_tkm", "groups_7_tonnes", "groups_7_tkm")
    scenarios = {}
    for scenario_id in ("2019_BASE", "2040_P1"):
        source_regions = bundle["scenarios"][scenario_id]["regions"]
        scenarios[scenario_id] = {
            "year": 2019 if scenario_id == "2019_BASE" else 2040,
            "regions": {
                region_id: {field: region[field] for field in fields}
                for region_id, region in source_regions.items()
            }
        }

    preview = {
        "metadata": {
            "title": "VP2040-Vorschau für Tooltips der Übersicht",
            "source": bundle["metadata"]["source"],
            "comparison": "Originale VP2040-Matrizen: Basisjahr 2019 und Basisprognose 2040 (P1)."
        },
        "scenarios": scenarios
    }
    temp_dir = os.path.join("C:\\tmp", "gueterstroeme-vp2040")
    os.makedirs(temp_dir, exist_ok=True)
    temp_output = os.path.join(temp_dir, "web_forecast_overview_tooltip.json")
    try:
        with open(temp_output, "w", encoding="utf-8") as file:
            json.dump(preview, file, ensure_ascii=False, separators=(",", ":"))
        shutil.copyfile(temp_output, output_path)
    finally:
        if os.path.isfile(temp_output):
            os.remove(temp_output)
        if os.path.isdir(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)


def build_overview_tooltip_preview_from_existing_bundle():
    """Refresh the tooltip preview without rebuilding the large VP2040 cube."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bundle_path = os.path.join(base_dir, "data", "processed", "web_forecast_2040.json")
    output_path = os.path.join(base_dir, "data", "processed", "web_forecast_overview_tooltip.json")
    with open(bundle_path, "r", encoding="utf-8") as file:
        bundle = json.load(file)
    write_overview_tooltip_preview(bundle, output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"DONE: Generated web_forecast_overview_tooltip.json ({size_kb:.0f} KB)")


if __name__ == "__main__":
    import sys
    if "--tooltip-preview-only" in sys.argv:
        build_overview_tooltip_preview_from_existing_bundle()
    else:
        build_vp2040_bundle()
