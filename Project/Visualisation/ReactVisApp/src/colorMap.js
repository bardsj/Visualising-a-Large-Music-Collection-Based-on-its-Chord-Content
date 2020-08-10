import * as d3 from 'd3';

export function genreColormap() {

    const genres = ['pop','rock','electronic','hiphop','jazz','indie','filmscore','classical','chillout','ambient','folk','metal','latin','rnb','reggae','punk','country','house','blues']
    // Colour map
    const scale = d3.scalePoint().domain(genres).range([0, 1])
    let colorMap = { null: "rgb(0, 0, 0)" }

    for (let i = 0; i < genres.length; i++) {
        colorMap[genres[i]] = d3.interpolateTurbo(scale(genres[i]))
    }
    return colorMap
}

export function nodeColormap() {
    const root_nodes = ["C","Db","D","Eb","E","F","Gb","G","Ab","A","Bb","B"]
    const scale = d3.scalePoint().domain(root_nodes).range([0, 11])
    let colorMap = {}

    for (let i = 0; i < root_nodes.length; i++) {
        colorMap[root_nodes[i]] = d3.schemeSet3[scale(root_nodes[i])]
    }
    return colorMap
}