import React from "react";
import * as d3 from 'd3';
import { genreColormap } from './colorMap'

export class ChartParallel extends React.Component {
    constructor(props) {
        super(props)
        this.state = { data: null, request_params: null }
    }

    fetchData(request_params, majMinSel) {
        let r_url = ""
        if (request_params.tag_val.length > 0) {
            r_url = "http://127.0.0.1:5000/parallel?tag_val=" + request_params.tag_val.join() + "&tag_name=" + request_params.tag_name
        }
        else {
            r_url = "http://127.0.0.1:5000/parallel?"
        }
        if (request_params.optType) {
            r_url = r_url + "&order_opt=" + request_params.optType
        }
        if (request_params.majMinSel) {
            r_url = r_url + "&majmin_agg=" + request_params.majMinSel
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
            let node_list = this.state.data.order
            let data = this.state.data.sets
            if (this.state.request_params.tag_val.length > 0) {
                data = data.filter(x => x.tag == genres_tmp[tag_ix])
            }
            data = data.filter(x => x.values > this.props.request_params.support / 100)
            if (this.props.queryParams['chordSel'].length > 0) {
                data = data.filter(x => x.labels.some(r => this.props.queryParams['chordSel'].includes(r)))
            }
            const margin = ({ top: 20, bottom: 20, left: 60, right: 10 })

            // Number of parallel axes from max itemset length
            const n_ax = d3.max(data.map(x => x.labels.length))

            // Filter out nodes from order that all not in filtered sets
            //const filtered_set = new Array(... new Set(data.flatMap(x => x['labels'])))
            //node_list = node_list.filter(x => filtered_set.includes(x))

            // Colour map
            const cmap = genreColormap(this.state.request_params.tag_val)


            // Add axes field to data by taking index of node in data node lists
            const data_ax = data.map(d => ({ labels: d.labels.map((l, i) => ({ node: l, ax: i })), values: d.values, tag: d.tag, km_label: d.km_label }))

            let scY = []
            // Add axis field for n axes from node list
            let node_list_ax = []

            // Categorical y scale
            for (let i = 0; i < n_ax; i++) {
                //const ax_nodes = new Array(... new Set(data_ax.filter(x => x.labels[i]).map(x => x.labels[i].node)))
                //scY.push(d3.scalePoint().domain(node_list.filter(x=>ax_nodes.includes(x))).range([margin.top, height - margin.bottom]))
                const ax_nodes = node_list
                scY.push(d3.scalePoint().domain(node_list).range([margin.top, height - margin.bottom]))
                node_list_ax.push(...ax_nodes.map(x => ({ ax: i, node: x })))
            }
            // Linear x scale for parallel axes
            const scX = d3.scaleLinear().domain([0, n_ax - 1]).range([margin.left, width - margin.right])

            // Add node groups to create parallel axes
            const nodes_group = svg.selectAll("g")
                .data(node_list_ax)
                .enter()
                .append("g")
                .attr("transform", (d) => "translate(" + scX(d.ax) + "," + scY[d.ax](d.node) + ")")
            // Append circle to node groups
            const nodes = nodes_group.append("circle")
                .attr("r", 2)
            // Append labels to node groups
            const labels = nodes_group.append("text")
                .text(d => d.node)
                .attr("class", "label")
                .attr("font-size", height/60)
                .attr("dx", -4)
                .attr("dy", 2)
                .attr("text-anchor", "end")
                .attr("fill", d => this.props.queryParams['chordSel'].includes(d.node) ? "red" : "black")
                .attr("font-weight", d => this.props.queryParams['chordSel'].includes(d.node) ? 700 : 400)

            // Add transparent rectangle to labels for easier hover selection
            const label_bg = nodes_group.append("rect")
                .attr("width", 30)
                .attr("height", 20)
                .attr("fill", "transparent")
                .attr("transform", "translate(-34,-6)")

            // Path generator
            const lineGen = d3.line().y(d => d.y).x(d => d.x)

            const create_points = (d, i) => {
                let line = [{ "x": scX(d.labels[i].ax), "y": scY[d.labels[i].ax](d.labels[i].node) },
                { "x": scX(d.labels[i + 1].ax), "y": scY[d.labels[i + 1].ax](d.labels[i + 1].node) }
                ]
                return line
            }

            const node_cmap_sc = d3.scalePoint().range([0, 1]).domain(node_list)
            // Append lines for each axes seperately to allow each to be coloured based on start node
            let data_filt = []
            for (let i = 0; i < n_ax; i++) {
                data_filt.push(...data_ax.filter(x => x.labels.length > i + 1).map(d => Object.assign(d, { ax: i })))
            }
            // Append paths
            let links = svg.selectAll("path").select(".link")
                .data(data_filt)
                .enter()
                .append("path")
                .attr("class", "link")
                .attr("d", d => lineGen(create_points(d, d.ax)))
                .attr("fill", "none")
                .attr("stroke", d => this.props.request_params.cPath ? d3.interpolateTurbo(node_cmap_sc(d.labels[d.ax].node)) : cmap[d.tag])
                .attr("fill", "none")
                .attr("stroke-width", d => d.values ** 1.5 * 50)
                .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** this.props.request_params.focus)



            // Highlight paths when hovering on node
            label_bg.on("mouseenter", (sel) => {

                d3.selectAll(".label")
                    .filter(l => l == sel)
                    .transition(0.1)
                    .attr("font-size", height/45)


                d3.selectAll(".link")
                    //.filter(d=>d.labels.includes(sel.label))
                    .filter(d => d.labels[sel.ax] ? d.labels[sel.ax].node === sel.node : null)
                    .transition(0.1)
                    .attr("stroke", "red")
                    .attr("stroke-width", 3)
                    .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** 1)
            })

            label_bg.on("mouseleave", (sel) => {

                d3.selectAll(".label")
                    .filter(l => l == sel)
                    .transition(0.1)
                    .attr("font-size", height/60)

                d3.selectAll(".link")
                    .filter(d => d.labels[sel.ax] ? d.labels[sel.ax].node === sel.node : null)
                    .transition(0.1)
                    .attr("stroke", d => this.props.request_params.cPath ? d3.interpolateTurbo(node_cmap_sc(d.labels[d.ax].node)) : cmap[d.tag])
                    .attr("stroke-width", d => d.values ** 1.5 * 50)
                    .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** this.props.request_params.focus)
            })

            label_bg.on("click", (sel) => {
                let currentQState = this.props.queryParams['chordSel']
                if (currentQState.includes(sel.node)) {
                    currentQState.splice(currentQState.indexOf(sel.node), 1)
                }
                else {
                    currentQState.push(sel.node)
                }
                this.props.setQueryParams({ "chordSel": currentQState })

            })

            // Raise label groups above paths
            nodes_group.raise()
            label_bg.raise()

            this.setState({ sets: data })


            // Raise label groups above paths
            nodes_group.raise()
            label_bg.raise()

            this.setState({ sets: data })
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