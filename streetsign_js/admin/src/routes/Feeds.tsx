import * as React from 'react';

import * as Immutable from 'immutable';

export enum Actions {
    addFeed,
    delFeed,
}

export interface FeedItemProps {
    id: number,
    name: string,
    published: boolean,
};

function FeedListItem ({id, name, published}: FeedItemProps) {
    return (
        <tr>
            <td data-label="id">{ id }</td>
            <td data-label="name">{ name }</td>
            <td data-label="published">{ published ? "Published" : "-" }</td>
        </tr>
    );
}

type FeedsProps = {};
type FeedsState = { feeds: Immutable.List<FeedItemProps> };

class Feeds extends React.Component<FeedsProps, FeedsState> {
    constructor(props: any) {
        super(props);
        this.state = {
            feeds: Immutable.List(),
        };
    }

    addClick() {
        return (evt:any) => {
            this.setState((state, props) => ({
                feeds: state.feeds.push({id: 42, name: 'First Feed', published: true})
            }));
        }
    }

    async getFromServer() {
        const response = await fetch('/feeds.json');
        const json = await response.json() as {feeds:FeedItemProps[]};
        this.setState({feeds: Immutable.List(json.feeds)});
    }



    componentDidMount() {
        this.getFromServer();
    }
    render() {
        return( <div>
            <h1>All Feeds: {this.state.feeds.count()}</h1>
            <button className="ui button primary" onClick={this.addClick()}>+</button>
            <table className="ui celled table">
                <thead><tr>
                <th>ID</th><th>Name</th><th>Published</th>
                </tr></thead>
                <tbody>
                {this.state.feeds.map((feeds: any, index: number) => (
                    <FeedListItem key={index} {...feeds} />
                ))}
                </tbody>
            </table>
        </div>)
    }
}

export default Feeds;
