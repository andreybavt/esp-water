let currentDate = new Date("01 Jan 2017");
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

let xAxis = d3.axisBottom(x),
    xAxis2 = d3.axisBottom(x2),
    yAxis = d3.axisLeft(y);

let area = d3.area()
    .curve(d3.curveMonotoneX)
    .y0(height)
    .x(function (d) {
        return x(d.date);
    })
    .y1(function (d) {
        return y(d.price);
    });

let brush = d3.brushX()
    .extent([[0, 0], [width, height2]])
    .on("brush end", brushed);

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

let zoom = d3.zoom()
    .scaleExtent([1, Infinity])
    .translateExtent([[0, 0], [width, height]])
    .extent([[0, 0], [width, height]])
    .on("zoom", zoomed);

let focus = svg.append("g")
    .attr("class", "focus")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

let context = svg.append("g")
    .attr("class", "context")
    .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

let data = [];

let focusPath = focus.append("path")
    .datum(data)
    .attr("class", "area");
let xAxisEl = focus.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + height + ")");

let yAxisEl = focus.append("g")
    .attr("class", "axis axis--y");
let contextPath = context.append("path")
    .datum(data)
    .attr("class", "area");

let contextAxisXEl = context.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + height2 + ")");

function type(d) {
    d.date = parseDate(d.date);
    d.price = +d.price;
    return d;
}

let zoomRect = svg.append("rect")
    .attr("class", "zoom")
    .attr("width", width)
    .attr("height", height)
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")").call(zoom);
let brushEl = context.append("g")
    .attr("class", "brush")
    .call(brush);


let zoomedArea;

function redraw() {
    x.domain(d3.extent(data, function (d) {
        return d.date;
    }));
    y.domain([0, d3.max(data, function (d) {
        return d.price;
    })]);
    x2.domain(x.domain());
    y2.domain(y.domain());

    focusPath.attr("d", area);
    xAxisEl.call(xAxis);
    yAxisEl.call(yAxis);

    contextPath.attr("d", area2);
    contextAxisXEl.call(xAxis2);

    if (zoomedArea) {
        brush.extent(zoomedArea)
        // brush(brushEl)
        // brush.event(brushEl)
           brush(brushEl.transition().duration(500));

      // now fire the brushstart, brushmove, and brushend events
      // set transition the delay and duration to 0 to draw right away
      brush.event(brushEl.transition().delay(1000).duration(500))
    }


    // zoomRect.call(zoom, zoomedArea);
    // brushEl.call(brush.move, x.range());

}
// d3.csv("sp500.csv", type, function (error, d) {
//     d.forEach(el => data.push(el));
//     redraw()
// });
// setInterval(function () {
//     let val = Math.random() * 10000;
//     console.log(val);
//     data.push({date: new Date(), price: val});
//     redraw();
// }, 1000);


function zoomed() {
    if (d3.event.sourceEvent && d3.event.sourceEvent.type === "brush") return; // ignore zoom-by-brush
    let t = d3.event.transform;
    x.domain(t.rescaleX(x2).domain());
    focus.select(".area").attr("d", area);
    focus.select(".axis--x").call(xAxis);
    context.select(".brush").call(brush.move, x.range().map(t.invertX, t));
    zoomedArea = x.range().map(t.invertX, t);
    console.log('zoomedArea', zoomedArea);
    // context.select(".brush").call(brush.move, x.range().map(t.invertX, t));
}
function brushed() {
    if (d3.event.sourceEvent && d3.event.sourceEvent.type === "zoom") return; // ignore brush-by-zoom
    let s = d3.event.selection || x2.range();
    x.domain(s.map(x2.invert, x2));
    focus.select(".area").attr("d", area);
    focus.select(".axis--x").call(xAxis);
    svg.select(".zoom").call(zoom.transform, d3.zoomIdentity
        .scale(width / (s[1] - s[0]))
        .translate(-s[0], 0));
}

for (let i = 1; i < 20; i++) {
    let val = Math.random() * 10000;
    console.log(currentDate, val);
    currentDate.setTime(currentDate.getTime() + (1 * 60 * 60 * 1000));
    data.push({date: currentDate.getTime(), price: val});
    redraw();

}