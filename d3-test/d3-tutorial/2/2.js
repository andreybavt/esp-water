let currentDate = new Date();
let zoomedDomain;
let data = [];
for (let i = 0; i < 10; i++) {
    pushGeneratedDatum();
}


let svg = d3.select("svg"),
    margin = {top: 20, right: 20, bottom: 110, left: 40},
    margin2 = {top: 430, right: 20, bottom: 30, left: 40},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom,
    height2 = +svg.attr("height") - margin2.top - margin2.bottom;

let parseDate = d3.timeParse("%b %Y");

let x = d3.scaleTime().range([0, width]),
    x2 = d3.scaleTime().range([0, width]),
    y = d3.scaleLinear().range([height, 0]),
    y2 = d3.scaleLinear().range([height2, 0]);

let focusXaxisGenerator = d3.axisBottom(x),
    contextXaxisGenerator = d3.axisBottom(x2),
    focusYaxisGenerator = d3.axisLeft(y);

let brush = d3.brushX()
    .extent([[0, 0], [width, height2]])
    .on("brush end", brushed);

let zoom = d3.zoom()
    .scaleExtent([1, Infinity])
    .translateExtent([[0, 0], [width, height]])
    .extent([[0, 0], [width, height]])
    .on("zoom", zoomed);

let area = d3.area()
    .curve(d3.curveMonotoneX)
    .x(function (d) {
        return x(d.date);
    })
    .y0(height)
    .y1(function (d) {
        return y(d.price);
    });

let area2 = d3.area()
    .curve(d3.curveMonotoneX)
    .x(function (d) {
        return x2(d.date);
    })
    .y0(height2)
    .y1(function (d) {
        return y2(d.price);
    });

svg.append("defs").append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("width", width)
    .attr("height", height);

let focus = svg.append("g")
    .attr("class", "focus")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

let context = svg.append("g")
    .attr("class", "context")
    .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");


let mainPath = focus.append("path")
    .datum(data)
    .attr("class", "area");
let contextPath = context.append("path")
    .datum(data)
    .attr("class", "area");
let focusYaxis = focus.append("g")
    .attr("class", "axis axis--y");
let focusXaxis = focus.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + height + ")");
let contextXaxis = context.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + height2 + ")");

context.append("g")
    .attr("class", "brush")
    .call(brush)
    .call(brush.move, x.range());
svg.append("rect")
    .attr("class", "zoom")
    .attr("width", width)
    .attr("height", height)
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .call(zoom);

function redraw() {
    x.domain(d3.extent(data, d => d.date));
    x2.domain(d3.extent(data, d => d.date));
    y.domain([0, d3.max(data, d => d.price)]);

    y2.domain(y.domain());
    let xExtent = d3.extent(data, d => d.date);
    if (zoomedDomain) {
        if (zoomedDomain[1].getTime() === data[data.length - 2].date) {
            if (zoomedDomain[0].getTime() === data[0].date) {
                zoomedDomain = d3.extent(data, d => d.date);
            } else {
                let zoomDomainInPixels = zoomedDomain.map(x2);
                let zoomDomainPixelWidth = zoomDomainInPixels[1] - zoomDomainInPixels[0];
                let newEnd = x2(data[data.length - 1].date);
                zoomedDomain = [newEnd - zoomDomainPixelWidth, newEnd].map(x2.invert)
            }
        }
        context.select(".brush").call(brush.move, zoomedDomain.map(x2));
        x.domain(zoomedDomain)

    }


    mainPath.attr("d", area);
    focusXaxis.call(focusXaxisGenerator);
    focusYaxis.call(focusYaxisGenerator);
    contextXaxis.call(contextXaxisGenerator);

    contextPath.attr("d", area2);
}

function brushed() {
    if (d3.event.sourceEvent && d3.event.sourceEvent.type === "zoom") return; // ignore brush-by-zoom
    let s = d3.event.selection || x2.range();
    x.domain(s.map(x2.invert, x2));
    focus.select(".area").attr("d", area);
    focus.select(".axis--x").call(focusYaxisGenerator);
    svg.select(".zoom").call(zoom.transform, d3.zoomIdentity
        .scale(width / (s[1] - s[0]))
        .translate(-s[0], 0));
}

function zoomed() {
    if (d3.event.sourceEvent && d3.event.sourceEvent.type === "brush") return; // ignore zoom-by-brush
    let t = d3.event.transform;
    zoomedDomain = t.rescaleX(x2).domain();
    x.domain(zoomedDomain);
    focus.select(".area").attr("d", area);
    focus.select(".axis--x").call(focusXaxisGenerator);
    context.select(".brush").call(brush.move, x.range().map(t.invertX, t));
}

redraw();
setInterval(function () {
    pushGeneratedDatum();
    // data.push({date: n-ew Date(), price: Math.random() * 5000});
    redraw();
}, 300);
function pushGeneratedDatum() {
    let val = Math.random() * 5000;
    // console.log(currentDate, val);
    currentDate.setTime(currentDate.getTime() + (1 * 60 * 60 * 1000));
    data.push({date: currentDate.getTime(), price: val});
}
function addData() {
    pushGeneratedDatum();

    redraw();
}