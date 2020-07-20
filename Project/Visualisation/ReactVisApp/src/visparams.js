import React, { useState } from "react"

export function VisParams(props) {
    const [focus, setFocus] = useState(1)
    const [support, setSupport] = useState(0)

    return (
        <div style={{display: "grid", gridTemplateColumns: "80px 150px 50px"}}>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:1, gridColumn:1}}>Focus</p>
                <input style={{ float: "left", marginTop: -25, gridRow:1, gridColumn:2}} type="range" min="0.1" max="4" step="0.05" defaultValue="1" id="focus" onChange={(e)=> setFocus(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:1, gridColumn:3}}>{focus}</p>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:2, gridColumn:1}}>Support</p>
                <input style={{ float: "left", marginTop: -25, gridRow:2, gridColumn:2}} type="range" min="1" max="50" defaultValue="1" id="focus" onChange={(e)=> setSupport(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:2, gridColumn:3}}>{support}</p>
        </div>
    )
}