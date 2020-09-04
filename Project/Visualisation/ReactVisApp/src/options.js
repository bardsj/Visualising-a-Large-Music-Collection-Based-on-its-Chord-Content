import React from 'react';
import { Navbar, Form, Popover, OverlayTrigger, Button, Dropdown } from 'react-bootstrap';

export class Options extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {

        //const genres = ['pop','rock','electronic','hiphop','jazz','indie','filmscore','classical','chillout','ambient','folk','metal','latin','rnb','reggae','punk','country','house','blues']
        const genres = ['pop', 'rock', 'electronic', 'hiphop', 'jazz', 'classical', 'ambient', 'folk', 'metal', 'latin', 'rnb', 'reggae', 'house', 'blues']

        const popover = (
            <Popover id="popover-basic">
                <Popover.Title as="h3">Filter Options</Popover.Title>
                <Popover.Content>
                    <Form>
                        <Form.Label style={{ paddingRight: 5, fontWeight: 700 }}>Chart Type</Form.Label>
                        <Form.Control defaultValue={this.props.requestParams.chartType} as="select" onChange={(e) => this.props.setRequestParams({ ...this.props.requestParams, chartType: e.target.value })}>
                            <option>Circular</option>
                            <option>Parallel</option>
                            <option>Circular Hierarchical</option>
                            <option>Circular Hierarchical - Single Hue</option>
                            <option>Circular Clustered</option>
                            <option>Parallel Clustered</option>
                        </Form.Control>
                        <Form.Label style={{ paddingTop: 10, fontWeight: 700 }}>Genre</Form.Label>
                        <Form.Group>
                            {
                                genres.map((genre, index) => {
                                    return (<Form.Check onChange={(e) => this.props.handleFilter(e)}
                                        type="checkbox" key={index} value={genre} label={genre}
                                        defaultChecked={this.props.requestParams.tag_val.includes(genre) ? true : false}
                                    />)
                                })
                            }
                        </Form.Group>
                        <Form.Label style={{ paddingRight: 5, fontWeight: 700 }}>Data Type</Form.Label>
                        <Form.Control defaultValue={this.props.requestParams.chartType} as="select" onChange={(e) => this.props.setRequestParams({ ...this.props.requestParams, fi_type: e.target.value == "Frequent Itemsets" ? "frequent" : "hui" })}>
                            <option>Frequent Itemsets</option>
                            <option>High Utility Itemsets</option>
                        </Form.Control>
                    </Form>
                </Popover.Content>
            </Popover>
        );

        return (
            <Navbar bg='dark' variant='dark'>
                <Navbar.Brand style={{ paddingRight: 10 }}>Visualising a Large Music Collection Based on it's Chord Content</Navbar.Brand>
                <OverlayTrigger trigger="click" rootClose placement="right" overlay={popover}>
                    <Button variant="secondary">Options</Button>
                </OverlayTrigger>
            </Navbar>
        )
    }
}