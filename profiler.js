// GLOBAL STATE
let calls = {};
let idMap = {};
let treeRoot = null;
let processedBatches = 0;
const renderEvery = 5;
const MAX_NODES = 5000;
const MAX_TIMELINE = 5000;

// Streaming batch processing
function processBatch(batch) {
  for (const entry of batch) {
    const id = entry.call_id;
    if (!calls[id]) {
      calls[id] = {
        call_id: id,
        parent_call_id: entry.parent_call_id,
        function: entry.function,
        type: entry.type,
        start: null,
        end: null
      };
    }
    if (entry.event === "start") {
      calls[id].start = parseTime(entry.time);
    } else if (entry.event === "end") {
      calls[id].end = parseTime(entry.time);
    }
  }
  processedBatches++;
}

function maybeRender() {
  if (processedBatches % renderEvery === 0) {
    renderPartial();
  }
}

function renderPartial() {
  const partialAgg = computeAggregates(Object.values(calls));
  renderSummary(partialAgg);
}

function finalizeProcessing() {
  idMap = buildCallMap(calls);
  treeRoot = buildTree(idMap);
  renderTree(treeRoot);
  renderTimeline(Object.values(calls));
  renderSummary(computeAggregates(Object.values(calls)));
  renderFlamegraph(buildFlamegraphTree(calls));
  if (treeRoot) showFunctionDetails(treeRoot);
}

function parseTime(timeStr) {
  const [h, m, s] = timeStr.split(':');
  const [sec, ms = "0"] = s.split('.');
  const date = new Date();
  date.setHours(parseInt(h), parseInt(m), parseInt(sec), parseInt(ms));
  return date;
}

function buildCallMap(calls) {
  const map = {};
  for (const id in calls) {
    map[id] = { ...calls[id], children: [], expanded: false };
  }
  for (const id in map) {
    const node = map[id];
    if (node.parent_call_id != null && map[node.parent_call_id]) {
      map[node.parent_call_id].children.push(node);
    }
  }
  return map;
}
function flattenVisibleTree(node, result = [], depth = 0) {
  result.push({ node, depth });
  if (node.expanded) {
    for (const child of node.children) {
      flattenVisibleTree(child, result, depth + 1);
    }
  }
  return result;
}

function buildTree(idMap) {
  for (const id in idMap) {
    if (idMap[id].parent_call_id == null || !idMap[idMap[id].parent_call_id]) {
      return idMap[id];
    }
  }
  return null;
}

function renderTree(treeData) {
  if (!treeData) return;

  const container = document.getElementById("tree");
  container.innerHTML = "";

  const table = document.createElement("table");
  table.className = "profiler-table";
  container.appendChild(table);

  const visibleNodes = flattenVisibleTree(treeData);
  
  for (const { node, depth } of visibleNodes) {
    const row = table.insertRow();
    const cell = row.insertCell();

    cell.style.paddingLeft = (depth * 20) + "px";

    // Expand/collapse toggle
    if (node.children.length > 0) {
      const toggle = document.createElement("span");
      toggle.textContent = node.expanded ? "▼ " : "▶ ";
      toggle.style.cursor = "pointer";
      toggle.onclick = () => {
        node.expanded = !node.expanded;
        renderTree(treeData); // re-render after toggle
      };
      cell.appendChild(toggle);
    } else {
      cell.textContent = "• ";
    }

    const label = document.createElement("span");
    label.textContent = `${node.function} (${node.call_id})`;
    label.style.cursor = "pointer";
    label.onclick = () => showFunctionDetails(node);
    cell.appendChild(label);
  }
}
// === SAFE TIMELINE RENDERING ===
function renderTimeline(callArray) {
  const limited = callArray.slice(0, MAX_TIMELINE);
  const bars = limited.map(call => {
    let end = call.end || new Date();
    return {
      x: [call.start, end],
      y: [call.function + ` [${call.call_id}]`, call.function + ` [${call.call_id}]`],
      mode: 'lines',
      type: 'scatter',
      name: `${call.function} [${call.call_id}]`,
      call_id: call.call_id
    };
  });

  Plotly.newPlot('timeline', bars, {
    title: 'Global Timeline',
    xaxis: { type: 'date' },
    paper_bgcolor: '#1e1e1e',
    plot_bgcolor: '#1e1e1e',
    font: { color: '#dcdcdc' },
    height: document.getElementById("timeline").clientHeight
  });
}

function showFunctionDetails(data) {
  let html = "<table class='profiler-table'>";
  html += "<thead><tr><th colspan='2'>Function Details</th></tr></thead><tbody>";
  html += `<tr><td>Function:</td><td>${data.function}</td></tr>`;
  html += `<tr><td>Call ID:</td><td>${data.call_id}</td></tr>`;
  if (data.parent_call_id && idMap[data.parent_call_id]) {
    html += `<tr><td>Parent:</td><td>${idMap[data.parent_call_id].function} (${data.parent_call_id})</td></tr>`;
  }
  html += `<tr><td>Start:</td><td>${data.start || "missing"}</td></tr>`;
  html += `<tr><td>End:</td><td>${data.end || "missing"}</td></tr>`;
  if (data.start && data.end)
    html += `<tr><td>Duration:</td><td>${data.end - data.start} ms</td></tr>`;
  else
    html += `<tr><td>Duration:</td><td>incomplete</td></tr>`;
  html += "</tbody></table>";
  document.getElementById("functionInfo").innerHTML = html;
}

function computeAggregates(callArray) {
  const agg = {};
  for (const call of callArray) {
    if (!agg[call.function]) {
      agg[call.function] = { count: 0, total: 0 };
    }
    agg[call.function].count += 1;
    if (call.start && call.end) {
      agg[call.function].total += (call.end - call.start);
    }
  }
  return agg;
}

function renderSummary(aggregates) {
  let html = "<table class='profiler-table'>";
  html += "<thead><tr><th>Function</th><th>Calls</th><th>Total Time (ms)</th></tr></thead><tbody>";
  const sorted = Object.entries(aggregates).sort((a, b) => b[1].total - a[1].total);
  for (const [func, stat] of sorted) {
    html += `<tr><td>${func}</td><td>${stat.count}</td><td>${stat.total}</td></tr>`;
  }
  html += "</tbody></table>";
  document.getElementById("summaryTable").innerHTML = html;
}

function buildFlamegraphTree(calls) {
  const root = { name: "__ROOT__", value: 0, children: [] };

  for (const call of Object.values(calls)) {
    let current = call;
    const path = [];
    while (current) {
      path.unshift(current.function);
      current = current.parent_call_id ? calls[current.parent_call_id] : null;
    }

    let node = root;
    for (const func of path) {
      let child = node.children.find(c => c.name === func);
      if (!child) {
        child = { name: func, value: 0, children: [] };
        node.children.push(child);
      }
      node = child;
    }
    if (call.start && call.end)
      node.value += call.end - call.start;
  }
  return root;
}

function renderFlamegraph(data) {
  document.getElementById("flamegraphView").innerHTML = "";
  const width = document.getElementById("flamegraphView").clientWidth;
  const height = 400;

  const partition = d3.partition().size([width, height]);
  const root = d3.hierarchy(data).sum(d => d.value);
  partition(root);

  const color = d3.scaleOrdinal(d3.schemeTableau10);

  const svg = d3.select("#flamegraphView").append("svg")
    .attr("width", width)
    .attr("height", height);

  svg.selectAll("rect")
    .data(root.descendants())
    .enter().append("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0)
    .attr("fill", d => color(d.data.name))
    .append("title")
    .text(d => `\${d.data.name}: \${Math.round(d.value)} ms`);
}
