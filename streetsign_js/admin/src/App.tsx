import React from 'react';
import { BrowserRouter as Router, Route, NavLink } from 'react-router-dom';

import './App.css';

import Home from './routes/Home';
import Posts from './routes/Posts';
import Feeds from './routes/Feeds';
import Screens from './routes/Screens';
import Layouts from './routes/Layouts';
import LayoutEditor from './routes/Layout_editor';
import Users from './routes/Users';

//////////////////////////

/////////////////////////

export interface Props {
    name: string;
};

class App extends React.Component<Props, object> {
    render() {
        const { name } = this.props;

        return (
            <div id="everything">
            <div className="ui inverted vertical masthead center aligned segment">
                <div className="ui container">
                    <div className="ui large secondary inverted pointing menu">
                        <a className="toc item" href="#sidebar">
                            <i className="sidebar icon"></i>
                        </a>
                        <NavLink to="/" exact className="item">Home</NavLink>
                        <NavLink to="/posts" className="item">Posts</NavLink>
                        <NavLink to="/feeds" className="item">Feeds</NavLink>
                        <NavLink to="/screens" className="item">Screens</NavLink>
                        <NavLink to="/layouts" className="item">Layouts</NavLink>
                        <NavLink to="/users" className="item">Users</NavLink>
                        <NavLink to="/users" className="item right">{ name }</NavLink>
                    </div>
                </div>
            </div>
            <Route exact path="/" component={Home} />
            <Route exact path="/posts" component={Posts} />
            <Route exact path="/feeds" component={Feeds} />
            <Route exact path="/screens" component={Screens} />
            <Route exact path="/layouts" component={Layouts} />
            <Route exact path="/users" component={Users} />

            <Route exact path="/layouts/:id" component={LayoutEditor} />
            </div>
        );
    }
}

function AppRouter() {
    return (
        <Router>
            <App name="Dan" />
        </Router>
    );
};

export default AppRouter;
