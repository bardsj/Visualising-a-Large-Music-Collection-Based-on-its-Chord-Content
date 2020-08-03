import React from "react";
import * as d3 from 'd3';
import { genreColormap } from './colorMap'
import { set, path, mean } from "d3";
import { Popover } from "react-bootstrap";

export class ChartKMeans extends React.Component {
    constructor(props) {
        super(props)
        this.state = { data: null, request_params: null }
    }

    fetchData(request_params) {
        let r_url = ""
        if (request_params.tag_val.length > 0) {
            r_url = "http://127.0.0.1:5000/circKMeans?tag_val=" + request_params.tag_val.join() + "&tag_name=" + request_params.tag_name
        }
        else {
            r_url = "http://127.0.0.1:5000/circKMeans"
        }
        fetch(r_url, { mode: 'cors' })
            .then(r => r.json())
            .then(r => this.setState({ data: r, request_params: request_params }))

    }

    componentDidMount() {
        this.fetchData(this.props.request_params);
    }

    componentDidUpdate() {
        if (this.state.request_params !== this.props.request_params) {
            this.fetchData(this.props.request_params)
        }
        if (this.state.data) {
            this.createChart()
        }

    }

    createChart() {
        const svg = d3.select(this.refs[this.props.id + 'chartsvg'])
        svg.selectAll("*").remove()
        const width = this.props.width
        const height = this.props.height
        let order = this.state.data.order
        let sets = this.state.data.sets
        // Filter based on slider support val
        sets = sets.filter(x => x.values > this.props.support / 100)
        const r = (this.props.height / 2) - 50;

        // Filter out nodes from order that all not in filtered sets
        const filtered_set = new Array(... new Set(sets.flatMap(x => x['labels'])))
        order = order.filter(x => filtered_set.includes(x))

        // Calculate radial coordinate from ordered list of nodes
        const sc_radial = d3.scalePoint().domain(order).range([0, Math.PI * 2 - (Math.PI * 2 / order.length)])

        // Colour map
        const cmap = genreColormap()

        // Convert radial coordinate to cartesian
        const node2point = (d) => {
            return { x: r * Math.sin(sc_radial(d)), y: r * Math.cos(sc_radial(d)) }
        }

        // Centre of the circle
        const centre = { x: width / 2, y: width / 2 }

        // Create objects containing node labels and coordinates from list of edges (sets)
        const node_points = order.map(x => ({ "label": x, "coords": node2point(x) }))

        // Calculate inner heirarchy bundling nodes
        // Get cluster number values
        const n_clusters = new Array(... new Set(sets.map(x => x['km_label'])))
        // Inner node map
        let i_nodes = {}
        // Get labels and cluster value for each edge (set)
        const angle_map = sets.map(x => [x.labels, x.km_label])

        /////////////////////////// Calculate control points //////////////////////////

        for (let i = 0; i < angle_map.length; i++) {
            if (angle_map[i][1] in i_nodes) {
                // Push lhs and rhs node positions
                i_nodes[angle_map[i][1]][0].push(node2point(angle_map[i][0][0]))
                i_nodes[angle_map[i][1]][1].push(node2point(angle_map[i][0][1]))
            }
            else {
                i_nodes[angle_map[i][1]] = [[node2point(angle_map[i][0][0])], [node2point(angle_map[i][0][1])]]
            }
        }

        let root_nodes = {}
        for (const [key, value] of Object.entries(i_nodes)) {
            // If there is more than one node in array
            if (value[0].length > 1) {
                // Get lhs nodes
                const points_ln = value[0]
                // Calculate mean position of lhs nodes
                const mean_ln = { "x": d3.mean(points_ln.map(x => x.x)), "y": d3.mean(points_ln.map(x => x.y)) }
                // Do the same for rhs nodes
                const points_rn = value[1]
                const mean_rn = { "x": d3.mean(points_rn.map(x => x.x)), "y": d3.mean(points_rn.map(x => x.y)) }
                root_nodes[key] = { "ln": mean_ln, "rn": mean_rn }
            } else {
                root_nodes[key] = { "ln": value[0][0], "rn": value[1][0] }
            }
        }

        /////////////////////// Optimise control point positions ///////////////////////////

        // Calculate the total line length for a particular cluster group
        function calc_line_length(key, i_nodes, root_nodes, side) {
            const centroid = root_nodes[key]
            let total_line_length = 0
            // Calculate length between lhs and rhs centroids
            const mid_length = Math.sqrt((centroid.ln.x - centroid.rn.x) ** 2 + (centroid.ln.y - centroid.rn.y) ** 2)

            if (i_nodes[key][0].length > 1) {
                // Sum total line lengths
                //total_line_length = lengths_ln + lengths_rn + mid_length
                if (side == "ln") {
                    // Calculate total length between lhs nodes and centroid
                    const lengths_ln = d3.sum(i_nodes[key][0].map(x => Math.sqrt((x.x - centroid.ln.x) ** 2 + (x.y - centroid.ln.y) ** 2)))
                    total_line_length = lengths_ln + mid_length
                } else {
                    // Calculate total length between lhs nodes and centroid
                    const lengths_rn = d3.sum(i_nodes[key][1].map(x => Math.sqrt((x.x - centroid.rn.x) ** 2 + (x.y - centroid.rn.y) ** 2)))
                    total_line_length = lengths_rn + mid_length
                }

            } else {
                // Only one line, length is equal to centroid distance (centroids = node points)
                //total_line_length = Math.sqrt((centroid.ln.x - centroid.rn.x) ** 2 + (centroid.ln.y - centroid.rn.y) ** 2)
                total_line_length = mid_length
            }

            return total_line_length
        }

        // Golden section search
        function gss(f, a, b, key, i_nodes, root_nodes, side, tol = 0.0000000000001) {
            const gr = (Math.sqrt(5) + 1) / 2
            let c = b - (b - a) / gr
            let d = a + (b - a) / gr
            while (Math.abs(c - d) > tol) {
                if (f(c, key, i_nodes, root_nodes, side) < f(d, key, i_nodes, root_nodes, side)) {
                    b = d
                } else {
                    a = c
                }
                c = b - (b - a) / gr
                d = a + (b - a) / gr
            }
            return (b + a) / 2
        }

        // Function for gss to optimise (takes ratio of line between centroids to change position by)
        function gss_func(r, key, i_nodes, root_nodes, side) {
            //let new_root_nodes = Object.assign({},root_nodes)
            let new_root_nodes = JSON.parse(JSON.stringify(root_nodes))
            if (side == "ln") {
                new_root_nodes[key].ln = {
                    "x": new_root_nodes[key].ln.x + r * (new_root_nodes[key].rn.x - new_root_nodes[key].ln.x),
                    "y": new_root_nodes[key].ln.y + r * (new_root_nodes[key].rn.y - new_root_nodes[key].ln.y)
                }
            }
            if (side == "rn") {
                new_root_nodes[key].rn = {
                    "x": new_root_nodes[key].rn.x + r * (new_root_nodes[key].ln.x - new_root_nodes[key].rn.x),
                    "y": new_root_nodes[key].rn.y + r * (new_root_nodes[key].ln.y - new_root_nodes[key].rn.y)
                }
            }
            return calc_line_length(key, i_nodes, new_root_nodes, side)
        }

        // Carry out optimisation - set r_l and r_r to constant value if desired
        for (const [key, value] of Object.entries(root_nodes)) {
            // Do for lhs nodes
            const r_l = gss(gss_func, 0, 1, key, i_nodes, root_nodes, "ln")
            //const r_l = 0.1
            root_nodes[key].ln = {
                "x": root_nodes[key].ln.x + r_l * (root_nodes[key].rn.x - root_nodes[key].ln.x),
                "y": root_nodes[key].ln.y + r_l * (root_nodes[key].rn.y - root_nodes[key].ln.y)
            }

            // Do for rhs nodes
            const r_r = gss(gss_func, 0, 1, key, i_nodes, root_nodes, "rn")
            //const r_r = 0.1
            root_nodes[key].rn = {
                "x": root_nodes[key].rn.x + r_r * (root_nodes[key].ln.x - root_nodes[key].rn.x),
                "y": root_nodes[key].rn.y + r_r * (root_nodes[key].ln.y - root_nodes[key].rn.y)
            }
        }

        ////////////////////////////////////////////////////////////////////////////

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
            .attr("fill", "black")
            .attr("dx", (d) => d.coords.x * labelOffset)
            .attr("dy", (d) => -d.coords.y * labelOffset)
            .attr("text-anchor", "middle")
            .attr("font-size", 10)


        const beta = this.props.beta
        const lineGen = d3.line().x(d => d.x + centre.x).y(d => centre.y - d.y).curve(d3.curveBundle.beta(1))

        // Generate coordinates for line based on cluster value mapping to inner node values
        const create_points = (d) => {
            let line = [node2point(d.labels[0]),
            { "x": root_nodes[d.km_label].ln.x, "y": root_nodes[d.km_label].ln.y },
            { "x": root_nodes[d.km_label].rn.x, "y": root_nodes[d.km_label].rn.y },
            node2point(d.labels[1])]
            return line
        }

        const links = svg.selectAll("path")
            .data(sets)
            .enter()
            .append("path")
            .attr("class", "link")
            .attr("d", (d) => lineGen(create_points(d)))
            .attr("stroke", d => cmap[d.tag])
            //.attr("stroke", d => d.km_label == 2 ? "red" : cmap[d.tag])
            .attr("fill", "none")
            .attr("stroke-width", 1)
            .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** this.props.focus)

        nodes_group.on("mouseenter", (sel) => {
            d3.selectAll(".link")
                .filter(d => d.labels.includes(sel.label))
                .raise()
                .transition(0.1)
                .attr("stroke", "red")
                .attr("stroke-width", 3)
                .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** 1)
        })

        nodes_group.on("mouseleave", (sel) => {
            d3.selectAll(".link")
                .filter(d => d.labels.includes(sel.label))
                .transition(0.1)
                .attr("stroke", d => cmap[d.tag])
                .attr("stroke-width", 1)
                .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** this.props.focus)
        })

        /*
        // See control points for reference
        svg.append("circle")
            .attr("cx", centre.x + root_nodes[2].ln.x)
            .attr("cy", centre.y - root_nodes[2].ln.y)
            .attr("r", 10)
            .attr("fill", "red")

        svg.append("circle")
            .attr("cx", centre.x + root_nodes[2].rn.x)
            .attr("cy", centre.y - root_nodes[2].rn.y)
            .attr("r", 10)
            .attr("fill", "red")
        */

    }


    render() {
        return (
            <svg ref={this.props.id + 'chartsvg'} width={this.props.width} height={this.props.height} style={{ display: "block", margin: "auto" }}>

            </svg>
        )
    }

}