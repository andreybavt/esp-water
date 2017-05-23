let zoomedDomain;
let data = [{"date": "2017-05-23T00:48:00.042Z", "price": 3750.7523729179316}, {
    "date": "2017-05-23T00:48:00.242Z",
    "price": 4583.519924430146
}, {"date": "2017-05-23T00:48:00.442Z", "price": 2145.8942565252214}, {
    "date": "2017-05-23T00:48:00.643Z",
    "price": 3387.588318533732
}, {"date": "2017-05-23T00:48:00.842Z", "price": 3908.835931214709}, {
    "date": "2017-05-23T00:48:01.042Z",
    "price": 4075.0430377549383
}, {"date": "2017-05-23T00:48:01.244Z", "price": 1632.135951692778}, {
    "date": "2017-05-23T00:48:01.442Z",
    "price": 1274.3265916105684
}, {"date": "2017-05-23T00:48:01.642Z", "price": 297.13472951311326}, {
    "date": "2017-05-23T00:48:01.843Z",
    "price": 2686.953631528086
}, {"date": "2017-05-23T00:48:02.042Z", "price": 336.09172076612515}, {
    "date": "2017-05-23T00:48:02.242Z",
    "price": 2989.9877647900353
}, {"date": "2017-05-23T00:48:02.442Z", "price": 3814.228075485432}, {
    "date": "2017-05-23T00:48:02.642Z",
    "price": 4060.3422034818227
}, {"date": "2017-05-23T00:48:02.842Z", "price": 4198.655079525078}, {
    "date": "2017-05-23T00:48:03.042Z",
    "price": 4008.585361830571
}, {"date": "2017-05-23T00:48:03.242Z", "price": 3960.0963005487556}, {
    "date": "2017-05-23T00:48:03.442Z",
    "price": 2354.011212395537
}, {"date": "2017-05-23T00:48:03.642Z", "price": 4385.954019710887}, {
    "date": "2017-05-23T00:48:03.842Z",
    "price": 1529.1183142169796
}, {"date": "2017-05-23T00:48:04.042Z", "price": 1417.3946722000874}, {
    "date": "2017-05-23T00:48:04.242Z",
    "price": 1185.2718974982902
}, {"date": "2017-05-23T00:48:04.442Z", "price": 3067.6119179817974}, {
    "date": "2017-05-23T00:48:04.642Z",
    "price": 4716.778060115446
}, {"date": "2017-05-23T00:48:04.842Z", "price": 2424.9844015031154}, {
    "date": "2017-05-23T00:48:05.042Z",
    "price": 1410.7133455625897
}, {"date": "2017-05-23T00:48:05.242Z", "price": 3022.5621663308834}, {
    "date": "2017-05-23T00:48:05.442Z",
    "price": 2910.3135901030987
}, {"date": "2017-05-23T00:48:05.643Z", "price": 3491.1771084672637}, {
    "date": "2017-05-23T00:48:05.842Z",
    "price": 2162.7355717985542
}, {"date": "2017-05-23T00:48:06.042Z", "price": 3705.255387516618}, {
    "date": "2017-05-23T00:48:06.242Z",
    "price": 2176.750982173401
}, {"date": "2017-05-23T00:48:06.442Z", "price": 43.71869101844283}, {
    "date": "2017-05-23T00:48:06.642Z",
    "price": 2930.4176454142716
}, {"date": "2017-05-23T00:48:06.842Z", "price": 3395.7192927079327}].map(el => {
    el.date = new Date(el.date);
    return el
});
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
    x.domain(d3.extent(data, function (d) {
        return d.date;
    }));
    y.domain([0, d3.max(data, function (d) {
        return d.price;
    })]);
    x2.domain(x.domain());
    y2.domain(y.domain());

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
    x.domain(t.rescaleX(x2).domain());
    focus.select(".area").attr("d", area);
    focus.select(".axis--x").call(focusYaxisGenerator);
    context.select(".brush").call(brush.move, x.range().map(t.invertX, t));
}

redraw();
// setInterval(function () {
//     data.push({date: new Date(), price: Math.random() * 5000});
//     redraw();
// }, 200);
function addData() {
    data.push({date: new Date(), price: Math.random() * 5000});

    redraw();
}