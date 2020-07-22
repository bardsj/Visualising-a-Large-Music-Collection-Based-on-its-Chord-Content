import * as d3 from 'd3';

export function genreColormap() {

    const genres = ['jazz', 'electronic', 'chillout', 'ambient', 'pop', 'rock', 'dance', 'hiphop', 'all']
    // Colour map
    const scale = d3.scalePoint().domain(genres.slice(0, -1)).range([0, 1])
    let colorMap = { null: "rgb(0, 0, 0)" }

    for (let i = 0; i < genres.length - 1; i++) {
        colorMap[genres[i]] = d3.interpolateTurbo(scale(genres[i]))
    }
    return colorMap
}