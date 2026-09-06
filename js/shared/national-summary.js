  // Precompute National Aggregates from summaryData & benchmarkData
  function computeNationalSummaries(summaryData, benchmarkData) {
    const national = {};
    const years = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'];

    years.forEach(yr => {
      const b = benchmarkData[yr] || {};
      const bModes = b.modes || {};

      const obj = {
        total_tonnes: b.total_tonnes || 0,
        total_tkm: b.total_tkm || 0,
        modes_tonnes: {
          road: bModes.road?.tonnes || 0,
          rail: bModes.rail?.tonnes || 0,
          iww: bModes.iww?.tonnes || 0
        },
        modes_tkm: {
          road: bModes.road?.tkm || 0,
          rail: bModes.rail?.tkm || 0,
          iww: bModes.iww?.tkm || 0
        },
        modes_direction_tonnes: { road: { inbound: 0, outbound: 0 }, rail: { inbound: 0, outbound: 0 }, iww: { inbound: 0, outbound: 0 } },
        modes_direction_tkm: { road: { inbound: 0, outbound: 0 }, rail: { inbound: 0, outbound: 0 }, iww: { inbound: 0, outbound: 0 } },
        directions_tonnes: { inbound: 0, outbound: 0 },
        directions_tkm: { inbound: 0, outbound: 0 },
        groups_7_tonnes: { all: {}, inbound: {}, outbound: {}, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 },
        groups_7_tkm: { all: {}, inbound: {}, outbound: {}, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 },
        by_mode_groups: { road: { all: {}, inbound: {}, outbound: {} }, rail: { all: {}, inbound: {}, outbound: {} }, iww: { all: {}, inbound: {}, outbound: {} } },
        by_mode_groups_tkm: { road: { all: {}, inbound: {}, outbound: {} }, rail: { all: {}, inbound: {}, outbound: {} }, iww: { all: {}, inbound: {}, outbound: {} } },
        by_mode_divisions: { road: {}, rail: {}, iww: {} },
        by_mode_divisions_tkm: { road: {}, rail: {}, iww: {} }
      };

      Object.keys(summaryData).forEach(nutsId => {
        if (nutsId.length === 5) {
          const rData = summaryData[nutsId]?.[yr];
          if (!rData) return;
          ['road', 'rail', 'iww'].forEach(m => {
            obj.modes_direction_tonnes[m].inbound += (rData.modes_direction_tonnes?.[m]?.inbound || 0) / 2;
            obj.modes_direction_tonnes[m].outbound += (rData.modes_direction_tonnes?.[m]?.outbound || 0) / 2;
            obj.modes_direction_tkm[m].inbound += (rData.modes_direction_tkm?.[m]?.inbound || 0) / 2;
            obj.modes_direction_tkm[m].outbound += (rData.modes_direction_tkm?.[m]?.outbound || 0) / 2;
          });

          // Inbound & Outbound
          obj.directions_tonnes.inbound += (rData.directions_tonnes?.inbound || 0) / 2;
          obj.directions_tonnes.outbound += (rData.directions_tonnes?.outbound || 0) / 2;
          obj.directions_tkm.inbound += (rData.directions_tkm?.inbound || 0) / 2;
          obj.directions_tkm.outbound += (rData.directions_tkm?.outbound || 0) / 2;

          // NST 7
          const g7 = rData.groups_7_tonnes || {};
          const g7Map = g7.all || g7;
          Object.keys(g7Map).forEach(k => {
            obj.groups_7_tonnes[k] = (obj.groups_7_tonnes[k] || 0) + (g7Map[k] || 0) / 2;
            obj.groups_7_tonnes.all[k] = (obj.groups_7_tonnes.all[k] || 0) + (g7Map[k] || 0) / 2;
          });
          ['inbound', 'outbound'].forEach(direction => Object.entries(g7[direction] || {}).forEach(([k, amount]) => {
            obj.groups_7_tonnes[direction][k] = (obj.groups_7_tonnes[direction][k] || 0) + (amount || 0) / 2;
          }));
          const g7tkm = rData.groups_7_tkm || {};
          const g7tkmMap = g7tkm.all || g7tkm;
          Object.keys(g7tkmMap).forEach(k => {
            obj.groups_7_tkm[k] = (obj.groups_7_tkm[k] || 0) + (g7tkmMap[k] || 0) / 2;
            obj.groups_7_tkm.all[k] = (obj.groups_7_tkm.all[k] || 0) + (g7tkmMap[k] || 0) / 2;
          });
          ['inbound', 'outbound'].forEach(direction => Object.entries(g7tkm[direction] || {}).forEach(([k, amount]) => {
            obj.groups_7_tkm[direction][k] = (obj.groups_7_tkm[direction][k] || 0) + (amount || 0) / 2;
          }));

          // Mode divisions 20 & Mode groups 7
          ['road', 'rail', 'iww'].forEach(m => {
            const divMap = rData.by_mode_divisions?.[m]?.all || rData.by_mode_divisions?.[m] || {};
            Object.keys(divMap).forEach(k => {
              const padK = k.padStart(2, '0');
              obj.by_mode_divisions[m][padK] = (obj.by_mode_divisions[m][padK] || 0) + (divMap[k] || 0) / 2;
            });
            const divTkmMap = rData.by_mode_divisions_tkm?.[m]?.all || rData.by_mode_divisions_tkm?.[m] || {};
            Object.keys(divTkmMap).forEach(k => {
              const padK = k.padStart(2, '0');
              obj.by_mode_divisions_tkm[m][padK] = (obj.by_mode_divisions_tkm[m][padK] || 0) + (divTkmMap[k] || 0) / 2;
            });
            const grpMap = rData.by_mode_groups?.[m]?.all || rData.by_mode_groups?.[m] || {};
            Object.keys(grpMap).forEach(k => {
              obj.by_mode_groups[m][k] = (obj.by_mode_groups[m][k] || 0) + (grpMap[k] || 0) / 2;
              obj.by_mode_groups[m].all[k] = (obj.by_mode_groups[m].all[k] || 0) + (grpMap[k] || 0) / 2;
            });
            ['inbound', 'outbound'].forEach(direction => Object.entries(rData.by_mode_groups?.[m]?.[direction] || {}).forEach(([k, amount]) => {
              obj.by_mode_groups[m][direction][k] = (obj.by_mode_groups[m][direction][k] || 0) + (amount || 0) / 2;
            }));
            const grpTkmMap = rData.by_mode_groups_tkm?.[m]?.all || rData.by_mode_groups_tkm?.[m] || {};
            Object.keys(grpTkmMap).forEach(k => {
              obj.by_mode_groups_tkm[m][k] = (obj.by_mode_groups_tkm[m][k] || 0) + (grpTkmMap[k] || 0) / 2;
              obj.by_mode_groups_tkm[m].all[k] = (obj.by_mode_groups_tkm[m].all[k] || 0) + (grpTkmMap[k] || 0) / 2;
            });
            ['inbound', 'outbound'].forEach(direction => Object.entries(rData.by_mode_groups_tkm?.[m]?.[direction] || {}).forEach(([k, amount]) => {
              obj.by_mode_groups_tkm[m][direction][k] = (obj.by_mode_groups_tkm[m][direction][k] || 0) + (amount || 0) / 2;
            }));
          });
        }
      });

      if (!obj.total_tonnes) {
        obj.total_tonnes = obj.modes_tonnes.road + obj.modes_tonnes.rail + obj.modes_tonnes.iww;
      }
      national[yr] = obj;
    });
    return national;
  }

