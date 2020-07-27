import React from "react";
import * as d3 from 'd3';
import { genreColormap } from './colorMap'

export class Legend extends React.Component {
    constructor(props) {
        super(props)
        this.createLegend = this.createLegend.bind(this)
    }

    componentDidMount() {
        this.createLegend()
    }

    componentDidUpdate() {
        this.createLegend()
    }

    createLegend() {
        const svg = d3.select(this.refs["legend"])
        svg.selectAll("*").remove()

        // If single hue chart selected create gradient colour legend else create categorical legend
        if (!this.props.chartType.includes("Single Hue")) {
            svg.attr("height", "100%")
            const labels = svg.selectAll("g")
                .data(this.props.requestParams.tag_val)
                .enter()
                .append("g")
                .attr("transform", (d, i) => {
                    return "translate(20," + String((i * 40) + 20) + ")"
                })

            const cmap = genreColormap()

            labels.append("rect")
                .attr("fill", d => cmap[d])
                .attr("width", 20)
                .attr("height", 20)

            labels.append("text")
                .text(d => d)
                .attr("dx", 25)
                .attr("dy", 15)
                .attr("font-size", 15)

        }
    }

    render() {
        return (<svg ref={"legend"} height="100%"></svg>)
    }
}