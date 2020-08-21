import React from "react";
import { Table, Spinner, Popover, OverlayTrigger, Button } from 'react-bootstrap';

export class QueryTable extends React.Component {
    constructor(props) {
        super(props)
        this.state = { tableData: null, loading: true }
    }

    componentDidMount() {
        this.fetchData()
    }

    componentDidUpdate(prevProps) {
        if (prevProps.queryParams !== this.props.queryParams || (String(prevProps.requestParams.tag_val) !== String(this.props.requestParams.tag_val))) {
            this.fetchData()
        }
    }

    fetchData() {
        this.setState({ tableData: null, loading: true })
        let url = "http://127.0.0.1:5000/queryData?"
        if ('chordSel' in this.props.queryParams) {
            if (this.props.queryParams.chordSel.length > 0) {
                url = url + "&chordSel=" + this.props.queryParams.chordSel.join(",")
            }
        }
        if (this.props.requestParams.tag_name == 'genres' && this.props.requestParams.tag_val.length > 0) {
            url = url + "&genre=" + this.props.requestParams.tag_val.join(",")
        }
        fetch(url).then(r => r.json()).then(r => this.setState({ tableData: r, loading: false }))
    }

    render() {

        let tableRows = ""

        const spinner = (
            <div style={{ textAlign: "center", width: "100%" }}>
                <Spinner animation="border" role="status">
                    <span className="sr-only">Loading...</span>
                </Spinner>
            </div>
        )


        if (this.state.tableData) {
            tableRows = this.state.tableData.map((x, i) => {
                const popover = (
                    <Popover id="popover-basic">
                        <Popover.Title as="h3">Chords</Popover.Title>
                        <Popover.Content>
                            {x['chords'].join(", ")}
                        </Popover.Content>
                    </Popover>
                )
                return (
                    <tr key={i}>
                        <td>{x['name']}</td>
                        <td>{x['artist_name']}</td>
                        <td>{<OverlayTrigger trigger="click" placement="right" overlay={popover} rootClose>
                            <Button variant="success">Chords</Button>
                            </OverlayTrigger>}</td>
                        <td>{x.musicinfo.tags.genres.join(", ")}</td>
                        <td>
                            <audio controls style={{ "height": 30 }}>
                                <source src={x['audio']} type="audio/mpeg" />
                            </audio>
                        </td>
                    </tr>
                )
            })
        }

        if (!this.state.tableData && !this.state.loading) {
            tableRows = "No Results"
        }


        return (
            <div style={{ width: "100%", padding: "40px" }}>
                <Table bordered size='sm'>
                    <thead>
                        <tr>
                            <th>{"Track Name"}</th>
                            <th>{"Artist"}</th>
                            <th>{"Chords"}</th>
                            <th>{"Genre Tags"}</th>
                            <th>{"Audio"}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tableRows}
                    </tbody>
                </Table>
                {this.state.loading ? spinner : null}
                {this.state.tableData ? (this.state.tableData.length == 0 ? <div style={{ "textAlign": "center", "width": "100%" }}>No Results</div> : null) : null}
            </div>
        )
    }

}