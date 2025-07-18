// GLOBAL STATE
let calls = {};
let deadBeat = {};
let idMap = {};
let aggregates = {};
let processedBatches = 0;
const renderEvery = 5;
let currentRoot = null;



// processing 

function finalizeProcessing() {
  const forest = buildForest(calls);
  renderForest(forest);
  renderTimeline(Object.values(calls));
  renderSummary(aggregates);
  addToFlamegraph(forest);
  renderFlamegraph(flamegraphRoot);
  if (forest) showFunctionDetails(forest[0]);
}

function maybeRender() {
  if (processedBatches % renderEvery === 0) {
    requestSummaryRender();
    renderForestSnapshot = buildForest(calls);
    requestTreeRender(renderForestSnapshot);
    
    if (flamegraphActive){ addToFlamegraph(renderForestSnapshot); requestFlamegraphRender();}
    // renderTimeline(Object.values(calls));
  }
}

function processBatch(batch) {
  for (const entry of batch) {
    const id = entry.call_id;
    var cCall;
    // Create or update call
    if (!calls[id]) {
      calls[id] = {
        call_id: id,
        parent_call_id: entry.parent_call_id,
        function: entry.function,
        type: entry.is_async == 1 ? 'async' : 'sync',
        children: new Set(),
        expanded: false,
        start: entry.start,
        duration: entry.duration
      };
    }

    cCall = calls[id];



    // update aggregates
    if (!aggregates[entry.function]) {
      aggregates[entry.function] = { count: 0, total: 0 };
    }
    aggregates[entry.function].count += 1;
    aggregates[entry.function].total += entry.duration;


    // Link to parent and child
    if (cCall.parent_call_id) {
      if (!calls[cCall.parent_call_id]) {
        if (!deadBeat[cCall.parent_call_id])
          deadBeat[cCall.parent_call_id] = [];
        deadBeat[cCall.parent_call_id].push(cCall.call_id)
      } else {
        calls[cCall.parent_call_id].children.add(cCall.call_id);
      }
    }

    if (deadBeat[cCall.call_id]) {
      deadBeat[cCall.call_id].forEach(element => {
        cCall.children.add(element);
      });
      deadBeat[cCall.call_id] = null;
    }

  }
  processedBatches++;
}


// details handler ===============================================================================================================================================================================================================
function showFunctionDetails(data) {
  let html = "<table class='profiler-table'>";
  html += "<thead><tr><th colspan='2'>Function Details</th></tr></thead><tbody>";
  html += `<tr><td>Function:</td><td>${data.function}</td></tr>`;
  html += `<tr><td>Call ID:</td><td>${data.call_id}</td></tr>`;
  if (data.parent_call_id && calls[data.parent_call_id]) {
    html += `<tr><td>Parent:</td><td>${calls[data.parent_call_id].function} (${data.parent_call_id})</td></tr>`;
  }
  html += `<tr><td>Start:</td><td>${data.start || "missing"}</td></tr>`;
  html += `<tr><td>End:</td><td>${data.start + data.duration || "missing"}</td></tr>`;
  html += `<tr><td>Duration:</td><td>${data.duration || "missing"} ms</td></tr>`;
  html += "</tbody></table>";
  document.getElementById("functionInfo").innerHTML = html;
}

// timeline handler ===============================================================================================================================================================================================================
const MAX_TIMELINE = 5000;
function renderTimeline(callArray) {
  const limited = callArray.slice(0, MAX_TIMELINE);
  const bars = limited.map(call => {
    const startSec = call.start / 1000
    const endSec = (call.start + call.duration) / 1000;
    const durationSec = call.duration / 1000;
    if (durationSec < 1)
      t = `<br>Duration: ${durationSec* 1000} ms</br><extra></extra>`
    else
      t = `<br>Duration: ${durationSec} s</br><extra></extra>`
    
    return {
      x: [startSec, endSec],
      y: [call.function + ` [${call.call_id}]`, call.function + ` [${call.call_id}]`],
      mode: 'lines',
      type: 'scatter',
      name: `${call.function} [${call.call_id}]`,
      line: { width: 15 },  // increased from
      call_id: call.call_id,
      hovertemplate: t

    };
  });

  Plotly.newPlot('timeline', bars, {
    title: 'Global Timeline',
    xaxis: {
      title: 'Time (s)',
      tickformat: '.1f',
      zeroline: false
    },
    paper_bgcolor: '#1e1e1e',
    plot_bgcolor: '#1e1e1e',
    font: { color: '#dcdcdc' },
    height: document.getElementById("timeline").clientHeight,
    hovermode: 'closest'
  });
}

// Summary handler ===============================================================================================================================================================================================================
let summaryLastRender = 0;
const summaryRenderInterval = 100;


function requestSummaryRender() {
  const now = performance.now();
  if (now - summaryLastRender >= summaryRenderInterval) {
    summaryLastRender = now;
    renderSummary(aggregates);
  }
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


// Flame graph handler ===============================================================================================================================================================================================================
let flamegraphLastRender = 0;
const flamegraphRenderInterval = 1000;

let resizeObserver;

let flamegraphRenderTimeout = null;

let flamegraphSVG = null;
let flamegraphG = null;
let flamegraphPendingRender = false;
let flamegraphRoot = { name: "__ROOT__", value: 0, children: [] };
const color = d3.scaleOrdinal(d3.schemeTableau10);

function getNodePath(d) {
  return d.ancestors().map(n => n.data.name).reverse().join("/");
}
function renderFlamegraph(data) {
  const container = document.getElementById("flamegraphView");
  const width = container.clientWidth;
  const height = container.clientHeight;
  if (width === 0 || height === 0) return;

  const partition = d3.partition().size([width, height]);
  const root = d3.hierarchy(data).sum(d => d.value);
  partition(root);

  // Save for semantic zoom
  currentRoot = data;

  const MIN_WIDTH = 0;
  const nodes = root.descendants().filter(d => (d.x1 - d.x0) > MIN_WIDTH);

  if (!flamegraphSVG) {
    flamegraphSVG = d3.select("#flamegraphView").append("svg")
      .attr("width", width).attr("height", height);

    flamegraphG = flamegraphSVG.append("g");

    const zoom = d3.zoom().scaleExtent([0.5, 10])
      .on("zoom", (event) => flamegraphG.attr("transform", event.transform));
    flamegraphSVG.call(zoom);

    const button = document.createElement("button");
    button.innerText = "Zoom Out";
    button.style.position = "absolute";
    button.style.top = "10px";
    button.style.right = "20px";
    button.style.zIndex = 1000;
    button.style.padding = "8px 15px";
    button.style.background = "orange";
    button.style.border = "none";
    button.style.color = "#fff";
    button.style.fontWeight = "bold";
    button.style.cursor = "pointer";
    document.body.appendChild(button);
    button.onclick = () => {
      renderFlamegraph(flamegraphRoot);
    };
  } else {
    flamegraphSVG.attr("width", width).attr("height", height);
  }

  const rects = flamegraphG.selectAll("g.node").data(nodes, getNodePath);
  rects.exit().remove();

  const enter = rects.enter().append("g").attr("class", "node");
  enter.append("rect");
  enter.append("title");

  const merged = enter.merge(rects);

  merged.select("rect")
    .attr("x", d => d.x0).attr("y", d => d.y0)
    .attr("width", d => d.x1 - d.x0).attr("height", d => d.y1 - d.y0)
    .attr("fill", d => color(d.data.name))
    .on("click", (event, d) => zoomIntoNode(d))
    .on("mouseover", function (event, d) {
      d3.select(this).attr("stroke", "#fff").attr("stroke-width", 2);
      showTooltip(event, d);
    })
    .on("mouseout", function () {
      d3.select(this).attr("stroke", null);
      hideTooltip();
    });

  merged.select("title").text(d => `${d.data.name}: ${Math.round(d.value)} ms`);
}

function zoomIntoNode(target, partition, root) {
  const container = document.getElementById("flamegraphView");
  const width = container.clientWidth;
  const height = container.clientHeight;

  const x = d3.scaleLinear().domain([target.x0, target.x1]).range([0, width]);
  const y = d3.scaleLinear().domain([target.y0, root.y1]).range([0, height]);

  flamegraphG.selectAll("g.node").select("rect").transition().duration(750)
    .attr("x", d => x(d.x0))
    .attr("y", d => y(d.y0))
    .attr("width", d => x(d.x1) - x(d.x0))
    .attr("height", d => y(d.y1) - y(d.y0));
}

const tooltip = d3.select("body")
  .append("div")
  .style("position", "absolute")
  .style("padding", "8px")
  .style("background", "#333")
  .style("color", "#fff")
  .style("border-radius", "5px")
  .style("visibility", "hidden");

function showTooltip(event, d) {
  tooltip.style("visibility", "visible")
    .html(`<b>${d.data.name}</b><br>${Math.round(d.value)} ms`)
    .style("top", (event.pageY - 10) + "px")
    .style("left", (event.pageX + 10) + "px");
}

function hideTooltip() {
  tooltip.style("visibility", "hidden");
}

function addToFlamegraph(call) {
  flamegraphRoot = { name: "__ROOT__", value: 0, children: [] };
  call.forEach(element => {
    flamegraphRoot.children.push(get_path_from_root(element));
  });
}


function get_path_from_root(call) {

    const node = {
        name: call.function,
        value: call.duration,
        children: []
    };

    // Recurse over children, if any
    if (call.children && call.children.size > 0) {
        for (const childCall of call.children) {
            node.children.push(get_path_from_root(calls[childCall]));
        }
    }
    return node;
  

}

function requestFlamegraphRender() {

  const now = performance.now();
  if (now - flamegraphLastRender >= flamegraphRenderInterval) {
    summaryLastRender = now;
    currentRoot = flamegraphRoot;
    renderFlamegraph(flamegraphRoot);
  }
}
function zoomIntoNode(d) {
  renderFlamegraph(d.data); // drill into this node
}
// tree Handler ===============================================================================================================================================================================================================
let treeLastRender = 0;
const treeRenderInterval = 100;
const BUFFER_ROWS = 10;  // render slightly more than viewport to avoid blank areas
let rowPool = [];



function requestTreeRender(renderForestSnapshot) {
  const now = performance.now();
  if (now - treeLastRender >= treeRenderInterval) {
    treeLastRender = now;
    renderVirtualTree(renderForestSnapshot);
  }
}
function buildForest(calls) {
  const roots = [];
  for (const id in calls) {
    const node = calls[id];
    if (!node.parent_call_id || !calls[node.parent_call_id]) {
      roots.push(node);
    }
  }
  return roots;
}
function flattenVisibleTree(node, result = [], depth = 0) {
  result.push({ node, depth });
  if (node.expanded) {
    for (const child of node.children) {
      flattenVisibleTree(calls[child], result, depth + 1);
    }
  }
  return result;
}

function renderForest(forest) {
  const container = document.getElementById("tree");
  container.innerHTML = "";

  const table = document.createElement("table");
  table.className = "profiler-table";
  container.appendChild(table);

  for (const root of forest) {
    renderSubtree(root, table, 0);
  }
}

function renderSubtree(node, table, depth) {
  const row = table.insertRow();
  const cell = row.insertCell();
  cell.style.paddingLeft = (depth * 20) + "px";

  if (node.children.size > 0) {
    const toggle = document.createElement("span");
    toggle.textContent = node.expanded ? "▼ " : "▶ ";
    toggle.style.cursor = "pointer";
    toggle.onclick = () => {
      node.expanded = !node.expanded;
      renderForest(buildForest(calls));
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

  if (node.expanded) {
    for (const child of node.children) {
      renderSubtree(calls[child], table, depth + 1);
    }
  }
}

const ROW_HEIGHT = 25;

function renderVirtualTree(forest) {
  const container = document.getElementById("tree");
  const visibleNodes = [];
  for (const root of forest) {
    flattenVisibleTree(root, visibleNodes);
  }

  const totalHeight = visibleNodes.length * ROW_HEIGHT;

  let scroller;
  if (rowPool.length === 0) {
    const viewportHeight = container.clientHeight;
    const poolSize = Math.ceil(viewportHeight / ROW_HEIGHT) + BUFFER_ROWS;
    scroller = initRowPool(container, poolSize);
  } else {
    scroller = container.firstChild;
  }

  scroller.style.height = totalHeight + "px";

  // Attach scroll handler
  container.onscroll = () => {
    updateVirtualTree(container, scroller, visibleNodes);
  };

  updateVirtualTree(container, scroller, visibleNodes);
}

function updateVirtualTree(container, scroller, visibleNodes) {
  const scrollTop = container.scrollTop;
  const firstIndex = Math.floor(scrollTop / ROW_HEIGHT);
  const poolSize = rowPool.length;

  for (let i = 0; i < poolSize; i++) {
    const nodeIndex = firstIndex + i;
    const row = rowPool[i];

    if (nodeIndex >= visibleNodes.length) {
      row.style.display = "none";
      continue;
    }

    row.style.display = "flex";
    row.style.top = (nodeIndex * ROW_HEIGHT) + "px";
    const { node, depth } = visibleNodes[nodeIndex];

    row.innerHTML = "";  // Replace with smart row reuse later

    row.style.paddingLeft = (depth * 20) + "px";

    if (node.children.size > 0) {
      const toggle = document.createElement("span");
      toggle.textContent = node.expanded ? "▼ " : "▶ ";
      toggle.style.marginRight = "5px";
      toggle.onclick = (e) => {
        e.stopPropagation();
        node.expanded = !node.expanded;
        renderVirtualTree(buildForest(calls));
      };
      row.appendChild(toggle);
    } else {
      row.appendChild(document.createTextNode("• "));
    }

    const label = document.createElement("span");
    label.textContent = `${node.function} (${node.call_id})`;
    label.onclick = () => showFunctionDetails(node);
    row.appendChild(label);
  }
}

function initRowPool(container, poolSize) {
  const scroller = document.createElement("div");
  scroller.style.position = "relative";
  scroller.style.width = "100%";
  container.innerHTML = "";
  container.appendChild(scroller);
  rowPool = [];

  for (let i = 0; i < poolSize; i++) {
    const row = document.createElement("div");
    row.style.position = "absolute";
    row.style.left = "0";
    row.style.right = "0";
    row.style.height = ROW_HEIGHT + "px";
    row.style.display = "flex";
    row.style.alignItems = "center";
    row.style.paddingLeft = "0px";
    row.style.cursor = "pointer";
    rowPool.push(row);
    scroller.appendChild(row);
  }

  return scroller;
}



// Helper functions ===============================================================================================================================================================================================================

function parseTime(timeStr) {
  const [h, m, s] = timeStr.split(':');
  const [sec, ms = "0"] = s.split('.');
  const date = new Date();
  date.setHours(parseInt(h), parseInt(m), parseInt(sec), parseInt(ms));
  return date;
}


