import * as d3 from 'd3';

export function genreColormap() {

    const genres = ['pop','rock','electronic','hiphop','jazz','indie','filmscore','classical','chillout','ambient','folk','metal','latin','rnb','reggae','punk','country','house','blues']
    // Colour map
    const scale = d3.scalePoint().domain(genres.slice(0, -1)).range([0, 1])
    let colorMap = { null: "rgb(0, 0, 0)" }

    for (let i = 0; i < genres.length - 1; i++) {
        colorMap[genres[i]] = d3.interpolateTurbo(scale(genres[i]))
    }
    return colorMap
}