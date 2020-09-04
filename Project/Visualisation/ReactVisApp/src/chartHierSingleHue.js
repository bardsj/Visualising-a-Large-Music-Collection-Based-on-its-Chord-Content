import React from "react";
import * as d3 from 'd3';

export class ChartHierSingleHue extends React.Component {
    constructor(props) {
        super(props)
        this.state = { data: null, request_params: null }
    }

    fetchData(request_params, majMinSel) {
        let r_url = ""
        if (request_params.tag_val.length > 0) {
            r_url = "http://127.0.0.1:5000/circHier?tag_val=" + request_params.tag_val.join() + "&tag_name=" + request_params.tag_name
        }
        else {
            r_url = "http://127.0.0.1:5000/circHier?"
        }
        if (request_params.optType) {
            r_url = r_url + "&order_opt=" + request_params.optType
        }
        if (request_params.majMinSel) {
            r_url = r_url + "&majmin_agg=" + request_params.majMinSel
        }
        if (request_params.fi_type) {
            r_url = r_url + "&fi_type=" + request_params.fi_type
        }
        fetch(r_url, { mode: 'cors' })
            .then(r => r.json())
            .then(r => this.setState({ data: r, request_params: request_params }, () => { this.createChart() }))

    }

    componentDidMount() {
        this.fetchData(this.props.request_params)
    }

    componentDidUpdate(prevProps) {
        if (prevProps.request_params !== this.props.request_params) {
            if (prevProps.request_params.support !== this.props.request_params.support) {
                this.createChart()
            }
            else if (prevProps.request_params.focus !== this.props.request_params.focus) {
                this.updateFocus()
            }
            else {
                this.fetchData(this.props.request_params)
            }
        }
        if (prevProps.queryParams !== this.props.queryParams) {
            this.createChart()
        }
    }

    createChart() {
        // Set condition to loop through if no genres are selected
        let genres_tmp = ["all"]
        if (this.state.request_params.tag_val.length > 0) {
            genres_tmp = this.state.request_params.tag_val
        }
        // Iterate over genres and create new chart on selected svg
        for (let tag_ix = 0; tag_ix < genres_tmp.length; tag_ix++) {
            const svg = d3.select(this.refs[genres_tmp[tag_ix] + 'chartsvg'])
            svg.selectAll("*").remove()
            const width = svg.node().getBoundingClientRect().width
            const height = svg.node().getBoundingClientRect().height
            let order = this.state.data.order
            let sets = this.state.data.sets
            if (this.state.request_params.tag_val.length > 0) {
                sets = sets.filter(x => x.tag == genres_tmp[tag_ix])
            }
            // Filter based on slider support val
            sets = sets.filter(x => x.values > this.props.request_params.support / 100)
            if (this.props.queryParams['chordSel'].length > 0) {
                sets = sets.filter(x => x.labels.some(r => this.props.queryParams['chordSel'].includes(r)))
            }
            const r = (height / 2) - height / 16;

            // Filter out nodes from order that all not in filtered sets
            //const filtered_set = new Array(... new Set(sets.flatMap(x => x['labels'])))
            //order = order.filter(x => filtered_set.includes(x))

            // Calculate radial coordinate from ordered list of nodes
            const sc_radial = d3.scalePoint().domain(order).range([0, Math.PI * 2 - (Math.PI * 2 / order.length)])

            // Colour map
            //const scColor = d3.scaleSequential().domain([0,d3.max(sets.flatMap(x=>x.values))]).interpolator(d3.interpolateYlOrRd)
            const scColor = d3.scaleSequential().domain([0, 0.2]).interpolator(d3.interpolateYlOrRd)

            // Convert radial coordinate to cartesian
            const node2point = (d) => {
                return { x: r * Math.sin(sc_radial(d)), y: r * Math.cos(sc_radial(d)) }
            }

            // Centre of the circle
            const centre = { x: width / 2, y: width / 2 }

            // If no opt type selected (i.e. root node order)
            if (!this.props.request_params.optType) {
                // Get groups of root nodes based on current order
                let root_ix = [0]
                for (let i = 0; i < order.length - 1; i++) {
                    if (order[i][1] == "b") {
                        if (order[i].slice(0, 2) !== order[i + 1].slice(0, 2)) {
                            root_ix.push(i)
                            root_ix.push(i + 1)
                        }
                    } else {
                        if (order[i][0] !== order[i + 1][0]) {
                            root_ix.push(i)
                            root_ix.push(i + 1)
                        }
                    }
                }
                root_ix.push(order.length - 1)
                // Split into pair chunks
                let root_ix_pairs = []
                for (let i = 0; i < root_ix.length; i += 2) {
                    root_ix_pairs.push([root_ix[i], root_ix[i + 1]])
                }

                const arcGen = d3.arc()
                    .innerRadius(r + r / 80)
                    .outerRadius(r + r / 10)
                    .startAngle(d => sc_radial(order[d[0]]) - 0.03)
                    .endAngle(d => sc_radial(order[d[1]]) + 0.03)


                const root_arcs = svg.selectAll("path")
                    .data(root_ix_pairs)
                    .enter()
                    .append("path")
                    .attr("d", d => arcGen(d))
                    .attr("transform", "translate(" + centre.y + "," + centre.x + ")")
                    .attr("fill", "#ebebeb")

            }

            // Create objects containing node labels and coordinates from list of edges (sets)
            const node_points = order.map(x => ({ "label": x, "coords": node2point(x) }))

            // Calculate inner heirarchy bundling nodes
            let i_nodes = {}
            // For each root note get angle of sub nodes
            for (let i = 0; i < order.length; i++) {
                if (order[i][1] != "b") {
                    if (order[i][0] in i_nodes) {
                        i_nodes[order[i][0]].push(sc_radial(order[i]))
                    }
                    else {
                        i_nodes[order[i][0]] = [sc_radial(order[i])]
                    }
                }
                else {
                    if (order.slice(0, 2) in i_nodes) {
                        i_nodes[order[i].slice(0, 2)].push(sc_radial(order[i]))
                    }
                    else {
                        i_nodes[order[i].slice(0, 2)] = [sc_radial(order[i])]
                    }
                }
            }

            // Calculate mean angle for each root note
            let root_nodes = {}
            for (const [key, value] of Object.entries(i_nodes)) {
                const mean_angle = Math.atan2(d3.sum(value.map(Math.sin)) / value.length, d3.sum(value.map(Math.cos)) / value.length)
                root_nodes[key] = { x: r * Math.sin(mean_angle), y: r * Math.cos(mean_angle) }
            }

            // Append node groups
            const nodes_group = svg.selectAll("g")
                .data(node_points)
                .enter()
                .append("g")
                .attr("transform", (d) => {
                    var x = centre.x + d.coords.x
                    var y = centre.y - d.coords.y
                    return "translate(" + x + "," + y + ")"
                })

            // Append node circles to node groups
            const nodes = nodes_group.append("circle")
                .attr("class", "node")
                .attr("r", 5)

            // Text offset
            const labelOffset = 0.06

            // Append text to labels
            const labels = nodes_group.append("text")
                .text((d) => d.label)
                .attr("fill", d => this.props.queryParams['chordSel'].includes(d.label) ? "red" : "black")
                .attr("dx", (d) => d.coords.x * labelOffset)
                .attr("dy", (d) => -d.coords.y * labelOffset)
                .attr("text-anchor", "middle")
                .attr("font-size", height/60)
                .attr("font-weight", d => this.props.queryParams['chordSel'].includes(d.label) ? 700 : 400)


            const beta = this.props.request_params.beta
            const lineGen = d3.line().x(d => d.x + centre.x).y(d => centre.y - d.y).curve(d3.curveBundle.beta(beta))

            let path_factor = 1.4

            const links = svg.selectAll("path").select(".link")
                .data(sets)
                .enter()
                .append("path")
                .attr("class", "link")
                .attr("d", (d) => lineGen([node2point(d.labels[0]),
                {
                    x: root_nodes[d.labels[0][1] === "b" ? d.labels[0].slice(0, 2) : d.labels[0][0]].x / path_factor,
                    y: root_nodes[d.labels[0][1] === "b" ? d.labels[0].slice(0, 2) : d.labels[0][0]].y / path_factor
                },
                {
                    x: root_nodes[d.labels[1][1] === "b" ? d.labels[1].slice(0, 2) : d.labels[1][0]].x / path_factor,
                    y: root_nodes[d.labels[1][1] === "b" ? d.labels[1].slice(0, 2) : d.labels[1][0]].y / path_factor
                },
                node2point(d.labels[1])]))
                .attr("stroke", d => scColor(d.values))
                .attr("fill", "none")
                .attr("stroke-width", d => d.values ** 1.5 * 50)
                .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** this.props.request_params.focus)

            nodes_group.on("mouseenter", (sel) => {
                d3.selectAll(".link")
                    .filter(d => d.labels.includes(sel.label))
                    .raise()
                    .transition(0.1)
                    .attr("stroke", "red")
                    .attr("stroke-width", 3)
                    .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** 1)
                nodes_group.raise()
            })

            nodes_group.on("mouseleave", (sel) => {
                d3.selectAll(".link")
                    .filter(d => d.labels.includes(sel.label))
                    .transition(0.1)
                    .attr("stroke", d => scColor(d.values))
                    .attr("stroke-width", d => d.values ** 1.5 * 50)
                    .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** this.props.request_params.focus)
                nodes_group.raise()
            })

            nodes_group.on("click", (sel) => {
                let currentQState = this.props.queryParams['chordSel']
                if (currentQState.includes(sel.label)) {
                    currentQState.splice(currentQState.indexOf(sel.label), 1)
                }
                else {
                    currentQState.push(sel.label)
                }
                this.props.setQueryParams({ "chordSel": currentQState })

            })

            nodes_group.raise()
            this.setState({ sets: sets })
        }
    }

    updateFocus() {
        const svg = d3.select("svg")

        svg.selectAll(".link")
            .attr("stroke-opacity", d => (d.values / d3.max(this.state.sets.map(x => x.values))) ** this.props.request_params.focus)
    }


    render() {
        let svg_list = <svg ref={'allchartsvg'} width={this.props.width} height={this.props.height} style={{margin: "auto" }}></svg>

        if (this.state.request_params && this.state.request_params.tag_val.length > 0) {
            if(this.state.request_params.tag_val.length>1){
            svg_list = this.state.request_params.tag_val.map((x, i) => {
                return (
                    <svg key={i} ref={x + 'chartsvg'} width={this.props.width / 1.5} height={this.props.height / 1.5} style={{margin: "auto" ,gridColumn:(i%2)+1,gridRow:Math.floor(i/2)+1}}></svg>
                )
            })
        }
        else {
            svg_list = this.state.request_params.tag_val.map((x, i) => {
                return (
                    <svg key={i} ref={x + 'chartsvg'} width={this.props.width} height={this.props.height} style={{margin: "auto"}}></svg>
                )
            })   
        }
        }
        return (
            <div style={{display:"grid",gridTemplateColumns: `50% 50%`}}>
                {svg_list}
            </div>
        )
    }

}