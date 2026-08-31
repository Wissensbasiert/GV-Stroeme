-- ====================================================================
-- Güterverkehrsströme Deutschland - Relationales Datenbankschema
-- Kompatibel mit PostgreSQL 12+ und MySQL 8.0+ / MariaDB
-- Optimiert für OWS Data Hosting
-- ====================================================================

-- 1. Dimension: Regionen (NUTS-3, NUTS-2, Häfen)
CREATE TABLE IF NOT EXISTS dim_region (
    nuts_id VARCHAR(10) PRIMARY KEY,
    nuts_name VARCHAR(150) NOT NULL,
    nuts_level INT NOT NULL,              -- 0 = Land, 1 = Bundesland, 2 = Reg.-Bezirk, 3 = Kreis
    country_code VARCHAR(5) NOT NULL,     -- DE, NL, PL, FR, etc.
    bundesland_name VARCHAR(100),         -- z.B. Baden-Württemberg, Bayern, Berlin
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    is_german BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index für schnelle Autocomplete- & Filterabfragen
CREATE INDEX IF NOT EXISTS idx_dim_region_country ON dim_region(country_code);
CREATE INDEX IF NOT EXISTS idx_dim_region_level ON dim_region(nuts_level);

-- 2. Dimension: Güterklassifikation NST-2007
CREATE TABLE IF NOT EXISTS dim_nst2007 (
    nst_code VARCHAR(10) PRIMARY KEY,     -- z.B. "01", "011", "G1"
    nst_level VARCHAR(20) NOT NULL,       -- 'group_7', 'division_20', 'group_3digit'
    group_7_id VARCHAR(5) NOT NULL,       -- 1..7 (kleinster gemeinsamer Nenner)
    group_7_name VARCHAR(255) NOT NULL,
    division_20_id VARCHAR(5),            -- 01..20
    division_20_name VARCHAR(255),
    group_3digit_id VARCHAR(10),          -- 011, 012 etc.
    group_3digit_name VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_dim_nst_group7 ON dim_nst2007(group_7_id);
CREATE INDEX IF NOT EXISTS idx_dim_nst_div20 ON dim_nst2007(division_20_id);

-- 3. Fakten-Tabelle: Regionale Zusammenfassung & Steckbriefe (Sub-Sekunden Schnellabfragen)
CREATE TABLE IF NOT EXISTS fact_regional_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year_ref INT NOT NULL,                -- 2010 .. 2025
    nuts_id VARCHAR(10) NOT NULL,
    mode_transport VARCHAR(20) NOT NULL,  -- 'road', 'rail', 'iww', 'maritime', 'all'
    direction VARCHAR(20) NOT NULL,       -- 'inbound', 'outbound', 'internal', 'transit', 'total'
    group_7_id VARCHAR(5),                -- Optional nach 7 Gütergruppen
    division_20_id VARCHAR(5),            -- Optional nach 20 Abteilungen (wo verfügbar)
    tonnes DECIMAL(15, 2) NOT NULL DEFAULT 0,
    tkm DECIMAL(18, 2) DEFAULT 0,
    trips BIGINT DEFAULT 0,
    teu DECIMAL(12, 2) DEFAULT 0,
    CONSTRAINT fk_summary_region FOREIGN KEY (nuts_id) REFERENCES dim_region(nuts_id)
);

CREATE INDEX IF NOT EXISTS idx_summary_lookup ON fact_regional_summary(year_ref, nuts_id, mode_transport, direction);

-- 4. Fakten-Tabelle: Quelle-Ziel-Verflechtungen (O-D Spinnenkarte & Top-X Relationen)
CREATE TABLE IF NOT EXISTS fact_od_flows (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year_ref INT NOT NULL,
    origin_nuts VARCHAR(10) NOT NULL,
    dest_nuts VARCHAR(10) NOT NULL,
    mode_transport VARCHAR(20) NOT NULL,  -- 'road', 'rail', 'iww', 'maritime'
    group_7_id VARCHAR(5) DEFAULT 'ALL',
    tonnes DECIMAL(15, 2) NOT NULL DEFAULT 0,
    tkm DECIMAL(18, 2) DEFAULT 0,
    trips BIGINT DEFAULT 0,
    teu DECIMAL(12, 2) DEFAULT 0,
    CONSTRAINT fk_od_origin FOREIGN KEY (origin_nuts) REFERENCES dim_region(nuts_id),
    CONSTRAINT fk_od_dest FOREIGN KEY (dest_nuts) REFERENCES dim_region(nuts_id)
);

CREATE INDEX IF NOT EXISTS idx_od_origin ON fact_od_flows(year_ref, origin_nuts, mode_transport);
CREATE INDEX IF NOT EXISTS idx_od_dest ON fact_od_flows(year_ref, dest_nuts, mode_transport);

-- 5. Fakten-Tabelle: Nationale & Landes-Benchmarks (Für den automatisierten Steckbrief-Text)
CREATE TABLE IF NOT EXISTS fact_benchmark (
    year_ref INT NOT NULL,
    benchmark_scope VARCHAR(20) NOT NULL, -- 'NATIONAL_DE', 'STATE_BY', 'STATE_BW', etc.
    mode_transport VARCHAR(20) NOT NULL,
    modal_share_tonnes DECIMAL(6, 4) NOT NULL, -- z.B. 0.7850 = 78.5%
    modal_share_tkm DECIMAL(6, 4),
    growth_rate_yoy DECIMAL(6, 4),             -- Vorjahreswachstum
    PRIMARY KEY (year_ref, benchmark_scope, mode_transport)
);

-- 6. Fakten-Tabelle: Verkehrsprognose 2040 (Vorbereitete Struktur für VP 2040 Matrizen)
CREATE TABLE IF NOT EXISTS fact_prognosis_vp2040 (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    scenario_horizon VARCHAR(20) NOT NULL, -- '2019_BASE', '2040_P1'
    origin_nuts VARCHAR(10) NOT NULL,
    dest_nuts VARCHAR(10) NOT NULL,
    mode_transport VARCHAR(20) NOT NULL,   -- 'road', 'rail', 'iww', 'maritime', 'intermodal'
    group_7_id VARCHAR(5) DEFAULT 'ALL',
    tonnes DECIMAL(15, 2) NOT NULL,
    tkm DECIMAL(18, 2)
);

CREATE INDEX IF NOT EXISTS idx_vp_lookup ON fact_prognosis_vp2040(scenario_horizon, origin_nuts, mode_transport);
