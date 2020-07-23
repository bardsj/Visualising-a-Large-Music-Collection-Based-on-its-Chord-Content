import React from 'react';
import { Navbar, Form, Popover, OverlayTrigger, Button } from 'react-bootstrap';

export class Options extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {

        const genres = ['pop','rock','electronic','hiphop','jazz','indie','filmscore','classical','chillout','ambient','folk','metal','latin','rnb','reggae','punk','country','house','blues']

        const popover = (
            <Popover id="popover-basic">
                <Popover.Title as="h3">Filter Options</Popover.Title>
                <Popover.Content>
                <Form>
                            <Form.Control defaultValue={this.props.chartType} as="select" onChange={(e) => this.props.handleChartType(e.target.value)}>
                                <option>Circular</option>
                                <option>Parallel</option>
                            </Form.Control>
                            <Form.Label>Genre</Form.Label>
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
                            <Form.Label style={{ paddingRight: 5, color: "white" }}>Chart Type</Form.Label>
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