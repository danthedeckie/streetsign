import * as React from 'react';
import { Link } from 'react-router-dom';

import * as Immutable from 'immutable';

export enum Actions {
    addLayout,
    delLayout,
}

export interface LayoutItemProps {
    id: number,
    slug: string,
    name: string,
};

function LayoutListItem ({id, slug, name}: LayoutItemProps) {
    return (
        <tr>
            <td data-label="id">{ id }</td>
            <td data-label="name"><Link to={"/layouts/" +id}>{ name }</Link></td>
            <td data-label="slug">{ slug }</td>
        </tr>
    );
}

type LayoutsProps = {};
type LayoutsState = { layouts: Immutable.List<LayoutItemProps> };

class Layouts extends React.Component<LayoutsProps, LayoutsState> {
    constructor(props: any) {
        super(props);
        this.state = {
            layouts: Immutable.List(),
        };
    }

    addClick() {
        return (evt:any) => {
            
            this.setState((state, props) => {
            let maybename = prompt("New Layout name?");

            if (maybename === null) {return null};
            const name: string = (maybename as string).trim();

            if (name === '') return;
            let slug = name.replace(/\W/g, '_');

            if (state.layouts.find(l => l.slug === slug)) {
                alert('There\'s already a layout with that name.');
                return;
            }

            return {layouts: state.layouts.push({id: 42, name: name, slug: slug})};
            }
            );
        }
    }

    async getFromServer() {
        const response = await fetch('/layouts.json');
        const json = await response.json() as {layouts:LayoutItemProps[]};
        this.setState({layouts: Immutable.List(json.layouts)});
    }



    componentDidMount() {
        this.getFromServer();
    }
    render() {
        return( <div>
            <h1>All Layouts: {this.state.layouts.count()}</h1>
            <button className="ui button primary" onClick={this.addClick()}>+</button>
            <table className="ui celled table">
                <thead><tr>
                <th>ID</th><th>Name</th><th>URL (Slug)</th>
                </tr></thead>
                <tbody>
                {this.state.layouts.map((layout: any, index: number) => (
                    <LayoutListItem key={index} {...layout} />
                ))}
                </tbody>
            </table>
        </div>)
    }
}

export default Layouts;
