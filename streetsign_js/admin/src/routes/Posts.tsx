import * as React from 'react';

import * as Immutable from 'immutable';

export enum Actions {
    addPost,
    delPost,
}

export interface PostItemProps {
    id: number,
    contenttype: string,
    published: boolean,
};

function PostListItem ({id, contenttype, published}: PostItemProps) {
    return (
        <tr>
            <td data-label="id">{ id }</td>
            <td data-label="contenttype">{ contenttype }</td>
            <td data-label="published">{ published ? "Published" : "-" }</td>
        </tr>
    );
}

type PostsProps = {};
type PostsState = { posts: Immutable.List<PostItemProps> };

class Posts extends React.Component<PostsProps, PostsState> {
    constructor(props: any) {
        super(props);
        this.state = {
            posts: Immutable.List(),
        };
    }

    addClick() {
        return (evt:any) => {
            this.setState((state, props) => ({
                posts: state.posts.push({id: 42, contenttype: 'text', published: true})
            }));
        }
    }

    async getFromServer() {
        const response = await fetch('/posts.json');
        const json = await response.json() as {posts:PostItemProps[]};
        this.setState({posts: Immutable.List(json.posts)});
    }



    componentDidMount() {
        this.getFromServer();
    }
    render() {
        return( <div>
            <h1>All Posts: {this.state.posts.count()}</h1>
            <button className="ui button primary" onClick={this.addClick()}>+</button>
            <table className="ui celled table">
                <thead><tr>
                <th>ID</th><th>Type</th><th>Published</th>
                </tr></thead>
                <tbody>
                {this.state.posts.map((post: any, index: number) => (
                    <PostListItem key={index} {...post} />
                ))}
                </tbody>
            </table>
        </div>)
    }
}

export default Posts;
