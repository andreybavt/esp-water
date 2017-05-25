let svg = d3.select("svg")
        .attr('width', d3.select('body').node().getBoundingClientRect().width)
        .attr('height', d3.select('body').node().getBoundingClientRect().height * 2),
    margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom,
    g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var zoom = d3.zoom()
    .scaleExtent([1, Infinity])
    .translateExtent([[0, 0], [width, height]])
    .extent([[0, 0], [width, height]])
    .on("zoom", zoomed);

svg.append("rect")
    .attr("class", "zoom-interceptor")
    .attr("width", width)
    .attr("height", height)
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .call(zoom);

function zoomed() {
    if (d3.event.sourceEvent && d3.event.sourceEvent.type === "brush") return; // ignore zoom-by-brush
    let t = d3.event.transform;
    x.domain(t.rescaleX(x).domain());
    g.select(".area").attr("d", area);
    g.select(".axis--x").call(xAxis);
    // context.select(".brush").call(brush.move, x.range().map(t.invertX, t));
}

let x = d3.scaleTime()
    .rangeRound([0, width]);

let y = d3.scaleLinear()
    .rangeRound([height, 0]);

let path = g.append("path")
    .attr("fill", "none")
    .attr("class", "area")
    .attr("stroke", "steelblue")
    .attr("stroke-linejoin", "round")
    .attr("stroke-linecap", "round")
    .attr("stroke-width", 1.5)
    .datum(data);

let area = d3.area()
    .curve(d3.curveMonotoneX)
    .x(d => x(d.date))
    .y0(height)
    .y1(d => y(d.val))


let xAxisG = g.append("g")
    .attr("transform", "translate(0," + height + ")")
    .attr('class','axis--x');
let yAxisG = g.append("g");

yAxisG
    .append("text")
    .attr("fill", "#000")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", "0.71em")
    .attr("text-anchor", "end")
    .text("Price ($)");
let xAxis = d3.axisBottom(x);
let yAxis = d3.axisLeft(y);

function redraw() {
    x.domain(d3.extent(data, function (d) {
        return d.date;
    }));
    y.domain(d3.extent(data, function (d) {
        return d.val;
    }));

    xAxisG.call(xAxis);
    yAxisG.call(yAxis);
    path
        .attr("d", area)
        .attr("fill", "steelblue")
}

redraw();
// setInterval(() => {
//     data.push({date: new Date(), val: Math.random() * 1000});
//     redraw();
//
// }, 3000);