import React from 'react';
import { Navbar, Form, InputGroup, FormControl, FormGroup } from 'react-bootstrap';

export class Options extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {

        const genres = ['jazz', 'electronic', 'chillout', 'ambient', 'pop', 'rock', 'dance', 'hiphop', "all"]

        return (
            <Navbar bg='dark' variant='dark'>
                <Navbar.Brand style={{paddingRight:10}}>Visualising a Large Music Collection Based on it's Chord Content</Navbar.Brand>
                <Form inline>
                    <Form.Label style={{paddingRight:5, color: "white"}}>Genre</Form.Label>
                    <Form.Control style={{marginRight:30}} as="select" onChange={(e) => this.props.handleFilter(e.target.value)}>
                        {
                            genres.map((genres, index) => {
                                return (<option key={index} value={genres}>{genres}</option>)
                            })
                        }
                    </Form.Control>
                    <Form.Label style={{paddingRight:5, color: "white"}}>Chart Type</Form.Label>
                    <Form.Control style={{marginRight:30}} as="select" onChange={(e) => this.props.handleChartType(e.target.value)}>
                        <option>Circular</option>
                        <option>Parallel</option>
                    </Form.Control>
                </Form>
            </Navbar>
        )
    }
}