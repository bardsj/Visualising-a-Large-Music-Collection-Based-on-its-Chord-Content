fetch("http://localhost:5000/parallel").then(r => r.json()).then(d => {

    const node_list = d.order
    const data = d.sets

    const width = 1400
    const height = 800

    // Append svg element to chart area
    const svg = d3.select("#chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("display", "block")
        .style("margin", "auto")

    const n_ax = d3.max(data.map(x => x.labels.length))

    let node_list_ax = []

    for (let i = 0; i < n_ax; i++) {
        for (let j = 0; j < node_list.length; j++) {
            node_list_ax.push({ node: node_list[j], ax: i })
        }
    }
    node_list_ax = node_list_ax.flat()

    const data_ax = data.map(d => ({ labels: d.labels.map((l, i) => ({ node: l, ax: i })), values: d.values }))

    const scY = d3.scalePoint().domain(node_list).range([20, height - 20])

    const scX = d3.scaleLinear().domain([0, n_ax - 1]).range([40, width - 10])


    const nodes_group = svg.selectAll("g")
        .data(node_list_ax)
        .enter()
        .append("g")
        .attr("transform", (d) => "translate(" + scX(d.ax) + "," + scY(d.node) + ")")

    const nodes = nodes_group.append("circle")
        .attr("r", 2)

    const labels = nodes_group.append("text")
        .text(d => d.node)
        .attr("font-size", 8)
        .attr("dx", -4)
        .attr("dy", 2)
        .attr("text-anchor", "end")

    const lineGen = d3.line().y(d => scY(d.node)).x(d => scX(d.ax))

    const links = svg.selectAll("path")
        .data(data_ax)
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("d", d => lineGen(d.labels))
        .attr("fill", "none")
        .attr("stroke", "black")
        .attr("fill", "none")
        .attr("stroke-width", 1)
        .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** 3)

    nodes_group.on("mouseenter", (sel) => {
        d3.select(this).raise()
        d3.selectAll(".link")
            //.filter(d=>d.labels.includes(sel.label))
            .filter(d => d.labels[sel.ax] ? d.labels[sel.ax].node === sel.node : null)
            .raise()
            .transition(0.1)
            .attr("stroke", "red")
            .attr("stroke-width", 3)
            .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** 1.5)
    })

    nodes_group.on("mouseleave", (sel) => {
        d3.selectAll(".link")
            .filter(d => d.labels[sel.ax] ? d.labels[sel.ax].node === sel.node : null)
            .transition(0.1)
            .attr("stroke", "black")
            .attr("stroke-width", 1)
            .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** 3)
    })

})