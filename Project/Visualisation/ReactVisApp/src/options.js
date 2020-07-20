import React from 'react';
import { Navbar, Form, InputGroup, FormControl, FormGroup } from 'react-bootstrap';

export class Options extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {

        const genres = ['jazz', 'electronic', 'chillout', 'ambient', 'pop', 'rock', 'dance', 'hiphop', "all"]

        return (
            <Navbar bg='light'>
                <Navbar.Brand>Visualising a Large Music Collection Based on it's Chord Content</Navbar.Brand>
                <Form inline >
                    <Form.Label>Genre</Form.Label>
                    <Form.Control as="select" onChange={(e) => this.props.handleFilter(e.target.value)}>
                        {
                            genres.map((genres, index) => {
                                return (<option key={index} value={genres}>{genres}</option>)
                            })
                        }
                    </Form.Control>
                </Form>
            </Navbar>
        )
    }
}